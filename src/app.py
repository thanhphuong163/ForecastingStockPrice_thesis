from datetime import datetime as dt
from datetime import timezone

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import pymongo
from dash.dependencies import Output, Input, Event, State
from plotly import tools
from pymongo import MongoClient
from settings import DATABASE, IndColl, INDICES_LST, HOST, MockColl, Indice_options


def _parseTime(date_time_str):
    date_time_obj = dt.strptime(date_time_str, '%b %d, %Y')
    return date_time_obj

def convert_data(df):
    df['Date'] = df['Date'].apply(lambda x: _parseTime(x))


# updates hidden div that stores the last clicked menu tab
def generate_active_menu_tab_callback():
    def update_current_tab_name(n_style, n_time):
        if n_style >= n_time:
            return "Style"
        return "Time"

    return update_current_tab_name


# show/hide 'time' menu content
def generate_studies_content_tab_callback():
    def studies_tab(current_tab):
        if current_tab == "Time":
            return {"display": "block", "textAlign": "left", "marginTop": "30"}
        return {"display": "none"}

    return studies_tab


# show/hide 'style' menu content
def generate_style_content_tab_callback():
    def style_tab(current_tab):
        if current_tab == "Style":
            return {"display": "block", "textAlign": "left", "marginTop": "30"}
        return {"display": "none"}

    return style_tab


# updates style of header 'time' in menu
def generate_update_time_header_callback():
    def studies_header(current_tab, old_style):
        if current_tab == "Time":
            old_style["borderBottom"] = "2px solid" + " " + "#45df7e"
        else:
            old_style["borderBottom"] = "2px solid" + " " + "rgba(68,149,209,.9)"
        return old_style

    return studies_header


# updates style of header 'style' in menu
def generate_update_style_header_callback():
    def style_header(current_tab, old_style):
        if current_tab == "Style":
            old_style["borderBottom"] = "2px solid" + " " + "#45df7e"
        else:
            old_style["borderBottom"] = "2px solid" + " " + "rgba(68,149,209,.9)"
        return old_style

    return style_header


# line
def line_trace(df):
    trace = go.Scatter(
        x=df["time"], y=df["close"], mode="lines", showlegend=False, name="line"
    )
    return trace


# candlestick
def candlestick_trace(df):
    return go.Candlestick(
        x=df["time"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        increasing=dict(line=dict(color="#00ff00")),
        decreasing=dict(line=dict(color="white")),
        showlegend=False,
        name="candlestick",
    )

Stock_name = INDICES_LST

timing = []

external_stylesheets = [
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css",
    "https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css",
    "https://cdn.rawgit.com/amadoukane96/8f29daabc5cacb0b7e77707fc1956373/raw/854b1dc5d8b25cd2c36002e1e4f598f5f4ebeee3/test.css",
    "https://use.fontawesome.com/releases/v5.2.0/css/all.css",
    'https://codepen.io/vantienduclqd/pen/eoNYPY.css',
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    }
]

app = dash.Dash(__name__,
                external_stylesheets=external_stylesheets)


# header app
def get_header(t=dt.now()):
    return html.Div(
        [
            html.P(
                "Stock Price Prediction",
                className="six columns",
                style={"color": "white", "textAlign": "center", "fontSize": "18px", "textTransform": "uppercase",
                       "margin": "auto"}
            ),
            html.P(
                t.strftime("%H:%M:%S"),
                id="live_clock",
                className="six columns",
                style={"color": "#45df7e", "textAlign": "center", "margin": "auto"}
            )
        ],
        className="row",
        style={"paddingBottom": "15px", "marginLeft": "10px"}
    )


# color of price
def get_color(a, b):
    if a == b:
        return "white"
    elif a > b:
        return "#45df7e"
    else:
        return "#da5657"


def chart_div():
    return html.Div(
        id='graph_div',
        children=[
            # menu-bar
            html.Div(
                children=[
                    html.Span(
                        "×",
                        id="close_menu",
                        n_clicks=0,
                        style={
                            "fontSize": "16",
                            "float": "right",
                            "paddingRight": "5",
                            "verticalAlign": "textTop",
                            "cursor": "pointer",
                            "color": "white",
                        },
                    ),
                    html.Span(
                        "Style",
                        id="style_header",
                        n_clicks_timestamp=2,
                        style={
                            "top": "0",
                            "float": "left",
                            "marginLeft": "5",
                            "marginRight": "5",
                            "textDecoration": "none",
                            "cursor": "pointer",
                            "color": "white",
                        },
                    ),
                    html.Span(
                        "Time",
                        id="time_header",
                        n_clicks_timestamp=1,
                        style={
                            "float": "left",
                            "textDecoration": "none",
                            "cursor": "pointer",
                            "color": "white",
                        },
                    ),
                    html.Div(
                        html.Div(
                            dcc.RadioItems(
                                id="chart_type",
                                options=[
                                    {"label": "candlestick", "value": "candlestick_trace"},
                                    {"label": "line", "value": "line_trace"},
                                ],
                                value="line_trace",
                            ),
                            id="type_tab",
                            style={"marginTop": "30", "textAlign": "left"},
                        )
                    ),
                    html.Div(
                        html.Div(
                            dcc.RadioItems(
                                id="timing",
                                options=[
                                    {"label": "1 day"},
                                    {"label": "1 week"},
                                    {"label": "1 month"},
                                    {"label": "1 year"},
                                    {"label": "all"},
                                ],
                                value="all",
                            ),
                            id="timing_tab",
                            style={"marginTop": "30", "textAlign": "left"},
                        ),
                    ),
                ],
                id="menu",
                className="not_visible",
                style={
                    "overflow": "auto",
                    "borderRight": "1px solid" + "rgba(68,149,209,.9)",
                    "backgroundImage": "-webkit-linear-gradient(top,#18252e,#2a516e 63%)",
                    "zIndex": "20",
                    "width": "45%",
                    "height": "100%",
                    "position": "absolute",
                    "left": "0",
                    "top": "27px",
                },
            ),
            html.Div(
                [
                    html.Span(
                        "Chart ",
                        style={"float": "left", "marginRight": "5px", "color": "white"},
                    ),
                    html.Span(
                        "☰",
                        n_clicks=0,
                        id="menu_button",
                        style={"float": "left", "color": "white", "cursor": "pointer"},
                    ),
                ],
                className="row",
                style={
                    "padding": "3",
                    "height": "20px",
                    "margin": "0 0 5 0",
                    "backgroundImage": "-webkit-linear-gradient(top,#18252e,#2a516e 63%)",
                },
            ),

            # Graph div
            html.Div(id='output'),
        ],
    )

