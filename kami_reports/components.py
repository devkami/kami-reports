#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html

app_logger = logging.getLogger('kami-dash')

## Filters


def dropdown_select(id, df, filter_dict, multi=True):
    return html.Div(
        [
            html.Label(filter_dict['name'], style={'font-size': '100%'}),
            dcc.Dropdown(
                options=df[filter_dict['options']].unique(),
                value=df[filter_dict['values']].unique()[:-1],
                id=f'select-{id}',
                className='dbc',
                multi=multi,
            ),
        ],
        className='my-2',
    )


def multi_selects_from_df(df, filters_list):
    return [dropdown_select(df, filter_dict) for filter_dict in filters_list]


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
