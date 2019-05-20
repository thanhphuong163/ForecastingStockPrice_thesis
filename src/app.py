from datetime import datetime as dt

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import pymongo
from dash.dependencies import Output, Input, Event, State
from plotly import tools
from pymongo import MongoClient

from src.query_data import QueryData
from src.settings import DATABASE, IndColl, INDICES_LST, HOST, Indice_options, History_data, CompoColl
from src.utilities import calculate_acf, calculate_pacf

Stock_name = INDICES_LST

timing = [

]

model = ["ARIMA", "CNN", "HYBRID", "LSTM"]

def _parseTime(date_time_str):
    date_time_obj = dt.strptime(date_time_str, '%b %d, %Y')
    return date_time_obj

def convert_data(df):
    df['Date'] = df['Date'].apply(lambda x: _parseTime(x))


#######STUDIES TRACES######

# Moving average
def moving_average_trace(df, fig):
    price = df['close'].rolling(window=5).mean()
    trace = go.Scatter(
        x=df['date'], y=price, mode="lines", showlegend=False, name="MA"
    )
    fig.append_trace(trace, 1, 1)  # plot in first row
    return fig


# Exponential moving average
def e_moving_average_trace(df, fig):
    price = df['close'].rolling(window=20).mean()
    trace = go.Scatter(
        x=df['date'], y=price, mode="lines", showlegend=False, name="EMA"
    )
    fig.append_trace(trace, 1, 1)  # plot in first row
    return fig


# Bollinger Bands
def bollinger_trace(df, fig, window_size=10, num_of_std=5):
    price = df["close"]
    rolling_mean = price.rolling(window=window_size).mean()
    rolling_std = price.rolling(window=window_size).std()
    upper_band = rolling_mean + (rolling_std * num_of_std)
    lower_band = rolling_mean - (rolling_std * num_of_std)

    trace = go.Scatter(
        x=df["date"], y=upper_band, mode="lines", showlegend=False, name="BB_upper", line=dict(color='#a2a2a2'),
        opacity=0.5
    )

    trace2 = go.Scatter(
        x=df["date"], y=rolling_mean, mode="lines", showlegend=False, name="BB_mean", opacity=0.5
    )

    trace3 = go.Scatter(
        x=df["date"], y=lower_band, mode="lines", showlegend=False, name="BB_lower", line=dict(color='#a2a2a2'),
        opacity=0.5
    )

    fig.append_trace(trace, 1, 1)  # plot in first row
    fig.append_trace(trace2, 1, 1)  # plot in first row
    fig.append_trace(trace3, 1, 1)  # plot in first row
    return fig


# Pivot points
def pp_trace(df, fig):
    PP = pd.Series((df["high"] + df["low"] + df["close"]) / 3)
    R1 = pd.Series(2 * PP - df["low"])
    S1 = pd.Series(2 * PP - df["high"])
    R2 = pd.Series(PP + df["high"] - df["low"])
    S2 = pd.Series(PP - df["high"] + df["low"])
    R3 = pd.Series(df["high"] + 2 * (PP - df["low"]))
    S3 = pd.Series(df["low"] - 2 * (df["high"] - PP))
    trace = go.Scatter(x=df.index, y=PP, mode="lines", showlegend=False, name="PP")
    trace1 = go.Scatter(x=df.index, y=R1, mode="lines", showlegend=False, name="R1")
    trace2 = go.Scatter(x=df.index, y=S1, mode="lines", showlegend=False, name="S1")
    trace3 = go.Scatter(x=df.index, y=R2, mode="lines", showlegend=False, name="R2")
    trace4 = go.Scatter(x=df.index, y=S2, mode="lines", showlegend=False, name="S2")
    trace5 = go.Scatter(x=df.index, y=R3, mode="lines", showlegend=False, name="R3")
    trace6 = go.Scatter(x=df.index, y=S3, mode="lines", showlegend=False, name="S3")
    fig.append_trace(trace, 1, 1)
    fig.append_trace(trace1, 1, 1)
    fig.append_trace(trace2, 1, 1)
    fig.append_trace(trace3, 1, 1)
    fig.append_trace(trace4, 1, 1)
    fig.append_trace(trace5, 1, 1)
    fig.append_trace(trace6, 1, 1)
    return fig

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


