import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np


def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(
                    np.round(dataframe.iloc[i][col], 2)
                ) if (isinstance(dataframe.iloc[i][col], float)) else (
                    html.Td(
                        dataframe.iloc[i][col]
                    )
                )

                for col in dataframe.columns
            ])
            for i in range(min(len(dataframe), max_rows))
        ])
    ])


def generate_world_map(year):
    df = pd.read_csv('data/eGov-t3.csv')
    filtered_df = df[df.Year == year]

    fig = go.Figure(data=go.Choropleth(
        locations=df['Code'],
        z=filtered_df['UN eGov index'],
        text=df['Czech name'],

        colorscale=[[0.0, "rgb(0,150,50)"],
                    [0.3, "rgb(250,240,110)"],
                    [0.6, "rgb(180,60,50)"],
                    [1.0, "rgb(80,20,80)"]],
        # Note - this fixes min and max points on colorscale to make years comparable
        zmin=0,
        zmax=1,
        autocolorscale=False,
        reversescale=True,
        marker_line_color='darkgray',
        marker_line_width=0.5,
        colorbar_tickprefix='',
        colorbar_title=str(year) + ' index value',
    ))

    fig.update_geos(
        resolution=50
    )

    fig.update_layout(
        height=1000,
        title_text=' eGovernment index OSN z roku ' + str(year),
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='equirectangular'
        ),
        annotations=[dict(
            x=0.59,
            y=0.01,
            xref='paper',
            yref='paper',
            # TODO fix source
            text='Zdroj: <a href="https://publicadministration.un.org/egovkb/">Organizace spojených národů</a>',
            showarrow=False
        )]
    )
    return fig


def generate_europe_map(df, year):
    filtered_df = df[df.Year == year]

    figeu = go.Figure(data=go.Choropleth(
        locations=filtered_df['Code'],
        z=filtered_df['EU eGov index'],
        text=filtered_df['Czech name'],

        colorscale=[[0.0, "rgb(0,150,50)"],
                    [0.3, "rgb(250,240,110)"],
                    [0.6, "rgb(180,60,50)"],
                    [1.0, "rgb(80,20,80)"]],
        # Note - this fixes min and max points on colorscale to make years comparable
        zmin=10,
        zmax=90,
        autocolorscale=False,
        reversescale=True,
        marker_line_color='darkgray',
        marker_line_width=0.5,
        colorbar_tickprefix='',
        colorbar_title=str(year) + ' index value',
    ))

    figeu.update_geos(
        resolution=50,
        fitbounds="locations",
        visible=True,
        scope="europe"
    )

    figeu.update_layout(
        height=1000,
        title_text=' eGovernment index EU z roku ' + str(year),
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='equirectangular'
        ),
        annotations=[dict(
            x=0.59,
            y=0.01,
            xref='paper',
            yref='paper',
            # TODO fix source
            text='Zdroj: <a href="https://ec.europa.eu/newsroom/dae/document.cfm?doc_id=62371">\
                Evropská unie</a>',
            showarrow=False
        )],
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    )
    return figeu


# TODO needs fixing
def generate_correlation(df1, df2):
    df = df1.append(df2)
    fig = px.scatter(df, x="UN eGov index", y="EU eGov index", color="Code", hover_data=['Czech name'])
    return fig