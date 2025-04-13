import dash
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output
import requests

# Function to fetch data from API
def fetch_data():
    try:
        response = requests.get("http://localhost:8000/products")
        data = response.json()["products"]
        df_live = pd.DataFrame(data)
        df_live['price'] = pd.to_numeric(df_live['price'], errors='coerce')
        df_live.dropna(subset=['price'], inplace=True)
        df_live['shop'] = df_live['shop'].astype('category')
        return df_live
    except Exception as e:
        print(f"Erreur lors du chargement des données : {e}")
        return pd.DataFrame(columns=['shop', 'price', 'shop_link'])

# Initial data load
df = fetch_data()

# Data cleaning
if not df.empty:
    df['ram'] = df.get('ram', '').str.extract(r'(\d+)').astype(float, errors='ignore')
    df['os'] = df.get('os', '').str.lower()
    df['os'] = df['os'].str.replace(r'windows\s*\d+\s*', 'windows ', regex=True)
    df['os'] = df['os'].str.replace('macos', 'macos')
    df['os'] = df['os'].str.replace('freedos', 'free dos')

    os_mapping = {
        'windows 11': 'Windows 11',
        'windows 11 home': 'Windows 11',
        'windows 11 pro': 'Windows 11',
        'windows 10': 'Windows 10',
        'macos': 'macOS',
        'free dos': 'FreeDOS'
    }

    df['processor_brand'] = df.get('processor_brand', '').str.lower().str.strip()
    processor_mapping = {
        'intel': 'Intel',
        'amd': 'AMD',
        'apple': 'Apple',
        'qualcomm': 'Qualcomm',
        'mediatek': 'Mediatek'
    }

    df['processor_brand'] = df['processor_brand'].replace(processor_mapping, regex=False)
    df['os'] = df['os'].replace(os_mapping, regex=True)

# Function to create graphs
def créer_graphiques(df):
    if df.empty:
        return {key: px.scatter(title="No Data Available") for key in [
            'hist_prix', 'bar_boutiques', 'camembert', 'nuage_prix',
            'bar_os_prix', 'pie_processeurs', 'box_prix_os'
        ]}

    shop_counts = df['shop'].value_counts().reset_index()
    shop_counts.columns = ['Boutique', "Nombre d'annonces"]
    
    os_prices = df.groupby('os')['price'].mean().reset_index().sort_values('price', ascending=False)
    ram_prices = df.groupby('ram')['price'].mean().reset_index()
    storage_counts = df.get('storage', pd.Series([])).value_counts().reset_index()
    storage_counts.columns = ['Stockage', "Nombre d'annonces"]
    processor_counts = df.get('processor_brand', pd.Series([])).value_counts().reset_index()
    processor_counts.columns = ['Marque', "Nombre d'annonces"]
    processor_prices = df.groupby('processor_brand')['price'].mean().reset_index().sort_values('price', ascending=False)

    return {
        'hist_prix': px.histogram(
            df, x='price', nbins=30,
            title="Distribution des prix",
            labels={'price': 'Prix (TND)', 'count': "Nombre d'annonces"},
            template='plotly_white',
            color_discrete_sequence=['#4E79A7']
        ),
        'bar_boutiques': px.bar(
            shop_counts, x='Boutique', y="Nombre d'annonces",
            title="Nombre d'annonces par boutique",
            template='plotly_white',
            color_discrete_sequence=['#F28E2B']
        ),
        'camembert': px.pie(
            shop_counts, names='Boutique', values="Nombre d'annonces",
            title="Répartition par boutique",
            template='plotly_white',
            hole=0.3
        ),
        'nuage_prix': px.scatter(
            df, x='shop', y='price',
            title="Distribution des prix par boutique",
            labels={'shop': 'Boutique', 'price': 'Prix (TND)'},
            template='plotly_white',
            color_discrete_sequence=['#E15759']
        ),
        'bar_os_prix': px.bar(
            os_prices, x='os', y='price',
            title="Prix moyen par système d'exploitation",
            labels={'os': 'Système', 'price': 'Prix moyen (TND)'},
            template='plotly_white',
            color_discrete_sequence=['#76B7B2']
        ),
        'pie_processeurs': px.pie(
            processor_counts, names='Marque', values="Nombre d'annonces",
            title="Répartition des marques de processeurs",
            template='plotly_white',
            hole=0.4
        ),
        'box_prix_os': px.box(
            df, x='os', y='price',
            title="Distribution des prix par système d'exploitation",
            labels={'os': 'Système', 'price': 'Prix (TND)'},
            template='plotly_white',
            color_discrete_sequence=['#FF9DA7']
        )
    }