# open modal
def generate_modal_open_callback():
    def open_modal(n):
        if n > 0:
            return {"display": "block"}
        else:
            return {"display": "none"}

    return open_modal


# close modal
def generate_modal_close_callback():
    def close_modal(n, n2):
        return 0

    return close_modal

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

app.config['suppress_callback_exceptions'] = True

# CSS
tabs_styles = {
    'height': '44px'
}
tab_style = {
    'padding': '6px',
    'color': 'white',
    'backgroundColor': 'rgb(24, 37, 46)',
    'border': 'none'
}

tab_selected_style = {
    'borderBottom': '2px solid gold',
    'color': 'white',
    'padding': '6px',
    'fontWeight': 'bold',
    'backgroundColor': 'rgb(24, 37, 46)',
    'borderTop': 'none',
    'borderLeft': 'none',
    'borderRight': 'none'
}

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
            dcc.Interval(id="interval1", interval=1 * 1000, n_intervals=0),
            html.Div(
                children=[
                    html.Div(
                        "Style", id="menu_tab", style={"display": "none"}
                    ),
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
                            "padding": "4px"
                        },
                    ),
                    html.Span(
                        "Studies",
                        id="time_header",
                        n_clicks_timestamp=1,
                        style={
                            "float": "left",
                            "textDecoration": "none",
                            "cursor": "pointer",
                            "color": "white",
                            "padding": "4px"
                        },
                    ),
                    html.Div(
                        dcc.RadioItems(
                            id="chart_type",
                            options=[
                                {"label": "candlestick", "value": "candlestick_trace"},
                                {"label": "line", "value": "line_trace"},
                                {"label": "mountain", "value": "mountain_trace"}
                            ],
                            value="line_trace",
                            style={"color": "white", "marginTop": "30px", },
                            labelStyle={'display': 'block'}
                        ),
                        id="type_tab",
                        style={"textAlign": "left", "display": "block", 'marginLeft': '2px'},
                    ),
                    html.Div(
                        dcc.Checklist(
                            id="timing",
                            options=[
                                {'label': 'Bollinger bands', 'value': 'bollinger_trace'},
                                {'label': 'MA', 'value': 'moving_average_trace'},
                                # {'label': 'Pivot points', 'value': 'pp_trace'},
                                {"label": "EMA", "value": "e_moving_average_trace"},
                            ],
                            values=[],
                            style={"color": "white", "marginTop": "30px", },
                            labelStyle={'display': 'block', 'marginLeft': '2px'}
                        ),
                        id="timing_tab",
                        style={"textAlign": "left", "display": "block"},
                    ),
                ],
                id="menu",
                className="not_visible ",
                style={
                    "overflow": "auto",
                    "borderRight": "1px solid" + "rgba(68,149,209,.9)",
                    "backgroundImage": "-webkit-linear-gradient(top,#18252e,#2a516e 63%)",
                    "zIndex": "20",
                    "width": "25%",
                    "height": "45%",
                    "position": "absolute",
                    "left": "0",
                    "top": "20px",
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
                    "paddingLeft": "20px",
                    "height": "20px",
                    "margin": "0 0 5 0",
                    "backgroundImage": "-webkit-linear-gradient(top,#18252e,#2a516e 63%)",
                },
            ),

            # Graph div
            html.Div(
                id='output',
            ),
        ],
        style={
            "position": "relative",
            "border": "1px solid",
            "borderColor": "rgba(68,149,209,.9)",
            "overflow": "hidden",
            "marginBottom": "2px",
            "height": "600px"
        }
    )


