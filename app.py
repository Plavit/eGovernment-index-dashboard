# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import pathlib

from dash.dependencies import Input, Output
from urllib.parse import quote as urlquote
from flask import Flask, send_from_directory, send_file

from generators import generate_table, generate_world_map, generate_europe_map, generate_correlation

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Used dataset names
DATA_UN = 'eGov-t3.csv'
DATA_EU = 'eur-t2.csv'

df = pd.read_csv('data/{}'.format(DATA_UN))
dfeu = pd.read_csv('data/{}'.format(DATA_EU))

filtered_df = pd.DataFrame(df[df.Year == 2018], columns=['Czech name', 'UN eGov index'])
# Adding rank and percentile
filtered_df['Pořadí'] = filtered_df['UN eGov index'].rank(method='max')
filtered_df['Percentil'] = filtered_df['UN eGov index'].rank(pct=True)

# This is basically here only to use NumPy more than once ¯\_(ツ)_/¯
df['log of index'] = np.round(np.log(df['UN eGov index']), 2) if not df['UN eGov index'].isnull else 0

# Normally, Dash creates its own Flask server internally. By creating our own,
# we can create a route for downloading files directly:
server = Flask(__name__)


@server.route("/data/<path:path>")
def download(path):
    """Downloads the desired file from the data folder."""
    return send_file('data/'+path,
                     mimetype='text/csv',
                     attachment_filename=path,
                     as_attachment=True)

# Download link generation
def file_download_link(filename):
    """Creates a Plotly Dash 'A' element that downloads a file from the app."""
    location = "/data/{}".format(urlquote(filename))
    return html.A("Stáhnout dataset: " + filename, href=location)


app = dash.Dash(__name__, external_stylesheets=external_stylesheets, server=server)

server = app.server

app.layout = html.Div(children=[
    html.H1(children='eGovernment index viewer'),

    html.Div(children='''
        Jednoduchý přehled hodnot z indexů eGovernmentu od OSN a EU
    '''),

    # TODO create map callback to reset zoom if user zooms out too much
    html.Div(children=[

        dcc.Graph(id='world-map-with-slider', figure=generate_world_map(2018)),

        html.Label('Výběr roku'),
        dcc.Slider(
            id='year-slider',
            min=df['Year'].min(),
            max=df['Year'].max(),
            value=df['Year'].max(),
            marks={str(year): 'Rok {}'.format(year) if year == df['Year'].min() else str(year) for year in
                   df['Year'].unique()},
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
                    file_download_link(DATA_UN)
                ]
            )
        ],
    ),

    html.Div(children=[

        dcc.Graph(id='europe-map-with-slider', figure=generate_europe_map(dfeu, 2018)),

        dcc.Slider(
            id='year-slider-2',
            min=dfeu['Year'].min(),
            max=dfeu['Year'].max(),
            value=dfeu['Year'].max(),
            marks={str(year): 'Rok {}'.format(year) if year == df['Year'].min() else str(year) for year in
                   dfeu['Year'].unique()},
            step=None
        ),
        html.Div(
            children=[
                file_download_link(DATA_EU)
            ]
        )
    ], style={'columnCount': 1}),

    # TODO fix correlation
    # html.Div(children=[
    #     html.Label('Korelace'),
    #     dcc.Graph(id='correlation', figure=generate_correlation(df, dfeu)),
    # ], style={'columnCount': 1}),

], style={'columnCount': 1})


@app.callback(
    [Output('world-map-with-slider', 'figure'),
     Output('top-20-title', 'children'),
     Output('top-20-table', 'children')],
    [Input('year-slider', 'value')])
def update_world_map(selected_year):
    filtered_df = pd.DataFrame(df[df.Year == selected_year], columns=['Czech name', 'UN eGov index'])
    filtered_df['Pořadí'] = filtered_df['UN eGov index'].rank(method='max', ascending=False)
    filtered_df['Percentil'] = filtered_df['UN eGov index'].rank(pct=True)
    return generate_world_map(selected_year), "TOP 20 eGov " + str(selected_year), generate_table(filtered_df, 20)


@app.callback(
    Output('europe-map-with-slider', 'figure'),
    [Input('year-slider-2', 'value')])
def update_europe_map(selected_year):
    return generate_europe_map(dfeu, selected_year)


@app.server.route('/dash/urlToDownload')
def download_csv():
    return send_file('data/eur-t2.csv',
                     mimetype='text/csv',
                     attachment_filename='downloadFile.csv',
                     as_attachment=True)


if __name__ == '__main__':
    app.run_server(debug=True)