# Create initial graphs
graphiques = créer_graphiques(df)

# Customize graphs
for fig in graphiques.values():
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial, sans-serif", color='#333333'),
        margin=dict(l=20, r=20, t=60, b=20),
        title_font=dict(size=16, color='#2E3F4F'),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
    )

# Initialize app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])
app.title = "Tableau de Bord des Annonces"

# Color palette
colors = {
    'background': '#f5f7fe',
    'card_background': '#ffffff',
    'text': '#2E3F4F',
    'accent': '#4E79A7',
    'header': '#3a5169',
    'border': '#e1e5eb'
}

# Layout
app.layout = dbc.Container(
    fluid=True,
    style={
        'backgroundColor': colors['background'],
        'padding': '20px',
        'minHeight': '100vh'
    },
    children=[
        # Auto-refresh interval
        dcc.Interval(id="interval-component", interval=10*1000, n_intervals=0),
        
        # Header
        dbc.Row([
            dbc.Col(
                html.H1(
                    "TABLEAU DE BORD DES ANNONCES DES PC PORTABLES EN TUNISIE EN 2025",
                    className="text-center py-4",
                    style={
                        'fontWeight': '600',
                        'fontSize': '1.8rem',
                        'color': colors['header'],
                        'letterSpacing': '1px',
                        'backgroundColor': colors['card_background'],
                        'borderRadius': '8px',
                        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                        'fontFamily': 'Archivo Black, sans-serif'
                    }
                ),
                width=12
            )
        ], className="mb-4"),

        # KPI Cards with restored IDs
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        html.H6("TOTAL ANNONCES", className="card-subtitle", style={'color': colors['text']}),
                        html.H3(id='total-annonces', children=f"{len(df):,}" if not df.empty else "0", 
                                className="card-title mt-2", style={'color': colors['accent']}),
                    ])
                ], style={
                    'backgroundColor': colors['card_background'],
                    'border': f'1px solid {colors["border"]}',
                    'borderRadius': '8px'
                }),
                md=3
            ),
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        html.H6("PRIX MOYEN", className="card-subtitle", style={'color': colors['text']}),
                        html.H3(id='prix-moyen', children=f"{df['price'].mean():,.0f} TND" if not df['price'].empty else "N/A", 
                                className="card-title mt-2", style={'color': colors['accent']}),
                    ])
                ], style={
                    'backgroundColor': colors['card_background'],
                    'border': f'1px solid {colors["border"]}',
                    'borderRadius': '8px'
                }),
                md=3
            ),
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        html.H6("PRIX MAX", className="card-subtitle", style={'color': colors['text']}),
                        html.H3(id='prix-max', children=f"{df['price'].max():,.0f} TND" if not df['price'].empty else "N/A", 
                                className="card-title mt-2", style={'color': colors['accent']}),
                    ])
                ], style={
                    'backgroundColor': colors['card_background'],
                    'border': f'1px solid {colors["border"]}',
                    'borderRadius': '8px'
                }),
                md=3
            ),
            dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        html.H6("BOUTIQUES", className="card-subtitle", style={'color': colors['text']}),
                        html.H3(id='nb-boutiques', children=f"{len(df['shop'].unique()):,}" if not df.empty else "0", 
                                className="card-title mt-2", style={'color': colors['accent']}),
                    ])
                ], style={
                    'backgroundColor': colors['card_background'],
                    'border': f'1px solid {colors["border"]}',
                    'borderRadius': '8px'
                }),
                md=3
            )
        ], className="mb-4 g-3"),

        # Graphs Section
        dbc.Row([
            dbc.Col(
                html.H2(
                    "L'ensemble des graphiques",
                    style={
                        'fontWeight': '600',
                        'fontSize': '1.4rem',
                        'color': colors['header'],
                        'letterSpacing': '1px',
                        'fontFamily': 'Archivo Black, sans-serif',
                        'textAlign': 'start'
                    },
                    className="py-4"
                ),
                width=12
            )
        ]),

        # First row of graphs
        dbc.Row([
            dbc.Col(
                dcc.Graph(
                    id='bar-os-prix',
                    style={
                        'backgroundColor': colors['card_background'],
                        'borderRadius': '8px',
                        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                        'padding': '15px',
                        'height': '100%'
                    }
                ),
                md=6,
                className="mb-4"
            ),
            dbc.Col(
                dcc.Graph(
                    id='pie-processeurs',
                    style={
                        'backgroundColor': colors['card_background'],
                        'borderRadius': '8px',
                        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                        'padding': '15px',
                        'height': '100%'
                    }
                ),
                md=6,
                className="mb-4"
            )
        ], className="g-3"),

        # Box plot
        dbc.Row([
            dbc.Col(
                dcc.Graph(
                    id='box-prix-os',
                    style={
                        'backgroundColor': colors['card_background'],
                        'borderRadius': '8px',
                        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                        'padding': '15px',
                        'height': '100%'
                    }
                ),
                width=12,
                className="mb-4"
            )
        ]),

        # Second row of graphs
        dbc.Row([
            dbc.Col(
                dcc.Graph(
                    id='hist-prix',
                    style={
                        'backgroundColor': colors['card_background'],
                        'borderRadius': '8px',
                        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                        'padding': '15px',
                        'height': '100%'
                    }
                ),
                md=6,
                className="mb-4"
            ),
            dbc.Col(
                dcc.Graph(
                    id='bar-boutiques',
                    style={
                        'backgroundColor': colors['card_background'],
                        'borderRadius': '8px',
                        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                        'padding': '15px',
                        'height': '100%'
                    }
                ),
                md=6,
                className="mb-4"
            )
        ], className="g-3"),

        # Third row of graphs
        dbc.Row([
            dbc.Col(
                dcc.Graph(
                    id='camembert',
                    style={
                        'backgroundColor': colors['card_background'],
                        'borderRadius': '8px',
                        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                        'padding': '15px',
                        'height': '100%'
                    }
                ),
                md=6,
                className="mb-4"
            ),
            dbc.Col(
                dcc.Graph(
                    id='nuage-prix',
                    style={
                        'backgroundColor': colors['card_background'],
                        'borderRadius': '8px',
                        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                        'padding': '15px',
                        'height': '100%'
                    }
                ),
                md=6,
                className="mb-4"
            )
        ], className="g-3"),

        # Filters
        dbc.Row([
            dbc.Col(
                html.H2(
                    "Application des filtres",
                    style={
                        'fontWeight': '600',
                        'fontSize': '1.4rem',
                        'color': colors['header'],
                        'letterSpacing': '1px',
                        'fontFamily': 'Archivo Black, sans-serif',
                        'textAlign': 'start'
                    },
                    className="py-4"
                ),
                width=12
            )
        ]),
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(
                        "FILTRES",
                        className="py-3",
                        style={
                            'backgroundColor': colors['accent'],
                            'color': 'white',
                            'fontWeight': '600',
                            'borderRadius': '8px 8px 0 0'
                        }
                    ),
                    dbc.CardBody([
                        html.Label("Plage de prix (TND):", className="mb-2", style={'color': colors['text']}),
                        dcc.RangeSlider(
                            id='slider-prix',
                            min=0,
                            max=int(df['price'].max()) if not df.empty else 10000,
                            step=500,
                            value=[0, int(df['price'].max()) if not df.empty else 5000],
                            marks={i: f"{i:,}" for i in range(0, int(df['price'].max())+1, 2000)} if not df.empty else {0: "0", 10000: "10000"},
                            tooltip={"placement": "bottom", "always_visible": True},
                            className="mb-4"
                        ),
                        html.Label("Sélection des boutiques:", className="mb-2", style={'color': colors['text']}),
                        dcc.Dropdown(
                            id='dropdown-boutiques',
                            options=[{'label': b, 'value': b} for b in sorted(df['shop'].unique())] if not df.empty else [],
                            multi=True,
                            placeholder="Toutes les boutiques...",
                            className="mb-4",
                            style={
                                'border': f'1px solid {colors["border"]}',
                                'borderRadius': '4px'
                            }
                        ),
                        html.Label("Recherche par mot-clé:", className="mb-2", style={'color': colors['text']}),
                        dbc.Input(
                            id='input-recherche',
                            placeholder="Entrez un mot-clé...",
                            style={
                                'border': f'1px solid {colors["border"]}',
                                'borderRadius': '4px'
                            }
                        )
                    ], style={
                        'backgroundColor': colors['card_background'],
                        'borderRadius': '0 0 8px 8px',
                        'padding': '20px'
                    })
                ], style={
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                    'border': 'none'
                }),
                width=12
            )
        ], className="mb-4"),

        # Data Table
        dbc.Row([
            dbc.Col(
                html.H3(
                    "Résultat du filtrage",
                    style={
                        'fontWeight': '600',
                        'fontSize': '1.2rem',
                        'color': colors['header'],
                        'letterSpacing': '1px',
                        'fontFamily': 'Archivo Black, sans-serif',
                        'textAlign': 'center'
                    },
                    className="py-4"
                ),
                width=12
            )
        ]),
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(
                        "DÉTAIL DES ANNONCES",
                        className="py-3",
                        style={
                            'backgroundColor': colors['accent'],
                            'color': 'white',
                            'fontWeight': '600',
                            'borderRadius': '8px 8px 0 0'
                        }
                    ),
                    dbc.CardBody([
                        dash_table.DataTable(
                            id='table-donnees',
                            columns=[{"name": col, "id": col} for col in df.columns] if not df.empty else [],
                            data=df.to_dict('records') if not df.empty else [],
                            page_size=10,
                            style_table={
                                'overflowX': 'auto',
                                'border': 'none',
                                'borderRadius': '0 0 8px 8px'
                            },
                            style_header={
                                'backgroundColor': colors['accent'] + '20',
                                'fontWeight': '600',
                                'color': colors['text'],
                                'borderBottom': f'1px solid {colors["border"]}'
                            },
                            style_cell={
                                'padding': '12px',
                                'border': 'none',
                                'textAlign': 'left',
                                'color': colors['text']
                            },
                            style_data={
                                'borderBottom': f'1px solid {colors["border"]}'
                            },
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': colors['background']
                                }
                            ],
                            filter_action="native",
                            sort_action="native"
                        )
                    ], style={
                        'backgroundColor': colors['card_background'],
                        'padding': '0',
                        'borderRadius': '0 0 8px 8px'
                    })
                ], style={
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                    'border': 'none'
                }),
                width=12
            )
        ])
    ]
)

