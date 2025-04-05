from dash.dependencies import Input, Output, State
from .utils import load_and_preprocess_data

def register_callbacks(app):
    # Chargement des données
    df = load_and_preprocess_data()

    @app.callback(
        Output('table-donnees', 'data'),
        [Input('slider-prix', 'value'),
         Input('dropdown-boutiques', 'value'),
         Input('input-recherche', 'value')]
    )
    def update_table(price_range, selected_shops, search_term):
        min_price, max_price = price_range
        filtered_df = df[(df['price'] >= min_price) & (df['price'] <= max_price)]
        
        if selected_shops:
            filtered_df = filtered_df[filtered_df['company'].isin(selected_shops)]
        
        if search_term:
            filtered_df = filtered_df[filtered_df['company_path'].str.contains(
                search_term, case=False, na=False
            )]
        
        return filtered_df.to_dict('records')