from datetime import datetime as dt
from datetime import timezone

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Output, Input, Event
from plotly import tools
from pymongo import MongoClient

from src.settings import DATABASE, IndColl, INDICES_LST, HOST, MockColl


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
                         value='VN 30 (VNI30)'
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
        db_cm_ind = mng_db[IndColl]
        db_cm_mock = mng_db[MockColl]

        if start_date is not None:
            start_date = dt.strptime(start_date, '%Y-%m-%d')
            start_date = float(start_date.replace(tzinfo=timezone.utc).timestamp())
        if end_date is not None:
            end_date = dt.strptime(end_date, '%Y-%m-%d')
            end_date = float(end_date.replace(tzinfo=timezone.utc).timestamp())

        if start_date is not None and end_date is not None:
            df_mock = pd.DataFrame(list(db_cm_mock.find(
                {
                    "$and": [
                        {
                            # "name": input_data
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
            df_mock = pd.DataFrame(list(db_cm_mock.find(
                {
                    # "name": input_data
                }
            )))

        df_ind = pd.DataFrame(list(db_cm_ind.find(
            {
                "name": input_data
            }
        )))
        df_mock = df_mock.rename(columns=lambda x: x.strip())
        df_mock['time'] = df_mock['time'].apply(lambda x: dt.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'))
        df_ind['time'] = df_ind['time'].apply(lambda x: dt.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'))

        df_mock = df_mock.sort_values(by=['time'])
        df_ind = df_ind.sort_values(by=['time'])
        df_mock['last'] = df_mock['last'].round(4)
        df_ind['last'] = df_ind['last'].round(4)

        trace_ind = go.Scatter(
            x=df_ind['time'],
            y=df_ind['last'],
            mode='lines',
            line=dict(color='#28a745'),
            name=input_data,
            # opacity=0.8
        )

        trace_mock = go.Scatter(
            x=df_mock['time'],
            y=df_mock['last'],
            mode='lines',
            line=dict(color='#4f94c4'),
            name=input_data,
            opacity=0.8
        )

        figure = tools.make_subplots(rows=1,
                                     cols=2,
                                     shared_yaxes=True,
                                     print_grid=False)

        figure.append_trace(trace_ind, 1, 1)
        figure.append_trace(trace_mock, 1, 2)
        figure['layout'].update(title=input_data)

        return dcc.Graph(
            id='example-graph',
            figure=figure
        )
    except Exception as e:
        with open('errors.txt', 'a') as f:
            f.write(str(e))
            f.write('\n')


if __name__ == '__main__':
    app.run_server(debug=True)