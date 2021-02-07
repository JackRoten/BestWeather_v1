#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Create a dashboard
import dash
import dash_html_components as html
import dash_table
import pandas as pd
import urllib
from dash.dependencies import Input, Output, State
import sqlite3

def read_sql_db():
    conn = sqlite3.connect('../data/forecast.sqlite')
    df = pd.read_sql("select * from locations_forecast", conn)
    return df


df = read_sql_db()
#instantiate the dash app
app = dash.Dash(__name__)
PAGE_SIZE = 200

#build the app layout
app.layout = html.Div([
    html.H1("Forecast Data"),
    html.P(''),
    html.P('Filter and sort the data, then export as needed.'),
    html.P(''),
    dash_table.DataTable(
    id='table-sorting-filtering',
    style_data={
        'whiteSpace': 'normal',
        'height': 'auto'
    },
    style_table={
        'maxHeight': '800px'
        ,'overflowY': 'scroll'
    },
    columns=[
        {'name': i, 'id': i} for i in df.columns
    ],
    page_current= 0,
    page_size= PAGE_SIZE,
    page_action='custom',
    filter_action='custom',
    filter_query='',
    sort_action='custom',
    sort_mode='multi',
    sort_by=[]
)
, html.Div([ html.P(' ')
    ,html.A('Download CSV', id='my-link', download="data.csv",
            href="",
            target="_blank")])
])

# end div
#list of operators for data table query
operators = [['ge ', '>='],
             ['le ', '<='],
             ['lt ', '<'],
             ['gt ', '>'],
             ['ne ', '!='],
             ['eq ', '='],
             ['contains '],
             ['datestartswith ']]

def split_filter_part(filter_part):
    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find('{') + 1: name_part.rfind('}')]
                value_part = value_part.strip()
                v0 = value_part[0]
                if v0 == value_part[-1] and v0 in ("'", '"', '`'):
                    value = value_part[1: -1].replace('\\' + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part
                # word operators need spaces after them in the filter string,
                # but we don't want these later
                return name, operator_type[0].strip(), value
    return [None] * 3

#call back to sort and filter data table
@app.callback(
    Output('table-sorting-filtering', 'data'),
    [Input('table-sorting-filtering', "page_current"),
     Input('table-sorting-filtering', "page_size"),
     Input('table-sorting-filtering', 'sort_by'),
     Input('table-sorting-filtering', 'filter_query')])

def update_table(page_current, page_size, sort_by, filter):
    filtering_expressions = filter.split(' && ')
    dff = df
    for filter_part in filtering_expressions:
        col_name, operator, filter_value = split_filter_part(filter_part)
        if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
            # these operators match pandas series operator method names
            dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
        elif operator == 'contains':
            dff = dff.loc[dff[col_name].str.contains(filter_value)]
        elif operator == 'datestartswith':
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            dff = dff.loc[dff[col_name].str.startswith(filter_value)]
    if len(sort_by):
        dff = dff.sort_values(
            [col['column_id'] for col in sort_by],
            ascending=[
                col['direction'] == 'asc'
                for col in sort_by
            ],
            inplace=False
        )
    page = page_current
    size = page_size
    return dff.iloc[page * size: (page + 1) * size].to_dict('records')

#callback to filter and sort data for export link
@app.callback(Output('my-link', 'href')
            , [Input('table-sorting-filtering', "page_current"),
     Input('table-sorting-filtering', "page_size"),
     Input('table-sorting-filtering', 'sort_by'),
     Input('table-sorting-filtering', 'filter_query')])

def update_table2(page_current, page_size, sort_by, filter):
    filtering_expressions = filter.split(' && ')
    dff = df
    for filter_part in filtering_expressions:
        col_name, operator, filter_value = split_filter_part(filter_part)
        if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
            # these operators match pandas series operator method names
            dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
        elif operator == 'contains':
            dff = dff.loc[dff[col_name].str.contains(filter_value)]
        elif operator == 'datestartswith':
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            dff = dff.loc[dff[col_name].str.startswith(filter_value)]
    if len(sort_by):
            dff = dff.sort_values(
            [col['column_id'] for col in sort_by],
            ascending=[
                col['direction'] == 'asc'
                for col in sort_by
            ],
            inplace=False
        )
    csv_string = dff.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8,%EF%BB%BF" + urllib.parse.quote(csv_string)
    return csv_string

#used for instantiating the app
if __name__ == '__main__':
    app.run_server(debug=True)
