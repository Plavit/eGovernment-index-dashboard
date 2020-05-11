# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output
from urllib.parse import quote as urlquote

from generators import generate_table, generate_world_map, generate_europe_map

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
df = pd.read_csv('data/eGov-t3.csv')
dfeu = pd.read_csv('data/eur-t1.csv')

# TODO add rank
filtered_df = pd.DataFrame(df[df.Year == 2018], columns=['Czech name', 'eGov index'])


# TODO fix download link
def file_download_link(filename):
    """Creates a Plotly Dash 'A' element that downloads a file from the app."""
    location = "/data/{}".format(urlquote(filename))
    return html.A(filename, href=location)


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='eGovernment index viewer'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    html.Label('Slider'),
    dcc.Slider(
        min=2012,
        max=2018,
        step=2,
        marks={i: 'Rok {}'.format(i) if i == 2012 else str(i) for i in range(2012, 2018, 2)},
        value=2016,
    ),

    # TODO create map callback to reset zoom if user zooms out too much
    html.Div(children=[

        dcc.Graph(id='world-map-with-slider', figure=generate_world_map(2018)),

        dcc.Slider(
            id='year-slider',
            min=df['Year'].min(),
            max=df['Year'].max(),
            value=df['Year'].max(),
            marks={str(year): str(year) for year in df['Year'].unique()},
            step=None
        ),
    ], style={'columnCount': 1}),

    html.Div(
        children=[
            html.H4(
                id='top-20-title',
                children='TOP 20 eGov selected year'),
            html.Div(
                id='top-20-table',
                children=[
                    generate_table(filtered_df, 20)
                ], style={'columnCount': 4}),
            html.Div(
                children=[
                    file_download_link('eGov-t3.csv')
                ]
            )
        ],
    ),

    html.Div(children=[

        dcc.Graph(id='Europe-map-with-slider', figure=generate_europe_map(dfeu, 2018)),

        dcc.Slider(
            id='year-slider-2',
            min=dfeu['Year'].min(),
            max=dfeu['Year'].max(),
            value=dfeu['Year'].max(),
            marks={str(year): str(year) for year in dfeu['Year'].unique()},
            step=None
        ),
    ], style={'columnCount': 1}),

], style={'columnCount': 1})


@app.callback(
    [Output('world-map-with-slider', 'figure'),
     Output('top-20-title', 'children'),
     Output('top-20-table', 'children')],
    [Input('year-slider', 'value')])
def update_figure(selected_year):
    # TODO add rank
    filtered_df = pd.DataFrame(df[df.Year == selected_year], columns=['Czech name', 'eGov index']).reset_index()
    return generate_world_map(selected_year), "TOP 20 eGov " + str(selected_year), generate_table(filtered_df, 20)


if __name__ == '__main__':
    app.run_server(debug=True)
