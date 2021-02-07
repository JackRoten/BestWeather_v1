#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Produces location dataframe from .csv file
"""
import os
import pandas as pd

class Locations():
    def __init__(self):
        self.location_path = os.path.realpath('../data/locations.csv')
        self.df = pd.read_csv(self.location_path)
        self.columns = self.df.columns




