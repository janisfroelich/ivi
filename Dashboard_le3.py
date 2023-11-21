# Import necessary libraries
import dash
from dash import dcc
from dash import html
import plotly.express as px
import pandas as pd
import numpy as np
from dash import callback_context

# Load sample data
df_gdp = pd.read_pickle('data_gapminder.pkl')

# convert year to int
df_gdp.year = df_gdp.year.astype(int)

# Create a Dash app
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div([
    html.H1("Gapminder Dataset", style={'text-align': 'center'}),
    html.Div([
        html.Div([
            html.Label("Select a year:"),
            dcc.Slider(
                id='year-slider',
                min=df_gdp['year'].min(),
                max=df_gdp['year'].max(),
                value=df_gdp['year'].min(),
                marks={str(year): str(year) for year in range(df_gdp['year'].min(), df_gdp['year'].max() + 1, 5)},
                step=5
            ),
        ], style={'width': '48%', 'display': 'inline-block'}),
        html.Div([
            html.Label("Select a continent:"),
            dcc.Dropdown(
                id='continent-dropdown',
                options=[{'label': continent, 'value': continent} for continent in df_gdp['continent']. unique()],
                value=df_gdp['continent'].unique()[0]
            ),
        ], style={'width': '48%', 'display': 'inline-block'}),
    ], style={'padding': '20px', 'display': 'flex', 'justify-content': 'space-between'}),
    html.Div([
        html.Div([
            dcc.Graph(id='graph'),
        ], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(id='bar-chart'),
        ], style={'width': '50%', 'display': 'inline-block'}),
    ], style={'display': 'flex'}),
    html.Div(id='output-container', style={'margin-top': 20, 'font-weight': 'bold'})  # Adding the output-container here
])

# Define the callback for the output-container
@app.callback(
    dash.dependencies.Output('output-container', 'children'),  # Corrected the id here
    [dash.dependencies.Input('year-slider', 'value'),
     dash.dependencies.Input('continent-dropdown', 'value')])
def update_output(selected_year, selected_continent):
    return 'Selected Year: {}, Selected Continent: {}'.format(int(selected_year), selected_continent)


# Define the callbacks for the scatterplot and bar chart
@app.callback(
    [dash.dependencies.Output('graph', 'figure'), 
     dash.dependencies.Output('bar-chart', 'figure')],
    [dash.dependencies.Input('year-slider', 'value'),
     dash.dependencies.Input('continent-dropdown', 'value')])
def update_charts(selected_year, selected_continent):
    if type(selected_continent) == str:
        selected_continent = [selected_continent]

    # Filter the DataFrame for the selected year and continent
    filtered_df = df_gdp[(df_gdp['year'] == selected_year) & (df_gdp['continent'].isin(selected_continent))]
    
    # Scatter plot
    scatter_fig = px.scatter(filtered_df, x='gdpPercap', y='lifeExp', size='pop', hover_name='country')
    scatter_fig.update_layout(transition_duration=500, hovermode='closest', hoverdistance=100)

    # Bar chart
    bar_fig = px.bar(filtered_df, x='country', y='pop', title='Population by Country')
    bar_fig.update_layout(transition_duration=500)

    return scatter_fig, bar_fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)