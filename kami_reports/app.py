#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from flask import Flask
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
    get_sales_bi_df,
    get_sales_lines_df,
)
from flask_caching import Cache
from kami_logging import benchmark_with, logging_with
from layout import get_page_layout, template_dark, template_ligth
server=Flask(__name__)
app = dash.Dash(server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'KAMI Sales Analytics'
cache = Cache(
    app.server, config={'CACHE_TYPE': 'filesystem', 'CACHE_DIR': 'cache'}
)
app_logger = logging.getLogger('kami-dash')


@cache.memoize(timeout=TIMEOUT)
@benchmark_with(app_logger)
@logging_with(app_logger)
def get_sales_bi_json():
    sales_bi_df = get_sales_bi_df(get_sales_lines_df())
    sales_bi_df.columns = list(
        map(lambda x: x.replace('dt_', 'timestamp_'), sales_bi_df.columns)
    )

    return sales_bi_df.to_json(orient='split')


def get_cached_sales_bi():
    sales_bi_json = get_sales_bi_json()
    sales_bi_df = pd.read_json(
        sales_bi_json, orient='split', convert_dates=True
    )
    sales_bi_df.columns = list(
        map(lambda x: x.replace('timestamp_', 'dt_'), sales_bi_df.columns)
    )
    return sales_bi_df


@cache.memoize(timeout=TIMEOUT)
@benchmark_with(app_logger)
@logging_with(app_logger)
def get_master_df_json(sales_bi_df):
    master_df = build_master_df(sales_bi_df)
    master_df.columns = list(
        map(lambda x: x.replace('dt_', 'timestamp_'), master_df.columns)
    )
    return master_df.to_json(orient='split')


def get_cached_master_df():
    master_df_json = get_master_df_json(get_cached_sales_bi())
    master_df = pd.read_json(
        master_df_json, orient='split', convert_dates=True
    )
    master_df.columns = list(
        map(lambda x: x.replace('timestamp_', 'dt_'), master_df.columns)
    )
    master_df = add_ytd_cols(master_df)
    return master_df


sales_bi_df = get_cached_sales_bi()
master_df = get_cached_master_df()

layout = get_page_layout(master_df)

app.layout = dbc.Container(
    layout,
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
    Output('salesperson-kpi-ativo', 'figure'),
    Input('select-sales-team', 'value'),
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
    Input('select-sales-team', 'value'),
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
    Input('select-sales-team', 'value'),
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
    Input('select-sales-team', 'value'),
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
    Input('select-sales-team', 'value'),
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
    Input('select-sales-team', 'value'),
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
    Input('select-sales-team', 'value'),
    Input(ThemeSwitchAIO.ids.switch('theme'), 'value'),
)
def update_graph_ytd_2022(sales_team, toggle):
    template = template_ligth if toggle else template_dark
    mask = get_filter_mask(master_df, 'equipe', sales_team)
    dff = master_df.loc[mask]
    ytd_2022 = get_ytd_graph(dff, 'ytd_2022', template)
    return ytd_2022


@callback(
    Output('download-master', 'data'),
    Input('export-master-button', 'n_clicks'),
    prevent_initial_call=True,
)
def download_master_df(n_clicks):
    return dcc.send_data_frame(master_df.to_csv, 'mestre_geral.csv')


@callback(
    Output('download-products', 'data'),
    Input('export-products-button', 'n_clicks'),
    prevent_initial_call=True,
)
def download_products_df(n_clicks):
    return dcc.send_data_frame(sales_bi_df.to_csv, 'produtos_geral.csv')


if __name__ == '__main__':
    app.run_server(debug=True, port=8008)
