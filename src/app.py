from collections import deque
from datetime import datetime as dt
from datetime import timezone

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Output, Input
from pymongo import MongoClient

from src.settings import DATABASE, IndColl, INDICES_LST, HOST


def _parseTime(date_time_str):
    date_time_obj = dt.strptime(date_time_str, '%b %d, %Y')
    return date_time_obj

def convert_data(df):
    df['Date'] = df['Date'].apply(lambda x: _parseTime(x))


Stock_name = INDICES_LST

timing = deque()

app = dash.Dash()
app.layout = html.Div(
    [html.H2('Stock Close Price Graph'),
     html.Div([
         dcc.Dropdown(
             id='input',
             options=[{'label': i, 'value': i} for i in Stock_name],
             value='HNX 30 (HNX30)'
         ),
         dcc.DatePickerRange(
             id='my-date-picker-range',
             min_date_allowed=dt(1995, 8, 5),
             max_date_allowed=dt.now(),
             initial_visible_month=dt(2019, 3, 1),
             start_date=dt(2017, 1, 1),
             end_date=dt(2019, 3, 21),
             updatemode='bothdates'
         )
     ],
         style={'width': '20%', }
     ),
     html.Div(id='output', style={'width': '80%', 'float': 'right'}),
     ]
)


@app.callback(Output('output', 'children'),
              [Input('input', 'value'),
               Input('my-date-picker-range', 'start_date'),
               Input('my-date-picker-range', 'end_date')])
def update_graph_scatter(input_data, start_date, end_date):
    try:
        mng_client = MongoClient(HOST)
        mng_db = mng_client[DATABASE]
        db_cm = mng_db[IndColl]
        test = dt(2017, 8, 25, 23, 59)

        if start_date is not None:
            start_date = dt.strptime(start_date, '%Y-%m-%d')
            start_date = float(start_date.replace(tzinfo=timezone.utc).timestamp())
        if end_date is not None:
            end_date = dt.strptime(end_date, '%Y-%m-%d')
            end_date = float(end_date.replace(tzinfo=timezone.utc).timestamp())

        if start_date is not None and end_date is not None:
            df = pd.DataFrame(list(db_cm.find(
                {
                    "$and": [
                        {
                            "name": input_data
                        },
                        {
                            "time":
                                {
                                    "$gt": start_date,
                                    "$lt": end_date
                                },
                        }
                    ]
                })))
        else:
            df = pd.DataFrame(list(db_cm.find({"name": input_data})))

        for unix_ts in df['time']:
            ts = int(unix_ts)
            timing.append(dt.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))
        return dcc.Graph(
            id='example-graph',
            figure={
                'data': [
                    go.Scatter(
                        x=list(timing),
                        y=df['last'],
                        mode='lines+markers',
                        line=dict(color='rgb(114, 186, 59)'),
                        name=input_data
                    )
                ],
                'layout': go.Layout(
                    title=input_data
                )
            }
        )
    except Exception as e:
        with open('errors.txt', 'a') as f:
            f.write(str(e))
            f.write('\n')


if __name__ == '__main__':
    app.run_server(debug=True)