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

from generators import generate_table, generate_world_map, generate_europe_map

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Used dataset names
DATA_UN = 'eGov-t4.csv'
DATA_EU = 'eur-t2.csv'

df = pd.read_csv('data/{}'.format(DATA_UN))
dfeu = pd.read_csv('data/{}'.format(DATA_EU))

filtered_df = pd.DataFrame(df[df.Year == df['Year'].max()], columns=['Czech name', 'UN eGov index'])
# Adding rank and percentile
filtered_df['Pořadí'] = filtered_df['UN eGov index'].rank(method='max', ascending=False)
filtered_df['Percentil'] = filtered_df['UN eGov index'].rank(pct=True)
filtered_df['Percentil'] = (filtered_df['Percentil'] * 100).round(1).astype(str) + '%'
filtered_df = filtered_df[['Pořadí', 'Czech name', 'UN eGov index', 'Percentil']]
filtered_df = filtered_df.rename(columns={'Czech name': 'Země','UN eGov index': 'index eGov OSN'})

filtered_df_eu = pd.DataFrame(dfeu[dfeu.Year == dfeu['Year'].max()], columns=['Czech name', 'EU eGov index'])
# Adding rank and percentile
filtered_df_eu['Pořadí'] = filtered_df_eu['EU eGov index'].rank(method='max', ascending=False)
filtered_df_eu['Percentil'] = filtered_df_eu['EU eGov index'].rank(pct=True)
filtered_df_eu['Percentil'] = (filtered_df_eu['Percentil'] * 100).round(1).astype(str) + '%'
filtered_df_eu = filtered_df_eu[['Pořadí', 'Czech name', 'EU eGov index', 'Percentil']]
filtered_df_eu = filtered_df_eu.rename(columns={'Czech name': 'Země', 'EU eGov index': 'index eGov EU'})

# This is basically here only to use NumPy more than once ¯\_(ツ)_/¯
df['log of index'] = np.round(np.log(df['UN eGov index']), 2) if not df['UN eGov index'].isnull else 0

# Normally, Dash creates its own Flask server internally. By creating our own,
# we can create a route for downloading files directly:
server = Flask(__name__)


@server.route("/data/<path:path>")
def download(path):
    """Downloads the desired file from the data folder."""
    return send_file('data/' + path,
                     mimetype='text/csv',
                     attachment_filename=path,
                     as_attachment=True)


# Download link generation
def file_download_link(filename):
    """Creates a Plotly Dash 'A' element that downloads a file from the app."""
    location = "/data/{}".format(urlquote(filename))
    return html.Div(
        [
            html.A(
                html.Button("Stáhnout kompletní dataset: " + filename),
                href=location,
            )
        ],
        className="download-button"
    )


app = dash.Dash(__name__, external_stylesheets=external_stylesheets, server=server)

server = app.server

