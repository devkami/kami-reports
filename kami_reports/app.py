#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

import dash
import dash_bootstrap_components as dbc
import pandas as pd
from components import get_filter_mask, get_single_indicator, get_ytd_graph
from constant import OPERATORS, TIMEOUT
from dash import State, callback, dcc
from dash.dependencies import Input, Output
from dash_bootstrap_templates import ThemeSwitchAIO
from dataframe import (
    add_ytd_cols,
    build_master_df,
    build_sales_orders_df,
    get_sales_lines_df,
)
from flask import Flask
from flask_caching import Cache
from kami_logging import benchmark_with, logging_with
from layout import get_page_layout, template_dark, template_ligth
from unidecode import unidecode
import urllib

server = Flask(__name__)
app = dash.Dash(server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'KAMI Sales Analytics'
cache = Cache(
    app.server, config={'CACHE_TYPE': 'filesystem', 'CACHE_DIR': 'cache'}
)
app_logger = logging.getLogger('kami-dash')


@cache.memoize(timeout=TIMEOUT)
@benchmark_with(app_logger)
@logging_with(app_logger)
def get_sales_lines_json():
    sales_lines_df = get_sales_lines_df()
    sales_lines_df.columns = list(
        map(lambda x: x.replace('dt_', 'timestamp_'), sales_lines_df.columns)
    )

    return sales_lines_df.to_json(orient='split')


def get_cached_sales_lines():
    sales_lines_json = get_sales_lines_json()
    sales_lines_df = pd.read_json(
        sales_lines_json, orient='split', convert_dates=True
    )
    sales_lines_df.columns = list(
        map(lambda x: x.replace('timestamp_', 'dt_'), sales_lines_df.columns)
    )
    return sales_lines_df


@cache.memoize(timeout=TIMEOUT)
@benchmark_with(app_logger)
@logging_with(app_logger)
def get_sales_orders_json():
    sales_orders_df = build_sales_orders_df(get_cached_sales_lines())
    sales_orders_df.columns = list(
        map(lambda x: x.replace('dt_', 'timestamp_'), sales_orders_df.columns)
    )

    return sales_orders_df.to_json(orient='split')


def get_cached_sales_orders():
    sales_orders_json = get_sales_orders_json()
    sales_orders_df = pd.read_json(
        sales_orders_json, orient='split', convert_dates=True
    )
    sales_orders_df.columns = list(
        map(lambda x: x.replace('timestamp_', 'dt_'), sales_orders_df.columns)
    )
    return sales_orders_df


@cache.memoize(timeout=TIMEOUT)
@benchmark_with(app_logger)
@logging_with(app_logger)
def get_master_df_json():
    master_df = build_master_df(get_cached_sales_orders())
    master_df.columns = list(
        map(lambda x: x.replace('dt_', 'timestamp_'), master_df.columns)
    )
    return master_df.to_json(orient='split')


def get_cached_master_df():
    master_df_json = get_master_df_json()
    master_df = pd.read_json(
        master_df_json, orient='split', convert_dates=True
    )
    master_df.columns = list(
        map(lambda x: x.replace('timestamp_', 'dt_'), master_df.columns)
    )
    master_df = add_ytd_cols(master_df)
    return master_df


products_df = get_cached_sales_lines()
master_df = get_cached_master_df()


app.layout = dbc.Container(
    get_page_layout(master_df),
    fluid=True,
    style={'height': '100vh'},
)


@app.callback(
    Output('sidebar', 'is_open'),
    Input('open-sidebar', 'n_clicks'),
    [State('sidebar', 'is_open')],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open


def split_filter_part(filter_part):
    for operator_type in OPERATORS:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[
                    name_part.find('{') + 1 : name_part.rfind('}')
                ]

                value_part = value_part.strip()
                v0 = value_part[0]
                if v0 == value_part[-1] and v0 in ("'", '"', '`'):
                    value = value_part[1:-1].replace('\\' + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part
                return name, operator_type[0].strip(), value

    return [None] * 3


@callback(
    Output('table-paging-with-graph', 'data'),
    Input('table-paging-with-graph', 'page_current'),
    Input('table-paging-with-graph', 'page_size'),
    Input('table-paging-with-graph', 'sort_by'),
    Input('table-paging-with-graph', 'filter_query'),
)
def update_table(page_current, page_size, sort_by, filter):
    filtering_expressions = filter.split(' && ')
    dff = master_df
    for filter_part in filtering_expressions:
        col_name, operator, filter_value = split_filter_part(filter_part)

        if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
            dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
        elif operator == 'contains':
            dff = dff.loc[dff[col_name].str.contains(filter_value)]
        elif operator == 'datestartswith':
            dff = dff.loc[dff[col_name].str.startswith(filter_value)]

    if len(sort_by):
        dff = dff.sort_values(
            [col['column_id'] for col in sort_by],
            ascending=[col['direction'] == 'asc' for col in sort_by],
            inplace=False,
        )

    return dff.iloc[
        page_current * page_size : (page_current + 1) * page_size
    ].to_dict('records')


@callback(
    Output('salesperson-inadimplentes', 'figure'),
    Input('select-sales-team-graph-tab', 'value'),
    Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
)
def update_kpi_inadimplentes(sales_team, toggle):
    template = template_ligth if toggle else template_dark
    mask = get_filter_mask(master_df, 'equipe', sales_team)
    customer_df = master_df.loc[mask].drop_duplicates(subset=['cod_cliente'])
    inadimplentes = get_single_indicator(
        title='Inadimplentes',
        value=customer_df[customer_df['dias_atraso'] > 30].count()[
            'cod_cliente'
        ],
        template=template,
    )
    return inadimplentes


# -----------------------------------------
@callback(
    Output('salesperson-churn-percent', 'figure'),
    Input('select-sales-team-graph-tab', 'value'),
    Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
)
def update_kpi_churn_base(sales_team, toggle):
    template = template_ligth if toggle else template_dark
    mask = get_filter_mask(master_df, 'equipe', sales_team)
    customer_df = master_df.loc[mask].drop_duplicates(subset=['cod_cliente'])
    churn = get_single_indicator(
        title='CHURN / BASE em %',
        value=round(
            customer_df[customer_df['STATUS'] == 'PERDIDO'].count()[
                'cod_cliente'
            ]
            / (
                customer_df[customer_df['STATUS'] == 'ATIVO'].count()[
                    'cod_cliente'
                ]
                + customer_df[customer_df['STATUS'] == 'INATIVO'].count()[
                    'cod_cliente'
                ]
                + customer_df[customer_df['STATUS'] == 'PRE-INATIVO'].count()[
                    'cod_cliente'
                ]
                + customer_df[customer_df['STATUS'] == 'PERDIDO'].count()[
                    'cod_cliente'
                ]
            ),
            2,
        )
        * 100,
        template=template,
    )
    return churn


@callback(
    Output('salesperson-kpi-ativo', 'figure'),
    Input('select-sales-team-graph-tab', 'value'),
    Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
)
def update_kpi_active(sales_team, toggle):
    template = template_ligth if toggle else template_dark
    mask = get_filter_mask(master_df, 'equipe', sales_team)
    customer_df = master_df.loc[mask].drop_duplicates(subset=['cod_cliente'])
    ativo = get_single_indicator(
        title='Total de Ativos',
        value=customer_df[customer_df['STATUS'] == 'ATIVO'].count()[
            'cod_cliente'
        ],
        template=template,
    )
    return ativo


@callback(
    Output('salesperson-kpi-pre_inativo', 'figure'),
    Input('select-sales-team-graph-tab', 'value'),
    Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
)
def update_kpi_pre_inactive(sales_team, toggle):
    template = template_ligth if toggle else template_dark
    mask = get_filter_mask(master_df, 'equipe', sales_team)
    customer_df = master_df.loc[mask].drop_duplicates(subset=['cod_cliente'])
    pre_inativo = get_single_indicator(
        title='Total de Pré-inativos',
        value=customer_df[customer_df['STATUS'] == 'PRE-INATIVO'].count()[
            'cod_cliente'
        ],
        template=template,
    )
    return pre_inativo


@callback(
    Output('salesperson-kpi-inativo', 'figure'),
    Input('select-sales-team-graph-tab', 'value'),
    Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
)
def update_kpi_inctive(sales_team, toggle):
    template = template_ligth if toggle else template_dark
    mask = get_filter_mask(master_df, 'equipe', sales_team)
    customer_df = master_df.loc[mask].drop_duplicates(subset=['cod_cliente'])
    inativo = get_single_indicator(
        title='Total de Inativos',
        value=customer_df[customer_df['STATUS'] == 'INATIVO'].count()[
            'cod_cliente'
        ],
        template=template,
    )
    return inativo


@callback(
    Output('salesperson-kpi-perdido', 'figure'),
    Input('select-sales-team-graph-tab', 'value'),
    Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
)
def update_kpi_lost(sales_team, toggle):
    template = template_ligth if toggle else template_dark
    mask = get_filter_mask(master_df, 'equipe', sales_team)
    customer_df = master_df.loc[mask].drop_duplicates(subset=['cod_cliente'])
    perdido = get_single_indicator(
        title='Total de Perdidos',
        value=customer_df[customer_df['STATUS'] == 'PERDIDO'].count()[
            'cod_cliente'
        ],
        template=template,
    )
    return perdido


@callback(
    Output('salesperson-graph-ytd', 'figure'),
    Input('select-sales-team-graph-tab', 'value'),
    Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
)
def update_graph_ytd(sales_team, toggle):
    template = template_ligth if toggle else template_dark
    mask = get_filter_mask(master_df, 'equipe', sales_team)
    dff = master_df.loc[mask]
    ytd = get_ytd_graph(dff, 'FAT. LÍQ. 2023 YTD', template)
    return ytd


@callback(
    Output('salesperson-graph-ytd-2023', 'figure'),
    Input('select-sales-team-graph-tab', 'value'),
    Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
)
def update_graph_ytd_2023(sales_team, toggle):
    template = template_ligth if toggle else template_dark
    mask = get_filter_mask(master_df, 'equipe', sales_team)
    dff = master_df.loc[mask]
    ytd_2023 = get_ytd_graph(dff, 'ytd_2023', template)
    return ytd_2023


@callback(
    Output('salesperson-graph-ytd-2022', 'figure'),
    Input('select-sales-team-graph-tab', 'value'),
    Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
)
def update_graph_ytd_2022(sales_team, toggle):
    template = template_ligth if toggle else template_dark
    mask = get_filter_mask(master_df, 'equipe', sales_team)
    dff = master_df.loc[mask]
    ytd_2022 = get_ytd_graph(dff, 'ytd_2022', template)
    return ytd_2022


def normalize_name(name):
    return unidecode(
        ''.join(
            ch for ch in name.replace(' ', '_') if ch.isalpha() or ch == '_'
        ).lower()
    )


@callback(
    Output('download-master', 'href'),
    Input('select-sales-team-download', 'value'),
    Input('export-master-button', 'n_clicks'),
    prevent_initial_call=True,
)
def download_master_df(sales_team, n_clicks):
    df = master_df
    mask = get_filter_mask(master_df, 'equipe', [sales_team])    
    dff = df.loc[mask]
    csv_string = dff.to_csv(index=False, encoding='utf-8',sep=';',header=True)
    csv_string="data:text/csv;charset=utf-8,%EF%BB%BF" + urllib.parse.quote(csv_string)
    return csv_string


@callback(
    Output('download-products', 'href'),
    Input('select-sales-team-download', 'value'),
    Input('export-products-button', 'n_clicks'),
    prevent_initial_call=True,
)
def download_products_df(sales_team, n_clicks):
    mask = get_filter_mask(products_df, 'equipe', [sales_team])
    dff = products_df.loc[mask]
    return dcc.send_data_frame(
        dff.to_excel, f'produtos_{normalize_name(sales_team)}.xlsx'
    )


if __name__ == '__main__':
    app.run_server(debug=True, port=8008)
