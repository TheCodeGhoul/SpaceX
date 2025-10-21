# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=([{'label': 'All Sites', 'value': 'ALL'}] +
                                             [{'label': s, 'value': s} for s in sorted(spacex_df['Launch Site'].unique())]),
                                    value='ALL',
                                    placeholder="Select a Launch Site",
                                    searchable=True,
                                    clearable=False,
                                    style={'width': '60%'}
                                ),

                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=min_payload,
                                    max=max_payload,
                                    step=1000,
                                    value=[min_payload, max_payload],
                                    marks={
                                        int(min_payload): str(int(min_payload)),
                                        int((min_payload + max_payload) / 2): str(int((min_payload + max_payload) / 2)),
                                        int(max_payload): str(int(max_payload)),
                                    },
                                    tooltip={"placement": "bottom", "always_visible": False}
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie(selected_site):
    if selected_site == 'ALL':
        # Total successful launches count by site
        # Use sum of class (1=success) as the value for each Launch Site
        df_all = (spacex_df.groupby('Launch Site', as_index=False)['class']
                  .sum()
                  .rename(columns={'class': 'successes'}))
        fig = px.pie(df_all,
                     names='Launch Site',
                     values='successes',
                     title='Total Successful Launches by Site')
    else:
        # Success vs. Failed counts for the selected site
        df_site = spacex_df[spacex_df['Launch Site'] == selected_site]
        # value_counts to get counts of 0 and 1
        counts = df_site['class'].value_counts().rename(index={1: 'Success', 0: 'Failure'}).reset_index()
        counts.columns = ['Outcome', 'Count']
        fig = px.pie(counts,
                     names='Outcome',
                     values='Count',
                     title=f'Success vs Failure for {selected_site}')
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter(selected_site, payload_range):
    low, high = payload_range
    # Filter by payload range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    dff = spacex_df[mask].copy()
    # Optionally filter by site
    if selected_site != 'ALL':
        dff = dff[dff['Launch Site'] == selected_site]

    fig = px.scatter(
        dff,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        hover_data=['Launch Site', 'Flight Number'],
        title=('Payload vs. Outcome (All Sites)'
               if selected_site == 'ALL'
               else f'Payload vs. Outcome ({selected_site})'),
        labels={'class': 'Launch Success (1=Success, 0=Fail)'}
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run()
