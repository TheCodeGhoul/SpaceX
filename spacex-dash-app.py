

# ---- Imports 
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# ---- Load data 
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()


site_options = [{'label': 'All Sites', 'value': 'ALL'}] + [
    {'label': s, 'value': s} for s in sorted(spacex_df['Launch Site'].unique())
]

# ---- App 
app = dash.Dash(__name__)

# ---- Layout 
app.layout = html.Div([
    html.H1(
        'SpaceX Launch Records Dashboard',
        style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}
    ),

    # ============================ TASK 1 ===============================
    # Add a Launch Site Drop-down Input Component

    dcc.Dropdown(
        id='site-dropdown',
        options=site_options,
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True
    ),
    # ========================== /TASK 1 ================================
    html.Br(),

    # ============================ TASK 2 ===============================
    # Pie chart container

    html.Div(dcc.Graph(id='success-pie-chart')),
    # ========================== /TASK 2 ================================
    html.Br(),

    html.P("Payload range (Kg):"),

    # ============================ TASK 3 ===============================
    # Range Slider to Select Payload
    # - Drives the scatter plot (Task 4)
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        value=[min_payload, max_payload],
        step=1000,
        marks={
            int(min_payload): str(int(min_payload)),
            int(max_payload): str(int(max_payload))
        }
    ),
    # ========================== /TASK 3 ================================
    html.Br(),

    # ============================ TASK 4 ===============================
    # Scatter chart container

    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
    # ========================== /TASK 4 ================================
])

# ============================ TASK 2 ==================================
# Callback: Input = site-dropdown, Output = success-pie-chart

@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie(selected_site):
    if selected_site == 'ALL':
        df = spacex_df[spacex_df['class'] == 1]
        fig = px.pie(
            df,
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
    else:
        df = spacex_df[spacex_df['Launch Site'] == selected_site]
        fig = px.pie(
            df,
            names='class',  # 1 = success, 0 = failure
            title=f'Success vs Failure for {selected_site}',
            labels={'class': 'Outcome'}
        )
        fig.update_traces(textinfo='value+percent')
        fig.update_layout(legend_title_text='Outcome')
    return fig


# ============================ TASK 2 and 4 ==================================
# Callback: Inputs = site-dropdown and payload-slider, Output = scatter chart
# - Filters by payload range
# - If a site is chosen, filter to that site as well
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter(selected_site, payload_range):
    low, high = payload_range
    df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]
    if selected_site != 'ALL':
        df = df[df['Launch Site'] == selected_site]

    fig = px.scatter(
        df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        hover_data=['Launch Site'],
        title=('Correlation between Payload and Launch Success'
               if selected_site == 'ALL'
               else f'Correlation between Payload and Launch Success — {selected_site}'),
        labels={'class': 'Launch Success (1=Success, 0=Failure)'}
    )
    return fig
# ========================== /TASK 4 ===================================

if __name__ == '__main__':

    app.run_server()
