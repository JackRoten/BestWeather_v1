#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

def create_sql_db(df):
    conn = sqlite3.connect('../data/forecast.sqlite')
    df.to_sql('locations_forecast', conn, if_exists='replace')

def update_table(df):
    conn = sqlite3.connect('../data/forecast.sqlite')
# more operations may need to live here to optimize the database's layout, and operations
# create a cron job to update the table every hour :)
