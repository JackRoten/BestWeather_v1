#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Package to request station data from NOAA
Author: Jack Roten
"""
import requests
import json

from src.constants import contact_info

class Noaadata():
    """
    Requests data from a select list of stations and returns json data
    Must input latitude, longitude and location.
    """

    def __init__(self, latitude, longitude, location):
        self.headers = {"User-Agent": f"(bestweatherwa.com, {contact_info})"}
        self.latitude = latitude
        self.longitude = longitude
        self.location = location
        self.meta_url = None
        self.forecast_url = None
        self.location_json = None
        self.json_data = None

    def meta_constructor(self):
        """
        Takes latitude and longitude, and gets meta data, finding 2.5km grid block for forecast area
        :return:
        """
        self.meta_url = f"https://api.weather.gov/points/{self.latitude},{self.longitude}"
        meta_response = requests.get(url=self.meta_url, headers=self.headers)
        self.location_json = json.loads(meta_response.text)['properties']

    def location_constructor(self):
        """
        Uses meta data from metaconstructor
        :return:
        """
        self.forecast_url = self.location_json['forecastGridData']
        forecast_response = requests.get(url=self.forecast_url, headers=self.headers)
        self.json_data = json.loads(forecast_response.text)

    def get_data(self):
        self.meta_constructor()
        self.location_constructor()
