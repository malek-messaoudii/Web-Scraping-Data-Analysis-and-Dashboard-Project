import pandas as pd
import plotly.express as px

def load_and_preprocess_data(filepath="data/data-final.csv"):
    # Chargement des données
    df = pd.read_csv(filepath)
    
    # Nettoyage des données
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df.dropna(subset=['price'], inplace=True)
    df['company'] = df['company'].astype('category')
    df['ram'] = df['ram'].str.extract('(\d+)').astype(float)
    
    # Normalisation des systèmes d'exploitation
    df['os'] = df['os'].str.lower()
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
    
    # Normalisation des marques de processeurs
    df['processor_brand'] = df['processor_brand'].str.lower().str.strip()
    processor_mapping = {
        'intel': 'Intel',
        'amd': 'AMD',
        'apple': 'Apple',
        'qualcomm': 'Qualcomm',
        'mediatek': 'Mediatek'
    }
    
    df['processor_brand'] = df['processor_brand'].replace(processor_mapping, regex=False)
    df['os'] = df['os'].replace(os_mapping, regex=True)
    
    return df

def create_charts(df):
    # Préparation des données
    company_counts = df['company'].value_counts().reset_index()
    company_counts.columns = ['Boutique', "Nombre d'annonces"]
    
    os_prices = df.groupby('os')['price'].mean().reset_index().sort_values('price', ascending=False)
    ram_prices = df.groupby('ram')['price'].mean().reset_index()
    processor_counts = df['processor_brand'].value_counts().reset_index()
    processor_counts.columns = ['Marque', "Nombre d'annonces"]
    
    # Création des graphiques
    charts = {
        'hist_prix': create_histogram(
            df, x='price', nbins=30,
            title="Distribution des prix",
            labels={'price': 'Prix (TND)', 'count': "Nombre d'annonces"},
            color='#4E79A7'
        ),
        'bar_boutiques': create_bar_chart(
            company_counts, x='Boutique', y="Nombre d'annonces",
            title="Nombre d'annonces par boutique",
            color='#F28E2B'
        ),
        'camembert': create_pie_chart(
            company_counts, names='Boutique', values="Nombre d'annonces",
            title="Répartition par boutique",
            hole=0.3
        ),
        'nuage_prix': create_scatter_plot(
            df, x='company', y='price',
            title="Distribution des prix par boutique",
            labels={'company': 'Boutique', 'price': 'Prix (TND)'},
            color='#E15759'
        ),
        'bar_os_prix': create_bar_chart(
            os_prices, x='os', y='price',
            title="Prix moyen par système d'exploitation",
            labels={'os': 'Système', 'price': 'Prix moyen (TND)'},
            color='#76B7B2'
        ),
        'pie_processeurs': create_pie_chart(
            processor_counts, names='Marque', values="Nombre d'annonces",
            title="Répartition des marques de processeurs",
            hole=0.4
        ),
        'box_prix_os': create_box_plot(
            df, x='os', y='price',
            title="Distribution des prix par système d'exploitation",
            labels={'os': 'Système', 'price': 'Prix (TND)'},
            color='#FF9DA7'
        )
    }
    
    return charts

def apply_chart_styles(fig):
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
    return fig

def create_histogram(data, x, nbins, title, labels, color):
    fig = px.histogram(
        data, x=x, nbins=nbins,
        title=title,
        labels=labels,
        template='plotly_white',
        color_discrete_sequence=[color]  # Notez la liste autour de color
    )
    return apply_chart_styles(fig)

def create_bar_chart(data, x, y, title, labels=None, color=None):
    fig = px.bar(
        data, x=x, y=y,
        title=title,
        labels=labels,
        template='plotly_white',
        color_discrete_sequence=[color] if color else None
    )
    return apply_chart_styles(fig)

def create_pie_chart(data, names, values, title, hole=0):
    fig = px.pie(
        data, names=names, values=values,
        title=title,
        template='plotly_white',
        hole=hole
    )
    return apply_chart_styles(fig)

def create_scatter_plot(data, x, y, title, labels, color):
    fig = px.scatter(
        data, x=x, y=y,
        title=title,
        labels=labels,
        template='plotly_white',
        color_discrete_sequence=[color]
    )
    return apply_chart_styles(fig)

def create_box_plot(data, x, y, title, labels, color):
    fig = px.box(
        data, x=x, y=y,
        title=title,
        labels=labels,
        template='plotly_white',
        color_discrete_sequence=[color]
    )
    return apply_chart_styles(fig)