# Callback to update dashboard
@app.callback(
    [
        Output('hist-prix', 'figure'),
        Output('bar-boutiques', 'figure'),
        Output('camembert', 'figure'),
        Output('nuage-prix', 'figure'),
        Output('bar-os-prix', 'figure'),
        Output('pie-processeurs', 'figure'),
        Output('box-prix-os', 'figure'),
        Output('table-donnees', 'data'),
        Output('table-donnees', 'columns'),
        Output('dropdown-boutiques', 'options'),
        Output('slider-prix', 'max'),
        Output('slider-prix', 'marks'),
        Output('total-annonces', 'children'),
        Output('prix-moyen', 'children'),
        Output('prix-max', 'children'),
        Output('nb-boutiques', 'children')
    ],
    [
        Input('interval-component', 'n_intervals'),
        Input('slider-prix', 'value'),
        Input('dropdown-boutiques', 'value'),
        Input('input-recherche', 'value')
    ]
)
def update_dashboard(n, plage_prix, boutiques, mot_cle):
    # Fetch fresh data
    df = fetch_data()
    
    if df.empty:
        empty_fig = px.scatter(title="No Data Available")
        return (
            empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig,
            [], [], [], 10000, {0: "0", 10000: "10000"},
            "0", "N/A", "N/A", "0"
        )

    # Apply data cleaning
    df['ram'] = df.get('ram', '').str.extract(r'(\d+)').astype(float, errors='ignore')
    df['os'] = df.get('os', '').str.lower()
    df['os'] = df['os'].str.replace(r'windows\s*\d+\s*', 'windows ', regex=True)
    df['os'] = df['os'].str.replace('macos', 'macos')
    df['os'] = df['os'].str.replace('freedos', 'free dos')

    os_mapping = {
        'windows 11': 'Windows 11',
        'windows 11 home': 'Windows 11',
        'windows 11 pro': 'Windows 11',
        'windows 10': 'Windows 10',
        'macos': 'macOS',
        'free dos': 'FreeDOS'
    }

    df['processor_brand'] = df.get('processor_brand', '').str.lower().str.strip()
    processor_mapping = {
        'intel': 'Intel',
        'amd': 'AMD',
        'apple': 'Apple',
        'qualcomm': 'Qualcomm',
        'mediatek': 'Mediatek'
    }

    df['processor_brand'] = df['processor_brand'].replace(processor_mapping, regex=False)
    df['os'] = df['os'].replace(os_mapping, regex=True)

    # Apply filters
    min_prix, max_prix = plage_prix
    df_filtre = df[(df['price'] >= min_prix) & (df['price'] <= max_prix)]
    
    if boutiques:
        df_filtre = df_filtre[df_filtre['shop'].isin(boutiques)]
    
    if mot_cle:
        df_filtre = df_filtre[df_filtre['shop_link'].str.contains(mot_cle, case=False, na=False)]
    
    # # Debug KPI calculations
    # print(f"Raw DataFrame size: {len(df)}")
    # print(f"Filtered DataFrame size: {len(df_filtre)}")
    # print(f"Price values (filtered): {df_filtre['price'].tolist()}")
    
    # Generate graphs
    graphiques = créer_graphiques(df_filtre)
    
    # Customize graphs
    for fig in graphiques.values():
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Arial, sans-serif", color='#333333'),
            margin=dict(l=20, r=20, t=60, b=20),
            title_font=dict(size=16, color='#2E3F4F'),
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Arial"
            )
        )

    # Update dropdown options
    boutique_options = [{'label': b, 'value': b} for b in sorted(df['shop'].unique())]
    
    # Update slider
    max_price = int(df['price'].max()) if not df['price'].empty else 10000
    marks = {i: f"{i:,}" for i in range(0, max_price+1, 2000)}
    
    # KPI calculations with explicit checks
    total_annonces = f"{len(df_filtre):,}" if not df_filtre.empty else "0"
    prix_moyen = f"{df_filtre['price'].mean():,.0f} TND" if not df_filtre['price'].empty else "N/A"
    prix_max = f"{df_filtre['price'].max():,.0f} TND" if not df_filtre['price'].empty else "N/A"
    nb_boutiques = f"{len(df_filtre['shop'].unique()):,}" if not df_filtre.empty else "0"

    # print(f"KPI - Total Annonces: {total_annonces}")
    # print(f"KPI - Prix Moyen: {prix_moyen}")
    # print(f"KPI - Prix Max: {prix_max}")
    # print(f"KPI - Nombre Boutiques: {nb_boutiques}")

    return (
        graphiques['hist_prix'],
        graphiques['bar_boutiques'],
        graphiques['camembert'],
        graphiques['nuage_prix'],
        graphiques['bar_os_prix'],
        graphiques['pie_processeurs'],
        graphiques['box_prix_os'],
        df_filtre.to_dict('records'),
        [{"name": col, "id": col} for col in df_filtre.columns],
        boutique_options,
        max_price,
        marks,
        total_annonces,
        prix_moyen,
        prix_max,
        nb_boutiques
    )

if __name__ == '__main__':
    app.run(debug=True)