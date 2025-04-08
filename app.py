import dash
import dash_bootstrap_components as dbc
from components.layout import create_layout
from components.callbacks import register_callbacks

# Initialisation de l'application
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.LUX],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)
app.title = "Tableau de Bord des Annonces"

# Configuration du layout
app.layout = create_layout()

# Enregistrement des callbacks
register_callbacks(app)

if __name__ == '__main__':
    app.run(debug=True, port=5000)