# Import necessary libraries
import dash
from dash import dcc
from dash import html
import plotly.express as px
import pandas as pd
import numpy as np

# Load sample data
df_gdp = pd.read_pickle('data_gapminder.pkl')

# turn year into a float
df_gdp['year'] = df_gdp['year'].astype(int)


# Create a Dash app
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div([
    html.H1('Gapminder Visualization'),
    html.Div([
        html.Div([
            dcc.Graph(id='graph'),
        ], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(id='bar-chart'),
        ], style={'width': '50%', 'display': 'inline-block'}),
    ], style={'display': 'flex'}),
    html.Div([
        dcc.Slider(
            id='year-slider',
            min=df_gdp['year'].min(),
            max=df_gdp['year'].max(),
            value=df_gdp['year'].min(),
            marks={str(year): str(year) for year in range(df_gdp['year'].min(), df_gdp['year'].max() + 1, 5)},
            step=5
        ),
        html.Label("Select a continent:"),
        dcc.Dropdown(
            id='continent-dropdown',
            options=[{"label": i, "value": i} for i in df_gdp["continent"].unique()],
            value=df_gdp['continent'].unique()[0],
            multi=True
        ),
    ], style={'margin': '20px 0px 50px 0px'}),
    html.Div(id='output-container', style={'margin-top': 20, 'font-weight': 'bold'})
])

# Define the callback
@app.callback(
    dash.dependencies.Output('graph', 'figure'),
    [dash.dependencies.Input('year-slider', 'value'),
    dash.dependencies.Input('continent-dropdown', 'value')])
def update_figure(selected_year, selected_continent):
    if type(selected_continent) == str:
        selected_continent = [selected_continent]
    filtered_df = df_gdp[(df_gdp['year'] == selected_year) & (df_gdp['continent'].isin(selected_continent))]
    # group by country
    filtered_df = filtered_df.groupby(['country', 'continent']).mean().reset_index()
    fig = px.scatter(filtered_df, x="gdpPercap", y="lifeExp", size="pop", color="continent", hover_name="country", size_max=60)
    fig.update_layout(transition_duration=500)
    return fig

# Callback for updating the bar chart
@app.callback(
    dash.dependencies.Output('bar-chart', 'figure'),
    [dash.dependencies.Input('year-slider', 'value'),
    dash.dependencies.Input('continent-dropdown', 'value')])
def update_bar_chart(selected_year, selected_continent):
    if type(selected_continent) == str:
        selected_continent = [selected_continent]
    # Filter the DataFrame for the selected year
    filtered_df = df_gdp[(df_gdp['year'] == selected_year) & (df_gdp['continent'].isin(selected_continent))]
    
    # Create a bar chart
    fig = px.bar(filtered_df, x='country', y='pop', title='Population by Country')

    # Optionally, you can customize the layout of the figure here
    fig.update_layout(transition_duration=500)

    return fig

# Define the callback for displaying the selected year
@app.callback(
    dash.dependencies.Output('output-container', 'children'),
    [dash.dependencies.Input('year-slider', 'value'),
     dash.dependencies.Input('continent-dropdown', 'value')])
def update_output(selected_year, selected_continent):
    return 'Selected Year: {}'.format(selected_year)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)