app.layout = html.Div(
    children=[
        html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src='assets/Logo-text.png',
                            draggable='False',
                            id="logo",
                            height='auto',
                            width=300,
                        ),
                    ],
                    className="two columns",
                ),
                html.Div(
                    [
                        html.H3(
                            "Přehled eGov indexů",
                            style={"margin-bottom": "0px"},
                        ),
                        html.H5(
                            "Jednoduchý přehled hodnot z indexů eGovernmentu od OSN a EU",
                            style={"margin-top": "0px"}
                        ),

                    ],
                    className="eight columns",
                    id="title",
                ),
                html.Div(
                    [
                        html.A(
                            html.Button("Kontaktovat autora", id="contact-button"),
                            href="mailto:marek.szeles@eforce.cvut.cz",
                        )
                    ],
                    className="two columns",
                    id="button",
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),

        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    children=[
                                        html.Img(
                                            src="https://1000logos.net/wp-content/uploads/2018/01/united-nations-logo.png",
                                            draggable='False',
                                            id="logo_un",
                                            height=150,
                                            width='auto',
                                        ),
                                        html.Div(
                                            [
                                                html.H3("Index eGovernmentu OSN"),
                                                html.P("Index eGovernmentu publikovaný Organizací spojených národů od roku 2001. Bližší popis metodologie bude přidán v budoucnu.")
                                            ]
                                        )
                                    ],
                                    id="un_description",
                                    className="pretty_container description twelve columns flex-display"
                                ),
                            ],
                            className="content_holder row twelve columns flex-display"
                        ),
                        html.Div(
                            [
                                html.Div(
                                    children=[
                                        html.Label(
                                            html.H6('Výběr roku')
                                        ),
                                        dcc.Slider(
                                            id='year-slider',
                                            min=df['Year'].min(),
                                            max=df['Year'].max(),
                                            value=df['Year'].max(),
                                            marks={
                                                str(year): 'Rok {}'.format(year) if year == df['Year'].min() else str(
                                                    year)
                                                for year
                                                in
                                                df['Year'].unique()},
                                            step=None,
                                            className='slider'
                                        ),

                                        dcc.Graph(id='world-map-with-slider',
                                                  figure=generate_world_map(df, df['Year'].max())),

                                    ],
                                    className="pretty_container ten columns",
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Div(
                                                    [html.H6(str(int(filtered_df.loc[filtered_df['Země'] == 'Česká republika']['Pořadí']))+". místo", id="un_rank_value"),
                                                     html.P("Pořadí ČR", id="un_rank_text")],
                                                    id="un_rank",
                                                    className="mini_container",
                                                ),
                                                html.Div(
                                                    [html.H6(str(np.round(float(filtered_df.loc[filtered_df['Země'] == 'Česká republika']['index eGov OSN']),3))+"", id="un_score_value"),
                                                     html.P("Skóre ČR", id="un_score_text")],
                                                    id="un_score",
                                                    className="mini_container",
                                                ),
                                                html.Div(
                                                    [html.H6(filtered_df.loc[filtered_df['Země'] == 'Česká republika']['Percentil']+"", id="un_percentile_value"),
                                                     html.P("Percentil ČR", id="un_percentile_text")],
                                                    id="un_percentile",
                                                    className="mini_container",
                                                ),
                                            ],
                                            className="twelve flex-display",
                                        ),
                                        html.Div(
                                            children=[
                                                html.H4(
                                                    id='top-un-title',
                                                    children='TOP 15 zemí světa v roce ' + str(df['Year'].max())),
                                                html.Div(
                                                    id='top-un-table',
                                                    children=[
                                                        generate_table(filtered_df, 15)
                                                    ], style={'columnCount': 1}),
                                                html.Div(
                                                    children=[
                                                        file_download_link(DATA_UN)
                                                    ]
                                                )
                                            ],
                                            className="pretty_container",
                                        ),
                                    ],
                                    className="three columns right-column",
                                ),
                            ],
                            className="content_holder row twelve columns flex-display"
                        ),
                    ],
                    className="pretty_container_bg twelve columns",
                ),
            ],
            className="row flex-display",
        ),

html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    children=[
                                        html.Img(
                                            src="https://ec.europa.eu/info/sites/info/themes/europa/images/svg/logo/logo--en.svg",
                                            draggable='False',
                                            id="logo_eu",
                                            height='auto',
                                            width=300,
                                        ),
                                        html.Div(
                                            [
                                                html.H3("Index eGovernmentu EU"),
                                                html.P("Index eGovernmentu publikovaný Evropskou unií. Bližší popis metodologie bude přidán v budoucnu.")
                                            ]
                                        )
                                    ],
                                    id="eu_description",
                                    className="pretty_container description twelve columns flex-display"
                                ),
                            ],
                            className="content_holder row twelve columns flex-display"
                        ),
                        html.Div(
                            [
                                html.Div(
                                    children=[
                                        html.Label(
                                            html.H6('Výběr roku')
                                        ),
                                        dcc.Slider(
                                            id='year-slider-2',
                                            min=dfeu['Year'].min(),
                                            max=dfeu['Year'].max(),
                                            value=dfeu['Year'].max(),
                                            marks={
                                                str(year): 'Rok {}'.format(year) if year == df['Year'].min() else str(
                                                    year) for year in
                                                dfeu['Year'].unique()},
                                            step=None,
                                            className='slider'
                                        ),

                                        dcc.Graph(id='europe-map-with-slider',
                                                  figure=generate_europe_map(dfeu, dfeu['Year'].max(), )),

                                    ],
                                    className="pretty_container ten columns",
                                ),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Div(
                                                    [html.H6(str(int(filtered_df_eu.loc[filtered_df_eu['Země'] == 'Česká republika']['Pořadí']))+". místo", id="eu_rank_value"),
                                                     html.P("Pořadí ČR", id="eu_rank_text")],
                                                    id="eu_rank",
                                                    className="mini_container",
                                                ),
                                                html.Div(
                                                    [html.H6(str(np.round(float(filtered_df_eu.loc[filtered_df_eu['Země'] == 'Česká republika']['index eGov EU']),2)), id="eu_score_value"),
                                                     html.P("Skóre ČR", id="eu_score_text")],
                                                    id="eu_score",
                                                    className="mini_container",
                                                ),
                                                html.Div(
                                                    [html.H6(filtered_df_eu.loc[filtered_df_eu['Země'] == 'Česká republika']['Percentil']+"", id="eu_percentile_value"),
                                                     html.P("Percentil ČR", id="eu_percentile_text")],
                                                    id="eu_percentile",
                                                    className="mini_container",
                                                ),
                                            ],
                                            className="twelve flex-display",
                                        ),
                                        html.Div(
                                            children=[
                                                html.H4(
                                                    id='top-eu-title',
                                                    children='TOP 15 zemí EU v roce ' + str(dfeu['Year'].max())),
                                                html.Div(
                                                    id='top-eu-table',
                                                    children=[
                                                        generate_table(filtered_df, 15)
                                                    ], style={'columnCount': 1}),
                                                html.Div(
                                                    children=[
                                                        file_download_link(DATA_EU)
                                                    ]
                                                )
                                            ],
                                            className="pretty_container",
                                        ),
                                    ],
                                    className="three columns right-column",
                                ),
                            ],
                            className="content_holder row twelve columns flex-display"
                        ),
                    ],
                    className="pretty_container_bg twelve columns",
                ),
            ],
            className="row flex-display",
        ),

    ],
    id="mainContainer",
    style={'columnCount': 1, "display": "flex", "flex-direction": "column"},
)

