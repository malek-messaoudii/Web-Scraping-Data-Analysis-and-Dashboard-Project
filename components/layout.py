import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.express as px
from .utils import load_and_preprocess_data, create_charts
from dash import dash_table


# Chargement et prétraitement des données
df = load_and_preprocess_data()

# Création des graphiques
charts = create_charts(df)

# Palette de couleurs
colors = {
    'background': '#f5f7fe',
    'card_background': '#ffffff',
    'text': '#2E3F4F',
    'accent': '#4E79A7',
    'header': '#3a5169',
    'border': '#e1e5eb'
}

def create_header():
    return dbc.Row([
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
    ], className="mb-4")

def create_kpi_cards(df):
    return dbc.Row([
        dbc.Col(create_kpi_card("TOTAL ANNONCES", f"{len(df):,}"), md=3),
        dbc.Col(create_kpi_card("PRIX MOYEN", f"{df['price'].mean():,.0f} TND"), md=3),
        dbc.Col(create_kpi_card("PRIX MAX", f"{df['price'].max():,.0f} TND"), md=3),
        dbc.Col(create_kpi_card("BOUTIQUES", f"{len(df['company'].unique())}"), md=3)
    ], className="mb-4 g-3")

def create_kpi_card(title, value):
    return dbc.Card([
        dbc.CardBody([
            html.H6(title, className="card-subtitle", style={'color': colors['text']}),
            html.H3(value, className="card-title mt-2", style={'color': colors['accent']}),
        ])
    ], style={
        'backgroundColor': colors['card_background'],
        'border': f'1px solid {colors["border"]}',
        'borderRadius': '8px'
    })

def create_section_title(title):
    return dbc.Row([
        dbc.Col(
            html.H2(
                title,
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
    ])

def create_graph_row(graph1, graph2=None, full_width=False):
    if full_width:
        return dbc.Row([
            dbc.Col(
                create_graph_card(graph1),
                width=12,
                className="mb-4"
            )
        ])
    
    return dbc.Row([
        dbc.Col(create_graph_card(graph1), md=6, className="mb-4"),
        dbc.Col(create_graph_card(graph2), md=6, className="mb-4")
    ], className="g-3")

def create_graph_card(figure):
    return dcc.Graph(
        figure=figure,
        style={
            'backgroundColor': colors['card_background'],
            'borderRadius': '8px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
            'padding': '15px',
            'height': '100%'
        }
    )

def create_filters():
    return dbc.Row([
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
                        max=int(df['price'].max()),
                        step=500,
                        value=[0, 5000],
                        marks={i: f"{i:,}" for i in range(0, int(df['price'].max())+1, 2000)},
                        tooltip={"placement": "bottom", "always_visible": True},
                        className="mb-4"
                    ),
                    html.Label("Sélection des boutiques:", className="mb-2", style={'color': colors['text']}),
                    dcc.Dropdown(
                        id='dropdown-boutiques',
                        options=[{'label': b, 'value': b} for b in sorted(df['company'].unique())],
                        multi=True,
                        placeholder="Toutes les boutiques...",
                        className="mb-4"
                    ),
                    html.Label("Recherche par mot-clé:", className="mb-2", style={'color': colors['text']}),
                    dbc.Input(
                        id='input-recherche',
                        placeholder="Entrez un mot-clé..."
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
    ], className="mb-4")

def create_data_table():
    return dbc.Row([
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
                        columns=[{"name": col, "id": col} for col in df.columns],
                        data=df.to_dict('records'),
                        page_size=10,
                        style_table={'overflowX': 'auto'},
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

def create_layout():
    return dbc.Container(
        fluid=True,
        style={
            'backgroundColor': colors['background'],
            'padding': '20px',
            'minHeight': '100vh'
        },
        children=[
            create_header(),
            create_kpi_cards(df),
            
            create_section_title("L'ensemble des graphiques"),
            create_graph_row(charts['bar_os_prix'], charts['pie_processeurs']),
            create_graph_row(charts['box_prix_os'], full_width=True),
            create_graph_row(charts['hist_prix'], charts['bar_boutiques']),
            create_graph_row(charts['camembert'], charts['nuage_prix']),
            
            create_section_title("Application des filtres"),
            create_filters(),
            
            create_section_title("Résultat du filtrage"),
            create_data_table()
        ]
    )