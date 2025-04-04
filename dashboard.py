import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.dash_table import DataTable

# Charger les données depuis le fichier CSV
df = pd.read_csv("data-final.csv")

# Nettoyage / traitement des données
df['price'] = pd.to_numeric(df['price'], errors='coerce')  # Assurer que le prix est numérique
df.dropna(subset=['price'], inplace=True)  # Supprimer les lignes où le prix est NaN

# Convertir 'company' en catégorie pour éviter les problèmes de mémoire pour les grandes listes
df['company'] = df['company'].astype('category')

# Créer un graphique à barres pour les annonces par boutique
company_counts = df['company'].value_counts().reset_index()
company_counts.columns = ['company', 'count']

# Créer un graphique pour la répartition des prix
price_hist = px.histogram(df, x='price', nbins=30, title="Répartition des prix")

# Créer un graphique à barres pour le nombre d'annonces par boutique
company_bar = px.bar(
    company_counts,
    x='company',
    y='count',
    labels={'company': 'Boutique', 'count': "Nombre d'annonces"},
    title="Annonces par boutique"
)

# Créer un graphique à secteurs (pie chart) pour la répartition des annonces par boutique
company_pie = px.pie(
    company_counts,
    names='company',
    values='count',
    title="Répartition des Annonces par Boutique"
)

# Créer un graphique en nuage de points pour la distribution des prix
scatter_price = px.scatter(
    df, x='company', y='price',
    title="Prix des Annonces par Boutique",
    labels={'company': 'Boutique', 'price': 'Prix (TND)'},
    hover_data=['company', 'price']
)

# Création de l'application Dash
app = dash.Dash(__name__)
app.title = "Tableau de Bord Annonces"

# Layout du dashboard avec une meilleure structure et design
app.layout = html.Div([
    html.H1("📊 Tableau de Bord des Annonces", style={'textAlign': 'center', 'margin-bottom': '40px'}),

    # Informations principales (Total annonces, Prix moyen, Prix max)
    html.Div([
        html.Div([
            html.H4("Nombre total d’annonces :"),
            html.P(f"{len(df):,}")
        ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px', 'textAlign': 'center'}),

        html.Div([
            html.H4("Prix moyen :"),
            html.P(f"{df['price'].mean():,.0f} TND")
        ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px', 'textAlign': 'center'}),

        html.Div([
            html.H4("Prix max :"),
            html.P(f"{df['price'].max():,.0f} TND")
        ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px', 'textAlign': 'center'}),
    ], style={'display': 'flex', 'justify-content': 'space-around', 'margin-bottom': '40px'}),

    # Histogramme des prix
    dcc.Graph(
        id='histogram-price',
        figure=price_hist,
        style={'margin-bottom': '40px'}
    ),

    # Bar chart : Nombre d'annonces par boutique
    dcc.Graph(
        id='shop-bar',
        figure=company_bar,
        style={'margin-bottom': '40px'}
    ),

    # Pie chart : Répartition des annonces par boutique
    dcc.Graph(
        id='shop-pie',
        figure=company_pie,
        style={'margin-bottom': '40px'}
    ),

    # Scatter plot : Prix des annonces par boutique
    dcc.Graph(
        id='scatter-price',
        figure=scatter_price,
        style={'margin-bottom': '40px'}
    ),

    # Data Table: Affichage des premières lignes du dataframe
    html.H3("Tableau des Annonces", style={'textAlign': 'center'}),
    DataTable(
        id='data-table',
        columns=[{"name": col, "id": col} for col in df.columns],
        data=df.head(10).to_dict('records'),
        style_table={'height': '300px', 'overflowY': 'auto'}
    ),

    # Dropdown pour filtrer les annonces par prix
    # RangeSlider for price filtering
    html.Div([
        html.Label("Filtrer par prix:"),
        dcc.RangeSlider(
            id='price-range-slider',
            min=0,
            max=int(df['price'].max()),
            step=500,
            marks={i: f'{i}' for i in range(0, int(df['price'].max()), 500)},
            value=[0, 5000]  # Default range
        ),
    ], style={'textAlign': 'center', 'width': '80%', 'margin': '20px auto'}),

    # Dropdown pour filtrer les annonces par boutique (company)
    html.Div([
        html.Label("Filtrer par boutique :"),
        dcc.Dropdown(
            id='company-filter',
            options=[{'label': company, 'value': company} for company in df['company'].unique()],
            value=df['company'].unique()[0],  # Default to the first company
            multi=False,
            style={'width': '50%',
                'margin': '20px auto',
                'padding': '10px',
                'borderRadius': '25px'}
        ),
    ], style={'textAlign': 'center'}),

    # Input pour rechercher des annonces par mot-clé (title)
    html.Div([
        html.Label("Rechercher des annonces :", style={'fontSize': '18px', 'fontWeight': 'bold', 'marginBottom': '10px'}),
        dcc.Input(
            id='search-input',
            type='text',
            placeholder='Rechercher...',
            debounce=True,
            style={
                'width': '50%',
                'margin': '20px auto',
                'padding': '10px 15px',
                'borderRadius': '25px',
                'border': '2px solid #B0BEC5',
                'boxShadow': '0px 4px 6px rgba(0, 0, 0, 0.1)',
                'fontSize': '16px',
                'transition': 'all 0.3s ease',
                'outline': 'none'
            }
        ),
    ], style={'textAlign': 'center', 'marginTop': '30px'}),
])

# Callback pour filtrer les données en fonction des filtres
@app.callback(
    dash.dependencies.Output('data-table', 'data'),
    [
        dash.dependencies.Input('price-range-slider', 'value'),
        dash.dependencies.Input('company-filter', 'value'),
        dash.dependencies.Input('search-input', 'value')
    ]
)
def update_table(price_range, company, search_term):
    min_price, max_price = price_range
    filtered_df = df[(df['price'] >= min_price) & (df['price'] <= max_price)]
    
    # Filtrer par boutique
    if company:
        filtered_df = filtered_df[filtered_df['company'] == company]

    # Filtrer par mot-clé dans le titre
    if search_term:
        filtered_df = filtered_df[filtered_df['company_path'].str.contains(search_term, case=False, na=False)]
    
    return filtered_df.head(10).to_dict('records')

# Exécution
if __name__ == '__main__':
    app.run(debug=True)