app.title = 'eGovernment benchmark'


@app.callback(
    [Output('world-map-with-slider', 'figure'),
     Output('top-un-title', 'children'),
     Output('top-un-table', 'children'),
     Output('un_rank_value', 'children'),
     Output('un_score_value', 'children'),
     Output('un_percentile_value', 'children')
     ],
    [Input('year-slider', 'value')])
def update_world_map(selected_year):
    filtered_df = pd.DataFrame(df[df.Year == selected_year], columns=['Czech name', 'UN eGov index'])
    filtered_df['Pořadí'] = filtered_df['UN eGov index'].rank(method='max', ascending=False)
    filtered_df['Percentil'] = filtered_df['UN eGov index'].rank(pct=True)
    filtered_df['Percentil'] = (filtered_df['Percentil'] * 100).round(1).astype(str) + '%'
    filtered_df = filtered_df[['Pořadí', 'Czech name', 'UN eGov index', 'Percentil']]
    filtered_df = filtered_df.rename(columns={'Czech name': 'Země','UN eGov index': 'index eGov OSN'})
    return generate_world_map(df, selected_year), \
           'TOP 15 zemí světa v roce ' + str(selected_year), \
           generate_table(filtered_df, 15), \
           str(int(filtered_df.loc[filtered_df['Země'] == 'Česká republika']['Pořadí']))+". místo", \
           str(np.round(float(filtered_df.loc[filtered_df['Země'] == 'Česká republika']['index eGov OSN']),3))+"", \
           filtered_df.loc[filtered_df['Země'] == 'Česká republika']['Percentil']


@app.callback(
    [Output('europe-map-with-slider', 'figure'),
     Output('top-eu-title', 'children'),
     Output('top-eu-table', 'children'),
     Output('eu_rank_value', 'children'),
     Output('eu_score_value', 'children'),
     Output('eu_percentile_value', 'children')],
    [Input('year-slider-2', 'value')])
def update_europe_map(selected_year):
    filtered_df_eu = pd.DataFrame(dfeu[dfeu.Year == selected_year], columns=['Czech name', 'EU eGov index'])
    filtered_df_eu['Pořadí'] = filtered_df_eu['EU eGov index'].rank(method='max', ascending=False)
    filtered_df_eu['Percentil'] = filtered_df_eu['EU eGov index'].rank(pct=True)
    filtered_df_eu['Percentil'] = (filtered_df_eu['Percentil'] * 100).round(1).astype(str) + '%'
    filtered_df_eu = filtered_df_eu[['Pořadí', 'Czech name', 'EU eGov index', 'Percentil']]
    filtered_df_eu = filtered_df_eu.rename(columns={'Czech name': 'Země', 'EU eGov index': 'index eGov EU'})
    filtered_df_eu = filtered_df_eu.sort_values('index eGov EU', ascending=False)
    return generate_europe_map(dfeu, selected_year), \
           'TOP 15 zemí EU v roce ' + str(selected_year), \
           generate_table(filtered_df_eu, 15), \
           str(int(filtered_df_eu.loc[filtered_df_eu['Země'] == 'Česká republika']['Pořadí'])) + ". místo", \
           str(np.round(float(filtered_df_eu.loc[filtered_df_eu['Země'] == 'Česká republika']['index eGov EU']), 2)), \
           filtered_df_eu.loc[filtered_df_eu['Země'] == 'Česká republika']['Percentil']


if __name__ == '__main__':
    app.run_server(debug=True)