# modal
def modal():
    return html.Div(
        [
            html.Div(
                [
                html.Div(
                    [
                        html.Span(
                            "x",
                            id="closeModal",
                            n_clicks=0,
                            style={
                                "float": "right",
                                "cursor": "pointer",
                                "marginTop": "0",
                                "marginBottom": "10",
                                "position": "relative",
                                "left": "730px",
                                "bottom": "22px",
                            }
                        ),

                        dcc.Tabs(id="tabs", value='tab-analyze', children=[
                            dcc.Tab(label='ANALYZE', value='tab-analyze', style=tab_style,
                                    selected_style=tab_selected_style),
                            dcc.Tab(label='PREDICT', value='tab-predict', style=tab_style,
                                    selected_style=tab_selected_style),
                        ]),
                        html.Div(id='tabs-content', style={'marginTop': '15px'}),
                        html.Div(
                            [
                                html.Button(
                                    "Analyze",
                                    id="analyze_button",
                                    n_clicks=0,
                                    style={
                                        "borderRadius": "10px",
                                        "marginRight": "20px"
                                    }
                                ),
                                html.Button(
                                    "Close",
                                    id="accept",
                                    n_clicks=0,
                                    style={
                                        "borderRadius": "10px"
                                    }
                                ),
                            ],
                            style={"textAlign": "left", "margin": "auto", "marginTop": "20px"}
                        ),
                    ],
                    className="modal-content",
                    style={
                        "backgroundColor": "#18252E",
                        "width": "50%",
                        "border": "3px solid rgba(68,149,209,.9)",
                        "borderRadius": "10px",
                        "padding": "20px",
                        "margin": "5% auto",
                        "position": "fixed",
                        "zIndex": "1000",
                        "left": "0",
                        "right": "0"

                    }
                )
            ],
            )
        ],
        id="modal_div",
        className="modal",
        style={"display": "none", "backgroundColor": "#18252E"}
    )

app.layout = html.Div(
    [
        dcc.Interval(id="interval", interval=1 * 1000, n_intervals=0),

        html.Div(
            [
                html.Div(
                    [
                        get_header(),
                        html.Div(
                            [
                                dcc.Dropdown(
                                    id='input',
                                    options=[{'label': i, 'value': i} for i in Indice_options.keys()],
	                                value='VN 30 (VNI30)',
	                                style={"color": "white"}
                                ),
                                dcc.Dropdown(
                                    id='indice-component',
                                ),
                                # dcc.DatePickerRange(
                                #     id='my-date-picker-range',
                                #     min_date_allowed=dt(1995, 8, 5),
                                #     max_date_allowed=dt.now(),
                                #     initial_visible_month=dt(2019, 3, 1),
                                #     end_date=dt(2019, 3, 21),
                                #     updatemode='bothdates'
                                # ),
                                html.Div(
                                    id='indice-information',
                                ),
                                html.Div(
                                    id='component-information',
                                ),
                                dcc.Interval(
                                    id='graph-update',
                                    interval=1 * 20000
                                )
                            ],
                        ),
                    ],
                    style={"float": "left", "backgroundColor": "#18252e", "padding": "20px",
                           "border": "1px solid rgba(68, 149, 209, 0.9)", "width": "312px"},
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Button(
                                    "Update database",
                                    id="button_chart_crawl",
                                    n_clicks=0,
                                    style={"padding": "0 75px", "margin": "auto", "borderRadius": "10px"}
                                ),

                                html.Button(
                                    "Analyze time series",
                                    id="button_chart",
                                    n_clicks=0,
                                    style={"padding": "0 66px", "margin": "auto", "marginTop": "10px",
                                           "borderRadius": "10px"}
                                )
                            ]
                        ),
                    ],
                    style={"float": "left", "backgroundColor": "#18252e", "padding": "20px", "marginTop": "20px",
                           "border": "1px solid rgba(68, 149, 209, 0.9)"},
                ),
            ],
            className='three columns selection',
        ),
        html.Div(
            [chart_div()],
            style={"height": "70%", "margin": "0px 5px", "float": "right"},
            id="charts",
            className="nine columns",
        ),
        html.Div([modal()])
    ],
    style={"paddingTop": "15px", "backgroundColor": "#1a2d46", "height": "100vh", "overflow": "auto",
           "display": "block"}
)


# open or close graph menu
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


# hide/show menu tab content if clicked or not
app.callback(
    Output("menu_tab", "children"),
    [
        Input("style_header", "n_clicks_timestamp"),
        Input("time_header", "n_clicks_timestamp"),
    ],
)(generate_active_menu_tab_callback())

