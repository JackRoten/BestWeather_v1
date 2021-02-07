#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Produces formatted table from Noaa Forecast data
"""
# Standard Libraries
import logging

# Community Packages
import pandas as pd


# Local Packages
from src.Location import Locations
from src.NoaaData import Noaadata
from src.constants import constant_columns

logging.basicConfig(
    level=logging.INFO,
    style='{',
    format='{asctime} | {levelname:<8s} | {name}:{lineno:5} | {message}'
)

class TableCreator():
    """
    Constructs Table for a single location
    """
    # TODO: Add missing information method that says which column and which time period
    def __init__(self):
        self.location = None
        self.json_data = None
        self.df = pd.DataFrame()
        self.temp_cols = pd.DataFrame()
        self.constant_columns = constant_columns

    def construct_table(self):
        for col_name in self.constant_columns:
            self.temp_cols = col_construct(self.json_data, col_name)
            if col_name == 'windSpeed':
                self.df = self.temp_cols.validTime.to_frame()
            self.df = pd.merge(self.df, self.temp_cols, on=['validTime'], how='left')
        self.df['location'] = self.location

def col_construct(json_data, column_name):
    """
    :param json_data: data from a call
    :param column_name: the values we want to flaten to single daily avged column
    columns = 'windSpeed', 'windGust', 'windDirection', 'snowfallAmount', 'temperature'
    :return: two column dataframe with validTime and temperature columns

    """
    col_values = json_data['properties'][column_name]['values']
    df = pd.json_normalize(col_values)
    # TODO: extract to datetime and filter out information for just the day
    df.validTime = df.validTime.str.extractall(r'(\d{4})-(\d{2})-(\d{2})').unstack().apply(lambda x: '-'.join(x.dropna()), axis=1)
    df.validTime = pd.to_datetime(df.validTime)
    df[column_name] = df.value
    df.drop(columns='value', inplace=True)
    df.fillna(0, inplace=True)
    # TODO: Groupby time periods attribured to days for greater drill down
    try:
        if column_name == 'temperature':
            df = temp_formatter(df)
        elif column_name == 'minTemperature':
            df = mintemp_formatter(df)
        elif column_name == 'maxTemperature':
            df = maxtemp_formatter(df)
        elif column_name == 'windSpeed':
            df = wind_speed_formatter(df)
        elif column_name == 'windSpeed':
            df = wind_speed_formatter(df)
        elif column_name == 'windGust':
            df = wind_gust_formatter(df)
        elif column_name == 'snowfallAmount':
            df = snowfall_formatter(df)
        elif column_name == 'windDirection':
            df = wind_direction_formatter(df)
        elif column_name == 'probabilityOfPrecipitation':
            df = precip_formatter(df)
        elif column_name == 'relativeHumidity':
            df = humid_formatter(df)
        elif column_name == 'skyCover':
            df = skycover_formatter(df)
        df[column_name] = df[column_name].round(2)
    except KeyError:
        pass
    return df

def location_formatter(locations, index):
    lat = locations.df.iloc[index][0].split(',')[0]
    long = locations.df.iloc[index][0].split(',')[1]
    name = locations.df.iloc[index][1]
    return lat, long, name

def temp_formatter(df):
    """
    Temp comes in Deg C. Format to Deg F and output min and max cols
    """
    df['temperature'] = df['temperature']*(9/5)+32
    df = df.groupby(['validTime'], as_index=False).mean()
    return df

def mintemp_formatter(df):
    df['minTemperature'] = df['minTemperature'] * (9 / 5) + 32
    df = df.groupby(['validTime'], as_index=False).mean()
    return df

def maxtemp_formatter(df):
    df['maxTemperature'] = df['maxTemperature'] * (9 / 5) + 32
    df = df.groupby(['validTime'], as_index=False).mean()
    return df

def wind_speed_formatter(df):
    # TODO: convert to reasonable unit
    df = df.groupby(['validTime'], as_index=False).mean()
    return df

def wind_gust_formatter(df):
    # TODO: convert to reasonable unit
    df = df.groupby(['validTime'], as_index=False).max()
    return df

def snowfall_formatter(df):
    # TODO: groupby something else, this is returning a huge number, might need to be a time-weighted average or something
    # TODO: resource:: https://journals.ametsoc.org/view/journals/mwre/147/3/mwr-d-18-0273.1.xml?tab_body=fulltext-display
    # in mm, convert to inches
    df['snowfallAmount'] = df['snowfallAmount']*0.0393701
    df = df.groupby(['validTime'], as_index=False).mean()
    return df

def wind_direction_formatter(df):
    # TODO: give more meaning to this unit
    df = df.groupby(['validTime'], as_index=False).mean()
    return df

def precip_formatter(df):
    df = df.groupby(['validTime'], as_index=False).mean()
    return df

def humid_formatter(df):
    df = df.groupby(['validTime'], as_index=False).mean()
    return df

def skycover_formatter(df):
    df = df.groupby(['validTime'], as_index=False).mean()
    return df

def build_table():
    result_df = pd.DataFrame()
    locations = Locations()
    for index in range(len(locations.df)):
        lat, long, name = location_formatter(locations, index)
        noaaData = Noaadata(lat, long, name)
        noaaData.get_data()
        logging.info(f"NOAA data for {name} found")
        table = TableCreator()
        table.json_data = noaaData.json_data
        table.constant_columns = constant_columns
        table.location = name
        table.construct_table()
        result_df = result_df.append(table.df, ignore_index=True)
        days = 5
        cutoff_date = result_df.validTime.iloc[0] + pd.Timedelta(days=days)
        result_df = result_df[(result_df.validTime < cutoff_date) & (result_df.validTime >= result_df.validTime.iloc[0])]
    logging.info(f"dataframe of length: {len(result_df)}")
    return result_df



