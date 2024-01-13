# Import necessary libraries
import dash
from dash import dcc
from dash import html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output, State

# Load sample data
df_gdp = pd.read_pickle('data_gapminder_join.pkl')

# convert year to int
df_gdp.year = df_gdp.year.astype(int)

# Create a Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Define the layout with a location component and a content div
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='shared-data', storage_type='session'),
    html.Div([
        html.Div([
            html.H2("Menu", style={'text-align': 'center'}),
            dcc.Link("Home", href="/", style={
                    'display': 'block', 
                    'margin': '10px 0',  # Adds space above and below the link
                    'text-align': 'center',  # Centers the link text
                    'font-family': 'Arial, sans-serif',  # Changes the font family
                    'font-size': '20px',  # Increases the font size
                }),
            dcc.Link("Map Page", href="/map", style={
                    'display': 'block', 
                    'margin': '10px 0',  # Adds space above and below the link
                    'text-align': 'center',  # Centers the link text
                    'font-family': 'Arial, sans-serif',  # Changes the font family
                    'font-size': '20px',  # Increases the font size
                }),
        ], style={'width': '20%', 'height': '100vh', 'position': 'fixed', 'zIndex': 1,
                  'top': '0', 'left': '0', 'background-color': '#f8f9fa',
                  'overflow-x': 'hidden', 'padding-top': '20px'}),
    ]),
    html.Div(id='page-content', style={'marginLeft': '20%', 'width': '80%'})
])

@app.callback(
    Output('shared-data', 'data'),
    [Input('year-slider', 'value')],
    [State('shared-data', 'data')])
def update_store(selected_year, data):
    if data is None:
        data = {}
    data['selected_year'] = selected_year
    return data

@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname'),
     Input('shared-data', 'data')])
