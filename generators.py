import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])


def generate_world_map(year):
    df = pd.read_csv('data/eGov-t3.csv')
    filtered_df = df[df.Year == year]

    fig = go.Figure(data=go.Choropleth(
        locations=df['Code'],
        z=filtered_df['eGov index'],
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
        title_text=str(year) + ' eGovernment index',
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
            text='Source: <a href="https://www.cia.gov/library/publications/the-world-factbook/fields/2195.html">\
                CIA World Factbook</a>',
            showarrow=False
        )]
    )
    return fig


def generate_europe_map(df, year):
    filtered_df = df[df.Year == year]

    figeu = go.Figure(data=go.Choropleth(
        locations=df['Code'],
        z=filtered_df['eGov index'],
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

    figeu.update_geos(
        resolution=50,
        fitbounds="locations",
        visible=True,
        scope="europe"
    )

    figeu.update_layout(
        height=1000,
        title_text=str(year) + ' eGovernment index',
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
            text='Source: <a href="https://www.cia.gov/library/publications/the-world-factbook/fields/2195.html">\
                CIA World Factbook</a>',
            showarrow=False
        )],
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    )
    return figeu
