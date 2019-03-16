import datetime
from datetime import datetime as dt

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Output, Input
from pymongo import MongoClient


def _parseTime(date_time_str):
    date_time_obj = datetime.datetime.strptime(date_time_str, '%b %d, %Y')
    return date_time_obj


def convert_data(df):
    df['Date'] = df['Date'].apply(lambda x: _parseTime(x))


Stock_name = ['HNX 30 (HNX30)', 'VN 30 (VNI30)']

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
             max_date_allowed=dt(2019, 3, 15),
             initial_visible_month=dt(2019, 3, 15),
         ),
     ],
         style={'width': '20%', 'display': 'inline-block'}
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

        mng_client = MongoClient()
        mng_db = mng_client['StockDB']
        csvTomongo = 'indicesCollection'
        db_cm = mng_db[csvTomongo]
        df = pd.DataFrame(list(db_cm.find({"name": input_data})))
        return dcc.Graph(
            id='example-graph',
            animate=True,
            figure={
                'data': [
                    {'x': df['time'].values, 'y': df['last'].values, 'type': 'line', 'name': input_data},
                ],
                'layout': {
                    'title': input_data
                }
            }
        )
    except Exception as e:
        with open('errors.txt', 'a') as f:
            f.write(str(e))
            f.write('\n')


if __name__ == '__main__':
    app.run_server(debug=True)