# hide/show menu tab content if clicked or not
app.callback(
    Output("type_tab", "style"), [Input("menu_tab", "children")]
)(generate_style_content_tab_callback())

# hide/show menu tab content if clicked or not
app.callback(
    Output("timing_tab", "style"), [Input("menu_tab", "children")]
)(generate_studies_content_tab_callback())

# styles menu tab depending on if clicked or not
app.callback(
    Output("style_header", "style"),
    [Input("menu_tab", "children")],
    [State("style_header", "style")],
)(generate_update_style_header_callback())

# styles menu tab depending on if clicked or not
app.callback(
    Output("time_header", "style"),
    [Input("menu_tab", "children")],
    [State("time_header", "style")],
)(generate_update_time_header_callback())

#set live clock
@app.callback(Output("live_clock", "children"), [Input("interval", "n_intervals")])
def update_time(t):
    return dt.now().strftime("%H:%M:%S")


#component options of selected indice
@app.callback((Output("indice-component", "options")), [Input("input", "value")])
def set_indice_options(selected_indice):
    mng_client = MongoClient(HOST)
    query = QueryData(mng_client)
    lst_ticket = query.get_list_ticket(index=selected_indice)
    return [{'label': i, 'value': i} for i in lst_ticket]


# open or close modal
@app.callback(
    Output("modal_div", "style"),
    [
        Input("button_chart", "n_clicks"),
        Input("closeModal", "n_clicks"),
        Input("accept", "n_clicks")
    ],
    [
        State("modal_div", "style")
    ]
)
def generate_modal_open_callback(n, n2, n3, style):
    if n == 0:
        return {"display": "none"}
    if style['display'] == "block":
        return {"display": "none"}
    else:
        return {"display": "block"}


@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-predict':
        return html.Div([
            html.Div(
                [
                    # row div with 2 div
                    html.Div(
                        [
                            html.Span(
                                "SELECT PARAMETERS",
                                id="modal_parameter",
                                style={
                                    "marginBottom": "10px",
                                    "color": "#45df7e",
                                }
                            ),
                            html.P(
                                "Time",
                                style={
                                    "color": "white",
                                    "marginBottom": "0",
                                }
                            ),
                            dcc.Dropdown(
                                id='select_time',
                                options=[
                                    {"label": "1 day", "value": "day"},
                                    {"label": "1 week", "value": "week"},
                                    {"label": "1 month", "value": "month"},
                                    {"label": "1 year", "value": "year"},
                                ],
                                value="day",
                                style={
                                    "backgroundColor": "#18252E",
                                    "color": "white",
                                    "borderColor": "rgba(68,149,209,.9)",
                                    "width": "50%",
                                    "marginTop": "5px"
                                }
                            )
                        ],
                        id="left_div",
                        className="six columns",
                        style={
                            "paddingLeft": "15px",
                        }
                    ),
                    html.Div(
                        [
                            html.P(
                                "Model",
                                style={
                                    "color": "white",
                                    "marginBottom": "0",
                                }
                            ),
                            dcc.RadioItems(
                                id="select_model",
                                options=[
                                    {"label": i, "value": i} for i in model
                                ],
                                labelStyle={
                                    "display": "inline-block",
                                    "marginRight": "10px"
                                },
                                style={
                                    "marginTop": "5px"
                                }
                            )
                        ],
                        id="right_div",
                        className="six columns",
                        style={
                            "marginTop": "19px",
                        }
                    )
                ],
                className="row",
            ),
            html.Div(
                id="analyze_result",
            ),
        ])
    elif tab == 'tab-analyze':
        return html.Div([
            html.Div(
                [
                    # row div with 2 div
                    html.Div(
                        [
                            html.Span(
                                "SELECT PARAMETERS",
                                id="modal_parameter",
                                style={
                                    "marginBottom": "10px",
                                    "color": "#45df7e",
                                }
                            ),
                            html.P(
                                "LAG",
                                style={
                                    "color": "white",
                                    "marginBottom": "0",
                                }
                            ),
                            dcc.Input(
                                id='lag',
                                type='number',
                                min=0,
                                step=1,
                                value=20
                            )
                        ],
                        id="left_div",
                        className="six columns",
                        style={
                            "paddingLeft": "15px",
                        }
                    ),
                    html.Div(
                        [
                            html.P(
                                "ALPHA",
                                style={
                                    "color": "white",
                                    "marginBottom": "0",
                                }
                            ),
                            dcc.Input(
                                id='alpha',
                                type='number',
                                min=0.01,
                                max=0.99,
                                step=0.01,
                                value=0.05
                            )
                        ],
                        id="right_div",
                        className="six columns",
                        style={
                            "marginTop": "19px",
                        }
                    )
                ],
                className="row",
            ),
            html.Div(
                id="analyze_result",
            ),
        ])


