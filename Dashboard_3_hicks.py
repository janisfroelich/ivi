# Import necessary libraries
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State, ALL
import plotly.express as px
import pandas as pd

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
        dcc.Graph(id='graph'),
        html.Div(id='output-container', style={'margin-top': 20, 'font-weight': 'bold'})
    ]),
    html.Div([
        html.Div(id='year-buttons', style={'margin': '10px 0px'}),
        html.Div(id='continent-buttons', style={'margin': '10px 0px'}),
    ], style={'margin': '20px 0px 50px 0px'})
])

# Callback for creating year and continent buttons
@app.callback(
    [Output('year-buttons', 'children'),
     Output('continent-buttons', 'children')],
    [Input('graph', 'figure')])
def create_buttons(_):
    year_buttons = [html.Button(year, id={'type': 'year-button', 'index': year}, n_clicks=0) for year in df_gdp['year'].unique()]
    continent_buttons = [html.Button(continent, id={'type': 'continent-button', 'index': continent}, n_clicks=0) for continent in df_gdp['continent'].unique()]
    return year_buttons, continent_buttons

# Define the callback for updating the graph
@app.callback(
    Output('graph', 'figure'),
    [Input({'type': 'year-button', 'index': ALL}, 'n_clicks'),
     Input({'type': 'continent-button', 'index': ALL}, 'n_clicks')])
def update_figure(year_clicks, continent_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        year_value = df_gdp['year'].min()
        continent_value = df_gdp['continent'].unique()[0]
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        button_id = eval(button_id)  # Convert string representation back to dictionary
        button_type = button_id['type']
        button_value = button_id['index']
        if button_type == 'year-button':
            year_value = float(button_value)
            continent_value = df_gdp['continent'].unique()[0]  # Default continent
        elif button_type == 'continent-button':
            year_value = df_gdp['year'].min()  # Default year
            continent_value = button_value

    filtered_df = df_gdp[(df_gdp['year'] == year_value) & (df_gdp['continent'] == continent_value)]
    fig = px.scatter(filtered_df, x="gdpPercap", y="lifeExp", size="pop", color="continent", hover_name="country", size_max=60)
    fig.update_layout(transition_duration=500)
    return fig

# Define the callback for displaying the selected year and continent
@app.callback(
    Output('output-container', 'children'),
    [Input({'type': 'year-button', 'index': ALL}, 'n_clicks'),
     Input({'type': 'continent-button', 'index': ALL}, 'n_clicks')])
def update_output(year_clicks, continent_clicks):
    ctx = dash.callback_context

    if not ctx.triggered:
        return 'Select Year and Continent'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        button_id = eval(button_id)
        return f'Selected: {button_id["type"]} - {button_id["index"]}'

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
