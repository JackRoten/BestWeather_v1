#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main executable for BestWeather app
Goal: find the best hiking/skiing locations in Washington based on quality of weather
"""

from src.ForecastTable import build_table

def main():
    # 1 get list of coordinates and locations from csv in data allow for two
    # columns as such: "coordinates": "47.299263,-121.287287" and "location":"Cabin Creek"

    # TODO: Create something like a sql table or maybe a json table for the formatted information
    # TODO: question: how to integrage with wordpress page
    # TODO: what information will we want to display?
    # TODO: create sql table, with data amassed, and create a ranking algorithm


    # Cron as an hourly operation, updating a sql table, then cron a table_view

    # first try displaying data as a dashboard with dash!
    df = build_table()
    df.to_csv("../data/forecast_data.csv", index=False)
    # 2 construct dataframes for several locations

    # 2.1 for each row in that list use Forecaster
    # to get weather data json for each area and output json data that
    # picks out temp, precip, wind speed, wind, direction

    # 3 Using database have a refreshing/updating django app that displays a table
    # of this data



if __name__ == "__main__":
    main()