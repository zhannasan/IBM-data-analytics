# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
launch_sites=set(spacex_df['Launch Site'])

def myfunc(a):
  return {'label': a, 'value':a}
opts=[{'label': 'All Sites', 'value': 'ALL'}]
opts=opts+list(map(myfunc, set(spacex_df['Launch Site'])))
# 
min_value=0
max_value=10000
marks= {i : i for i in range(0, max_value+1, 1000) }
# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                html.Br(),
                                dcc.Dropdown(
                                            id='site-dropdown',
                                            options=opts,
                                            value='ALL',
                                            placeholder="Select launch site",
                                            style={'width':'100%', 'padding':'3px', 'font-size': '20px', 'text-align-last' : 'center'}),
                                    # Place them next to each other using the division style
                                
                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=min_value, max=max_value, step=1000,
                                                marks=marks,
                                                value=[min_value, max_value]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback([Output(component_id='success-pie-chart', component_property='figure'),
                Output(component_id='success-payload-scatter-chart', component_property='figure')],
                [Input(component_id='site-dropdown', component_property='value'), 
                Input(component_id='payload-slider', component_property='value')])

def get_pie_chart(entered_site, entered_payload):
    if entered_site == 'ALL':
        all_data = spacex_df.groupby('Launch Site')['class'].mean().reset_index()

        pie_plot = px.pie(all_data, values='class', 
                        names=all_data['Launch Site'], 
                        title='Total success launches by site')
        scatter_plot= px.scatter(spacex_df, x=spacex_df['Payload Mass (kg)'], y=spacex_df['class'],color=spacex_df['Booster Version'],  hover_name=spacex_df['Booster Version'])
        scatter_plot.update_layout(title='Correlation between payload and success for all sites', xaxis_title='Payload Mass (kg)', yaxis_title='Class')
        return [pie_plot,scatter_plot]
    else:
        filtered_df = spacex_df[spacex_df['Launch Site']==entered_site]
        pie_df=filtered_df.groupby('class')["class"].count().reset_index(name ='Sums')
        scatter_df=filtered_df[filtered_df['Payload Mass (kg)'].between(entered_payload[0],entered_payload[1])]
        
        pie_plot = px.pie(pie_df, values='Sums', 
                        names=pie_df['class'], 
                        title='Total success launches for site '+entered_site)
        scatter_plot= px.scatter(scatter_df, x=scatter_df['Payload Mass (kg)'], y=scatter_df['class'], color=scatter_df['Booster Version'], hover_name=scatter_df['Booster Version'])
        scatter_plot.update_layout(title='Correlation between payload and success for '+entered_site, xaxis_title='Payload Mass (kg)', yaxis_title='Class')
        return [pie_plot,scatter_plot]
        # return the outcomes piechart for a selected site


# Run the app.groupby('class').sum().reset_index()
if __name__ == '__main__':
    app.run_server()
