import pytest
import dash_html_components as html
import pandas as pd

from generators import generate_table, generate_europe_map, generate_world_map

df = pd.read_csv('data/eGov-t3.csv')

filtered_df = pd.DataFrame(df[df.Year == 2018], columns=['Czech name', 'eGov index']).reset_index()


# checks if the generate table function raises an exception when passed something else than a dataframe
@pytest.mark.parametrize(
    "dataframe,max_rows",
    [
        (filtered_df, 10),
        ("not a dataframe", "hoho")
    ])
def test_func_table(dataframe, max_rows):
    if isinstance(dataframe, pd.DataFrame):
        try:
            generate_table(dataframe, 10)
            assert True
        except Exception:
            assert False
    else:
        try:
            generate_table(dataframe, 10)
            assert False
        except Exception:
            assert True


# checks if the generate worldmap function raises an exception when passed something else than a valid year
@pytest.mark.parametrize(
    "year",
    [
        (2018),
        ("not a year"),
    ])
def test_func_worldmap(year):
    if isinstance(year, int):
        try:
            generate_world_map(year)
            assert True
        except Exception:
            assert False
    else:
        try:
            generate_world_map(year)
            assert False
        except Exception:
            assert True


# checks if the generate europemap function raises an exception when passed something else than a dataframe
@pytest.mark.parametrize(
    "dataframe,max_rows",
    [
        (df, 2018),
        ("not a dataframe", "hoho")
    ])
def test_func_euromap(dataframe, max_rows):
    if isinstance(dataframe, pd.DataFrame):
        try:
            generate_europe_map(dataframe, 10)
            assert True
        except Exception:
            assert False
    else:
        try:
            generate_europe_map(dataframe, 10)
            assert False
        except Exception:
            assert True