def display_page(pathname, data):
    selected_year = data.get('selected_year', df_gdp['year'].max()) if data else df_gdp['year'].max()
    year_slider = html.Div([
        html.Label("Select a year:"),
        dcc.Slider(
            id='year-slider',
            min=df_gdp['year'].min(),
            max=df_gdp['year'].max(),
            value=selected_year,
            marks={str(year): str(year) for year in df_gdp['year'].unique()},
            step=None
        )
    ], style={'width': '90%', 'margin': '20px auto'})

    if pathname == '/map':
        # Map page content
        return html.Div([
                html.H1("Gapminder Map", style={'text-align': 'center'}),
                html.Div([  # Container for the filters
                    html.Div([  # Container for the year slider
                        year_slider
                    ], style={'width': '50%', 'display': 'inline-block', 'margin-right': '10px'}),  # Set to 50% width and inline-block for side-by-side display
                    html.Div([  # Container for the dropdown
                        dcc.Dropdown(
                            id='country-search-dropdown',
                            options=[{'label': country, 'value': country} for country in df_gdp['country'].unique()],
                            placeholder="Select a country",)
                    ], style={'width': '50%', 'display': 'inline-block'}),  # Set to 50% width and inline-block for side-by-side display
                ], style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}),  # This will ensure the filters are centered and flexibly aligned
                html.Div([
                    dcc.Graph(id='map-graph', style={'height': 'auto', 'width': '70%'}),
                ],  style={'margin-left': 'auto', 'margin-right': 'auto', 'margnin-top': '-20px', 'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'height': '100%'}),   # This will center the map in the div
            ], style={'height': '100vh', 'overflow': 'hidden'})
    else:
        # Home page content (default page)
        return html.Div([
                html.H1("Gapminder Dataset", style={'text-align': 'center', 'margin-bottom': '20px'}),
                html.Div([
                    html.Div([
                        html.Label("Select a year:"),
                        dcc.Slider(
                            id='year-slider',
                            min=df_gdp['year'].min(),
                            max=df_gdp['year'].max(),
                            value=selected_year,
                            marks={str(year): str(year) for year in df_gdp['year'].unique()},
                            step=None
                        ),
                    ], style={'width': '30%', 'display': 'inline-block'}),
                    html.Div([
                        html.Label("Select a continent:"),
                        dcc.Dropdown(
                            id='continent-dropdown',
                            options=[{'label': continent, 'value': continent} for continent in df_gdp['continent'].unique()],
                            value=df_gdp['continent'].unique()[0]
                        ),
                    ], style={'width': '30%', 'display': 'inline-block'}),
                    html.Div([
                        html.Label("Select a country:"),
                        dcc.Dropdown(
                                id='country-search-dropdown',  # Note the updated id here
                                options=[],  # Initially empty, will be populated via callback
                                placeholder="Select a country",
                        ),
                    ], style={'width': '30%', 'display': 'inline-block'}),
                ], style={'display': 'flex', 'justify-content': 'space-around', 'align-items': 'center', 'margin-bottom': '20px'}),
                html.Div([
                    dcc.Graph(id='graph', style={'display': 'inline-block', 'width': '49%'}),
                    dcc.Graph(id='bar-chart', style={'display': 'inline-block', 'width': '49%'}),
                ], style={'display': 'flex'}),
            ])

# Callback to update the country dropdown based on the selected continent
@app.callback(
    Output('country-search-dropdown', 'options'),
    [Input('continent-dropdown', 'value')])
def update_country_dropdown(selected_continent):
    if selected_continent is not None:
        filtered_countries = df_gdp[df_gdp['continent'] == selected_continent]['country'].unique()
        return [{'label': country, 'value': country} for country in filtered_countries]
    return []


# Define the callback for the map-graph - assuming you only want to show it on the map page
@app.callback(
    Output('map-graph', 'figure'),
    [Input('url', 'pathname'),
     Input('country-search-dropdown', 'value'),
     Input('year-slider', 'value')],
     [State('shared-data', 'data')])  # The shared data store is also a state)
def update_map(pathname, selected_country, selected_year, data):
    if pathname == '/map':
        selected_year = int(selected_year) if selected_year is not None else df_gdp['year'].max()
        # Assuming you want to display the latest year's data on the map
        df_filtered = df_gdp[df_gdp['year'] == selected_year]

        if selected_country in df_filtered['country'].unique():
            df_filtered = df_filtered[df_filtered['country'] == selected_country]

        

        # Create the map figure
        map_fig = px.choropleth(df_filtered, locations='alpha-3', hover_name='country', color='gdpPercapita',
                                color_continuous_scale=px.colors.sequential.Plasma,
                                 hover_data={
                                            'alpha-3': False,  # Hide ISO code
                                            'country': True,  # Display the country name
                                            'gdpPercapita': ':.2f',  # Display GDP per capita with 2 decimal places
                                            'population': True,  # Display population
                                            'lifeExpectancy': ':.1f'
                                            # Add other data columns here if you want them in the tooltip
                                        })

        if selected_country:
            map_fig.update_traces(marker_line_width=3, marker_line_color='gold')  # Highlight with a gold outline
            
            country_code = df_filtered[df_filtered['country'] == selected_country]['alpha-3'].iloc[0]
            # Add an annotation
            map_fig.add_annotation(
                x=country_code,
                y=country_code,
                text=f"{selected_country}: {df_filtered['gdpPercap']}",  # Customize with the data you want to show
                showarrow=True,
                arrowhead=1
            )

        
        # Update color bar size
        map_fig.update_layout(
            coloraxis_colorbar=dict(
                thickness=10,  # Adjust the thickness of the color bar (in pixels)
                len=0.3,  # Adjust the length of the color bar (fraction of the plot height)
                title='GDP per Capita',  # Color bar title
                titleside='right'
            ),
            transition_duration=500,
            width=1000,  # Set the width of the map
            height=1000,
            margin=dict(l=0, r=0, t=0, b=0, autoexpand=True) # Set the height of the map
            )
        
        return map_fig
    return {}


@app.callback(
    Output('graph', 'figure'),
    [Input('year-slider', 'value'),
    Input('continent-dropdown', 'value'),
    Input('country-search-dropdown', 'value')])
def update_scatter(selected_year, selected_continent, selected_country):

    if selected_country is None:
        filtered_df = df_gdp[(df_gdp['year'] == selected_year) & (df_gdp['continent'] == selected_continent)]
    else:
        filtered_df = df_gdp[(df_gdp['year'] == selected_year) & (df_gdp['continent'] == selected_continent) & (df_gdp['country'] == selected_country)]

    scatter_fig = px.scatter(filtered_df, x='gdpPercapita', y='lifeExpectancy', size='population', hover_name='country', color='country')
    scatter_fig.update_layout(transition_duration=500)
    return scatter_fig

# Callback for bar chart
@app.callback(
    Output('bar-chart', 'figure'),
    [Input('year-slider', 'value'),
    Input('continent-dropdown', 'value'),
    Input('country-search-dropdown', 'value')])
def update_bar(selected_year, selected_continent, selected_country):

    if selected_country is None:
        filtered_df = df_gdp[(df_gdp['year'] == selected_year) & (df_gdp['continent'] == selected_continent)]
    else:
        filtered_df = df_gdp[(df_gdp['year'] == selected_year) & (df_gdp['continent'] == selected_continent) & (df_gdp['country'] == selected_country)]
   
    bar_fig = px.bar(filtered_df, x='country', y='population')
    bar_fig.update_layout(transition_duration=500)
    return bar_fig

# Define the callbacks for the scatterplot and bar chart as before
# ...

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