# reset analyze result
@app.callback(
    Output("analyze_button", "n_clicks"),
    [
        Input("closeModal", "n_clicks"),
        Input("accept", "n_clicks"),
    ]
)
def reset_analyze_result(n, n2):
    if n > 0:
        return 0
    if n2 > 0:
        return 0


# analyze result
@app.callback(
    Output("analyze_result", "children"),
    [
        Input("analyze_button", "n_clicks"),
        Input("alpha", "value"),
        Input("lag", "value"),
        Input("input", "value"),
        Input('indice-component', 'value'),
    ]
)
def return_analyze_result(n3, alpha, lag, input_data, input_component):
    mng_client = MongoClient(HOST)
    mng_db = mng_client[DATABASE]
    db_cm_history = mng_db[History_data]
    db_cm_component = mng_db[CompoColl]
    if input_component is not None:
        df_history = pd.DataFrame(list(db_cm_history.find(
            {
                "name": input_component
            }
        )))
    else:
        df_history = pd.DataFrame(list(db_cm_history.find(
            {
                "name": input_data
            }
        )))

    acf_value, confint_upper_acf, confint_lower_acf = calculate_acf(df_history['close'], lag, alpha)
    pacf_value, confint_upper_pacf, confint_lower_pacf = calculate_pacf(df_history['close'], lag, alpha)
    if n3 > 0:
        # trace_acf_value = go.Scatter(
        #     y=acf_value,
        #     mode='markers',
        #     marker={
        #         'size': 8,
        #         'color': '#f7942e'
        #     },
        #     name='ACF'
        # )
        trace_confint_upper_acf = go.Scatter(
            y=confint_upper_acf,
            mode='lines',
            line=dict(color='#5fba7d'),
            opacity=0.7,
            showlegend=False,
            fill="tozeroy"
        )
        trace_confint_lower_acf = go.Scatter(
            y=confint_lower_acf,
            mode='lines',
            line=dict(color='#5fba7d'),
            opacity=0.7,
            showlegend=False,
            fill="tozeroy"
        )
        # trace_pacf_value = go.Scatter(
        #     y=pacf_value,
        #     mode='markers',
        #     marker={
        #         'size': 8,
        #         'color': '#007bff'
        #     },
        #     name='PACF'
        # )
        trace_confint_upper_pacf = go.Scatter(
            y=confint_upper_pacf,
            mode='lines',
            line=dict(color='#5fba7d'),
            opacity=0.7,
            showlegend=False,
            fill="tozeroy"
        )
        trace_confint_lower_pacf = go.Scatter(
            y=confint_lower_pacf,
            mode='lines',
            line=dict(color='#5fba7d'),
            opacity=0.7,
            showlegend=False,
            fill="tozeroy"
        )
        # figure = tools.make_subplots(
        #     rows=2,
        #     cols=1,
        #     print_grid=False,
        #     # shared_xaxes=True,
        #     # shared_yaxes=True,
        # )
        # figure.append_trace(trace_pacf_value, 2, 1)
        # figure.append_trace(trace_confint_lower_pacf, 2, 1)
        # figure.append_trace(trace_confint_upper_pacf, 2, 1)
        # figure.append_trace(trace_acf_value, 1, 1)
        # figure.append_trace(trace_confint_lower_acf, 1, 1)
        # figure.append_trace(trace_confint_upper_acf, 1, 1)
        # figure['layout']["margin"] = {"b": 50, "r": 5, "l": 50, "t": 20}
        # figure['layout'].update(paper_bgcolor="#18252E", plot_bgcolor="#18252E", font=dict(color='white'))
        data_acf = go.Bar(
            y=acf_value,
            name='Autocorrelation'
        )

        data_pacf = go.Bar(
            y=pacf_value,
            name='Partial Autocorrelation'
        )

        figure = tools.make_subplots(
            rows=2,
            cols=1,
            print_grid=False,
        )
        figure.append_trace(data_acf, 1, 1)
        figure.append_trace(trace_confint_lower_acf, 1, 1)
        figure.append_trace(trace_confint_upper_acf, 1, 1)
        figure.append_trace(data_pacf, 2, 1)
        figure.append_trace(trace_confint_lower_pacf, 2, 1)
        figure.append_trace(trace_confint_upper_pacf, 2, 1)
        figure['layout']["margin"] = {"b": 50, "r": 5, "l": 50, "t": 20}
        figure['layout'].update(paper_bgcolor="#18252E", plot_bgcolor="#18252E", font=dict(color='white'))
        return dcc.Graph(
            id='analyze_result_graph',
            figure=figure
        )


