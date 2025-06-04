import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Charger les données
df = pd.read_csv("spacex_launch_dash.csv")
max_payload = df['Payload Mass (kg)'].max()
min_payload = df['Payload Mass (kg)'].min()

# Initialiser l'application Dash
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('Tableau de bord des lancements SpaceX',
            style={'textAlign': 'center', 'color': '#503D36', 'fontSize': 40}),

    
    dcc.Dropdown(
        id='site-selector',
        options=[
            {'label': 'Tous les sites', 'value': 'All Sites'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
        ],
        value='All Sites',
        placeholder='Choisissez un site de lancement',
        searchable=True
    ),
    html.Br(),

    
    html.Div(dcc.Graph(id='pie-chart-success')),
    html.Br(),

    html.P("Plage de masse utile (kg) :"),

    
    dcc.RangeSlider(
        id='payload-range',
        min=0,
        max=10000,
        step=500,
        marks={i: str(i) for i in range(0, 10001, 1000)},
        value=[min_payload, max_payload]
    ),
    html.Br(),

    
    html.Div(dcc.Graph(id='scatter-payload-success'))
])

@app.callback(
    Output('pie-chart-success', 'figure'),
    Input('site-selector', 'value')
)
def update_pie_chart(site):
    if site == 'All Sites':
        
        summary = df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(summary, values='class', names='Launch Site', title="Réussites totales par site")
    else:
        filtered = df[df['Launch Site'] == site]
        counts = filtered['class'].value_counts().rename(index={1: 'Succès', 0: 'Échecs'}).reset_index()
        counts.columns = ['Statut', 'Nombre']
        fig = px.pie(counts, values='Nombre', names='Statut', title=f"Succès vs Échecs pour {site}")
    return fig

@app.callback(
    Output('scatter-payload-success', 'figure'),
    [Input('site-selector', 'value'),
     Input('payload-range', 'value')]
)
def update_scatter(site, payload_range):
    low, high = payload_range
    filtered = df[(df['Payload Mass (kg)'] >= low) & (df['Payload Mass (kg)'] <= high)]
    if site != 'All Sites':
        filtered = filtered[filtered['Launch Site'] == site]
    fig = px.scatter(filtered, x='Payload Mass (kg)', y='class', color='Booster Version Category',
                     hover_data=['Launch Site'], title='Corrélation masse utile et succès de lancement')
    return fig

if __name__ == '__main__':
    app.run(debug=True)

