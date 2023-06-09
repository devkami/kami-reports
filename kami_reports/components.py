#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from datetime import date, datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from constant import (
    CURRENT_MONTH,
    CURRENT_YEAR,
    MONTHS_PTBR_ABBR,
    SALE_NOPS,
    STARTING_YEAR,
)
from dash import Input, dcc, html
from dataframe import get_salesperson_opt_list, group_by_cols
from numerize import numerize

app_logger = logging.getLogger('kami-dash')

## Filters


def multi_select(id, df, filter_dict):
    return html.Div(
        [
            html.Label(filter_dict['name'], style={'font-size': '100%'}),
            dcc.Dropdown(
                options=df[filter_dict['options']].unique(),
                value=df[filter_dict['values']].unique()[:-1],
                id=f'select-{id}',
                className='dbc',
                multi=True,
            ),
        ],
        className='my-2',
    )


def multi_selects_from_df(df, filters_list):
    return [multi_select(df, filter_dict) for filter_dict in filters_list]


def get_filter_mask(df, col, selected_itens):
    return (
        df[col].isin(df[col].unique())
        if not selected_itens
        or selected_itens == [0]
        or 'Todos' in selected_itens
        or 'Todas' in selected_itens
        else df[col].isin(selected_itens)
    )


def get_single_indicator(title, value, template):
    return (
        go.Figure()
        .add_trace(go.Indicator(title=title, mode='number', value=value))
        .update_layout(template=template)
    )


def get_ytd_graph(dff, ytd_col, template):
    master_ytd_df = (
        dff.groupby(['nome_colaborador', 'equipe'])
        .agg(YEAR_TO_DATE=(ytd_col, 'sum'))
        .reset_index()
    )
    ytd = px.bar(
        master_ytd_df, x='YEAR_TO_DATE', y='nome_colaborador', orientation='h'
    )
    ytd.update_layout(template=template)
    return ytd