#indice information
@app.callback(
    (Output("indice-information", "children")),
    [
        Input("input", "value"),
        Input('indice-component', 'value'),
    ]
)
def get_indice_informations(selected_indice, indice_component):
    mng_client = MongoClient(HOST)
    mng_db = mng_client[DATABASE]
    db_cm_ind = mng_db[IndColl]
    df_ind = pd.DataFrame(list(db_cm_ind.find({"name": selected_indice}).sort("date", pymongo.DESCENDING).limit(2)))
    df_ind['date'] = df_ind['date'].apply(lambda x: dt.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'))
    last_price = str(df_ind['last'].values[0].round(2))
    return html.Div([
        html.P(
            selected_indice,
            style={"color": "rgb(69, 223, 126)", "textAlign": "left", "fontSize": "15px",
                   "textTransform": "uppercase", }
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
                    df_ind['date'].values[0],
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


# component information
@app.callback(
    (Output("component-information", "children")),
    [
        Input('indice-component', 'value'),
    ]
)
def get_component_information(selected_component):
    mng_client = MongoClient(HOST)
    mng_db = mng_client[DATABASE]
    db_cm_component = mng_db[CompoColl]
    df_component = pd.DataFrame(
        list(db_cm_component.find({"name": selected_component}).sort("date", pymongo.DESCENDING).limit(2)))
    df_component['date'] = df_component['date'].apply(lambda x: dt.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'))
    last_price = str(df_component['last'].values[0].round(2))
    return html.Div([
        html.P(
            selected_component,
            style={"color": "rgb(69, 223, 126)", "textAlign": "left", "fontSize": "15px",
                   "textTransform": "uppercase", }
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
                    df_component['date'].values[0],
                    className="four columns",
                    style={"color": "white", "textAlign": "center", "fontSize": "10px", "textTransform": "uppercase",
                           "margin": "auto"}
                ),
                html.P(
                    last_price,
                    className="four columns",
                    style={"color": get_color(df_component['last'].values[0], df_component['last'].values[1]),
                           "textAlign": "center", "fontSize": "10px", "textTransform": "uppercase",
                           "margin": "auto"}
                ),
                html.P(
                    df_component['volume'].values[0],
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
               Input('indice-component', 'value'),
               # Input('my-date-picker-range', 'start_date'),
               # Input('my-date-picker-range', 'end_date'),
               Input('chart_type', 'value'),
               Input('timing', 'values')],
              events=[Event('graph-update', 'interval')])
def update_graph_scatter(input_data, input_data_component, chart_type, studies):
    try:
        mng_client = MongoClient(HOST)
        mng_db = mng_client[DATABASE]
        db_cm_ind = mng_db[IndColl]
        db_cm_history = mng_db[History_data]
        db_cm_component = mng_db[CompoColl]
        # if start_date is not None:
        #     start_date = dt.strptime(start_date, '%Y-%m-%d')
        #     start_date = float(start_date.replace(tzinfo=timezone.utc).timestamp())
        # if end_date is not None:
        #     end_date = dt.strptime(end_date, '%Y-%m-%d')
        #     end_date = float(end_date.replace(tzinfo=timezone.utc).timestamp())

        if input_data_component is not None and input_data is not None:
            df_ind = pd.DataFrame(list(db_cm_component.find(
                {
                    "name": input_data_component
                }
            )))
            df_history = pd.DataFrame(list(db_cm_history.find(
                {
                    "name": input_data_component
                }
            )))
        elif input_data_component is None and input_data is not None:
            df_ind = pd.DataFrame(list(db_cm_ind.find(
                {
                    "name": input_data
                }
            )))
            df_history = pd.DataFrame(list(db_cm_history.find(
                {
                    "name": input_data
                }
            )))
        df_ind['date'] = df_ind['date'].apply(lambda x: dt.fromtimestamp(x).isoformat())

        df_ind = df_ind.sort_values(by=['date'])
        print(df_ind)
        df_history = df_history.sort_values(by=['date'])
        df_ind['last'] = df_ind['last'].round(4)

        if (chart_type == 'line_trace'):
            trace_ind = go.Scatter(
                x=df_history['date'],
                y=df_history['close'],
                mode='lines',
                line=dict(color='#4f94c4'),
                name="history data",
            )
        elif (chart_type == 'mountain_trace'):
            trace_ind = go.Scatter(
                x=df_history['date'],
                y=df_history['close'],
                mode='lines',
                line=dict(color='#4f94c4'),
                fill="tozeroy",
                name="history data",
            )
        elif (chart_type == 'candlestick_trace'):
            trace_ind = go.Candlestick(
                x=df_history["date"],
                open=df_history["open"],
                high=df_history["high"],
                low=df_history["low"],
                close=df_history["close"],
                increasing=dict(line=dict(color="#00ff00")),
                decreasing=dict(line=dict(color="white")),
                name="history data",
            )

        trace_mock = go.Scatter(
            x=df_ind['date'],
            y=df_ind['last'],
            mode='lines',
            line=dict(color='#28a745'),
            name="real-time data",
            opacity=0.8,
        )

        rows = 2
        figure = tools.make_subplots(
            rows=rows,
            cols=1,
            print_grid=False,
            # subplot_titles=("History Data", "Real-time Data")
        )

        if studies != []:
            for study in studies:
                if study == "bollinger_trace":
                    figure = bollinger_trace(df_history, figure)
                if study == "moving_average_trace":
                    figure = moving_average_trace(df_history, figure)
                if study == "e_moving_average_trace":
                    figure = e_moving_average_trace(df_history, figure)
                if study == "pp_trace":
                    figure = pp_trace(df_history, figure)

        figure.append_trace(trace_ind, 1, 1)
        figure.append_trace(trace_mock, 2, 1)
        figure['layout']["margin"] = {"b": 50, "r": 5, "l": 50, "t": 5}
        figure['layout']['xaxis'].update(title='1', showgrid=False)
        figure['layout']['yaxis'].update(title='2', showgrid=False)
        figure['layout'].update(title=input_data, paper_bgcolor="#18252E", plot_bgcolor="#18252E")
        figure['layout']['yaxis'] = dict(
            # range=[800, 1000],
            domain=[0.55, 1]
        )
        figure['layout']['xaxis'] = dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label='1d',
                         step='day',
                         stepmode='backward'),
                    dict(count=7,
                         label='1w',
                         step='day',
                         stepmode='backward'),
                    dict(count=1,
                         label='1m',
                         step='month',
                         stepmode='backward'),
                    dict(count=6,
                         label='6m',
                         step='month',
                         stepmode='backward'),
                    dict(count=1,
                         label='1y',
                         step='year',
                         stepmode='backward'),
                    dict(step='all')
                ]),
                font=dict(family='Arial',
                          size=10),
                bgcolor='white',
                activecolor='#ffc107'
            ),
            rangeslider=dict(
                visible=False
            ),
            type='date',
        )
        return dcc.Graph(
            id='example-graph',
            figure=figure,
            style={
                "height": "579px"
            }
        )
    except Exception as e:
        with open('errors.txt', 'a') as f:
            f.write(str(e))
            f.write('\n')


if __name__ == '__main__':
    app.run_server(debug=True)