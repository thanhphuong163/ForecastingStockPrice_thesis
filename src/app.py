from datetime import datetime as dt
from datetime import timezone

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Output, Input, Event
from pymongo import MongoClient

from src.settings import DATABASE, IndColl, INDICES_LST, HOST


def _parseTime(date_time_str):
    date_time_obj = dt.strptime(date_time_str, '%b %d, %Y')
    return date_time_obj

def convert_data(df):
    df['Date'] = df['Date'].apply(lambda x: _parseTime(x))


Stock_name = INDICES_LST

timing = []

external_stylesheets = [
    'https://codepen.io/vantienduclqd/pen/ywZPzG.css',
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    }
]

app = dash.Dash(__name__,
                external_stylesheets=external_stylesheets)
app.layout = html.Div(
    [html.H2('Stock Close Price Graph'),
     html.Div(
         [
             html.Div(
                 [
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
                         end_date=dt(2019, 3, 21),
                         updatemode='bothdates'
                     ),
                     dcc.Interval(
                         id='graph-update',
                         interval=1 * 20000
                     )
                 ],
             )
         ],
         className='selection',
     ),
     html.Div(id='output', style={'width': '60%', 'float': 'right'}),
     ]
)


@app.callback(Output('output', 'children'),
              [Input('input', 'value'),
               Input('my-date-picker-range', 'start_date'),
               Input('my-date-picker-range', 'end_date')],
              events=[Event('graph-update', 'interval')])
def update_graph_scatter(input_data, start_date, end_date):
    try:
        mng_client = MongoClient(HOST)
        mng_db = mng_client[DATABASE]
        db_cm = mng_db[IndColl]

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

        df['time'] = df['time'].apply(lambda x: dt.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'))
        df = df.sort_values(by=['time'])
        df['last'] = df['last'].round(4)
        return dcc.Graph(
            id='example-graph',
            figure={
                'data': [
                    go.Scatter(
                        x=df['time'],
                        y=df['last'],
                        mode='lines',
                        line=dict(color='#4f94c4'),
                        name=input_data,
                        opacity=0.8
                    )
                ],
                'layout': go.Layout(
                    title=input_data,
                    yaxis=dict(title='close price')
                )
            }
        )
    except Exception as e:
        with open('errors.txt', 'a') as f:
            f.write(str(e))
            f.write('\n')


if __name__ == '__main__':
    app.run_server(debug=True)