app.layout = html.Div(
    [
        dcc.Interval(id="interval", interval=1 * 1000, n_intervals=0),
        html.Div(
            [
                get_header(),
                html.Div(
                    [
                        dcc.Dropdown(
                            id='input',
                            options=[{'label': i, 'value': i} for i in Indice_options.keys()],
                            value='VN 30 (VNI30)'
                        ),
                        dcc.Dropdown(
                            id='indice-component',
                        ),
                        dcc.DatePickerRange(
                            id='my-date-picker-range',
                            min_date_allowed=dt(1995, 8, 5),
                            max_date_allowed=dt.now(),
                            initial_visible_month=dt(2019, 3, 1),
                            end_date=dt(2019, 3, 21),
                            updatemode='bothdates'
                        ),
                        html.Div(
                            id='indice-information',
                        ),
                        dcc.Interval(
                            id='graph-update',
                            interval=1 * 20000
                        )
                    ],
                )
            ],
            style={"backgroundColor": "#18252e", "padding": "20px"},
            className='three columns selection',
        ),
        html.Div(
            [chart_div()],
            style={"height": "70%", "margin": "0px 5px", "float": "right"},
            id="charts",
            className="nine columns",
        ),
        # html.Div(id='output', className='nine columns', style={'float': 'right'}),
    ],
    style={"paddingTop": "15px", "backgroundColor": "#1a2d46", "height": "100vh"}
)


# open close menu
@app.callback(
    Output("menu", "className"),
    [Input("menu_button", "n_clicks"),
     Input("close_menu", "n_clicks")],
    [State("menu", "className")],
)
def open_closeMenu(n, n2, className):
    if n == 0:
        return "not_visible"
    if className == "visible":
        return "not_visible"
    else:
        return "visible"


#set live clock
@app.callback(Output("live_clock", "children"), [Input("interval", "n_intervals")])
def update_time(t):
    return dt.now().strftime("%H:%M:%S")


@app.callback((Output("indice-component", "options")), [Input("input", "value")])
def set_indice_options(selected_indice):
    return [{'label': i, 'value': i} for i in Indice_options[selected_indice]]


# @app.callback()

#indice information
@app.callback((Output("indice-information", "children")), [Input("input", "value")])
def get_indice_informations(selected_indice):
    mng_client = MongoClient(HOST)
    mng_db = mng_client[DATABASE]
    db_cm_ind = mng_db[IndColl]
    df_ind = pd.DataFrame(list(db_cm_ind.find({"name": selected_indice}).sort("time", pymongo.DESCENDING).limit(2)))
    df_ind['time'] = df_ind['time'].apply(lambda x: dt.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'))
    last_price = str(df_ind['last'].values[0].round(2))
    return html.Div([
        html.P(
            selected_indice,
            style={"color": "white", "textAlign": "left", "fontSize": "25px", "textTransform": "uppercase", }
        ),
        html.Div(
            [
                html.P(
                    "date time",
                    className="four columns",
                    style={"color": "white", "textAlign": "center", "fontSize": "10px", "textTransform": "uppercase",
                           "margin": "auto"}
                ),
                html.P(
                    "close price",
                    className="four columns",
                    style={"color": "white", "textAlign": "center", "fontSize": "10px", "textTransform": "uppercase",
                           "margin": "auto"}
                ),
                html.P(
                    "volume",
                    className="four columns",
                    style={"color": "white", "textAlign": "center", "fontSize": "10px", "textTransform": "uppercase",
                           "margin": "auto"}
                ),
            ],
        ),
        html.Div(
            [
                html.P(
                    df_ind['time'].values[0],
                    className="four columns",
                    style={"color": "white", "textAlign": "center", "fontSize": "10px", "textTransform": "uppercase",
                           "margin": "auto"}
                ),
                html.P(
                    last_price,
                    className="four columns",
                    style={"color": get_color(df_ind['last'].values[0], df_ind['last'].values[1]),
                           "textAlign": "center", "fontSize": "10px", "textTransform": "uppercase",
                           "margin": "auto"}
                ),
                html.P(
                    df_ind['volume'].values[0],
                    className="four columns",
                    style={"color": "white", "textAlign": "center", "fontSize": "10px", "textTransform": "uppercase",
                           "margin": "auto"}
                ),
            ],
        ),
    ],
        style={"backgroundColor": "#18252e", "padding": "20px", "margin-top": "20px"},
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
                        {},
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
                {}
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
        rows = 1
        figure = tools.make_subplots(rows=rows,
                                     cols=2,
                                     shared_yaxes=True,
                                     print_grid=False)

        figure.append_trace(trace_ind, 1, 1)
        figure.append_trace(trace_mock, 1, 2)
        figure['layout']["margin"] = {"b": 50, "r": 5, "l": 50, "t": 5}
        figure['layout'].update(title=input_data, paper_bgcolor="#18252E", plot_bgcolor="#18252E")

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