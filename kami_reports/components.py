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


def date_picker(id, min_date, max_date, title):
    return html.Div(
        [
            html.Label(title, style={'font-size': '120%'}),
            dcc.DatePickerRange(
                id=f'date-picker-{id}',
                min_date_allowed=min_date,
                max_date_allowed=max_date,
                start_date=date(STARTING_YEAR, datetime.now().month, 1),
                end_date=datetime.now(),
            ),
        ]
    )


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


def create_input_filters(filter_cols):
    return [Input(f'select-{filter_id}', 'value') for filter_id in filter_cols]


def get_filters(df, filter_cols):
    filters_inputs = None
    filters = multi_selects_from_df(df, filter_cols)
    filters_inputs = create_input_filters(filter_cols)

    return filters_inputs, filters


def get_filter_mask(df, col, selected_itens):
    return (
        df[col].isin(df[col].unique())
        if not selected_itens
        or selected_itens == [0]
        or 'Todos' in selected_itens
        or 'Todas' in selected_itens
        else df[col].isin(selected_itens)
    )


def filter_orders_df(orders_df, filters):
    filtered_df = pd.DataFrame()
    for filter_col, filter_values in zip(filters.keys(), filters.values()):
        mask = get_filter_mask(orders_df, filter_col, filter_values)
        filtered_df = orders_df.loc[mask]
    filtered_df = filtered_df.dropna(subset=['dt_faturamento'])
    return filtered_df


## Graphs & Indicators
def brands_graph(orders_df):
    df = (
        orders_df.groupby(['cod_marca', 'desc_marca'])['valor_nota']
        .sum()
        .reset_index()
    )

    figure = go.Figure()
    figure.add_trace(
        go.Pie(
            labels=df['desc_marca'],
            values=df['valor_nota'],
            hole=0.3,
            textinfo='none',
        ),
    )

    return figure


def monthly_sales_graph(orders_df):
    orders_df = orders_df.sort_values(
        by=['ano', 'mes'], ascending=[True, True]
    )
    orders_df['ano_mes'] = (
        orders_df['ano'].astype(str) + '/' + orders_df['mes'].astype(str)
    )
    orders_df = orders_df.loc[orders_df['nop'].isin(SALE_NOPS)]
    df = orders_df.groupby(['ano_mes'])['valor_nota'].sum().reset_index()
    figure = go.Figure(
        go.Scatter(
            x=df['ano_mes'], y=df['valor_nota'], mode='lines', fill='tonexty'
        )
    )
    median = round(df['valor_nota'].mean(), 2)
    if not df['ano_mes'].empty:
        figure.add_shape(
            type='line',
            x0=min(df['ano_mes']),
            y0=median,
            x1=max(df['ano_mes']),
            y1=median,
            line_color='red',
            line_dash='dot',
        )
        figure.add_annotation(
            text=f'Média:{numerize.numerize(median)}',
            xref='paper',
            yref='paper',
            font=dict(size=25, color='red'),
            align='center',
            bgcolor='rgba(255,0,0,0.2)',
            x=0.05,
            y=0.75,
            showarrow=False,
        )
    return figure


def top_salesperson_indicator(orders_df):

    sellers_list = get_salesperson_opt_list(orders_df)

    df = orders_df.groupby(['cod_colaborador', 'nome_colaborador'])[
        'valor_nota'
    ].sum()
    df.sort_values(ascending=False, inplace=True)
    df = df.reset_index()

    figure = go.Figure()
    figure.add_trace(
        go.Indicator(
            mode='number+delta',
            title={
                'text': f"<span style='font-size:100%'>{df['nome_colaborador'].iloc[0]}</span><br><span style='font-size:70%'>Em vendas em relação a média</span><br>"
            },
            value=df['valor_nota'].iloc[0],
            number={'prefix': 'R$'},
            delta={
                'relative': True,
                'valueformat': '.1%',
                'reference': df['valor_nota'].mean(),
            },
        )
    )
    return figure


def average_ticket_indicator(orders_df):
    average_ticket = (
        orders_df['valor_nota'].sum() / orders_df['cod_pedido'].count()
    )
    figure = go.Figure()
    figure.add_trace(
        go.Indicator(
            mode='number',
            title={
                'text': f"<span style='font-size:100%'>Total de Vendas / QTD de Pedidos</span><br><span style='font-size:70%'>Em R$</span><br>"
            },
            value=average_ticket,
            number={'prefix': 'R$'},
        )
    )
    return figure


def daily_sales_graph(orders_df):
    orders_df = orders_df.sort_values(by=['dt_faturamento'], ascending=[True])
    df = (
        orders_df.groupby(['dt_faturamento'])['valor_nota'].sum().reset_index()
    )

    figure = go.Figure(
        go.Scatter(
            x=df['dt_faturamento'],
            y=df['valor_nota'],
            mode='lines',
            fill='tonexty',
        )
    )
    median = round(df['valor_nota'].mean(), 2)
    if not df['dt_faturamento'].empty:
        figure.add_shape(
            type='line',
            x0=min(df['dt_faturamento']),
            y0=median,
            x1=max(df['dt_faturamento']),
            y1=median,
            line_color='red',
            line_dash='dot',
        )
        figure.add_annotation(
            text=f'Média:{numerize.numerize(median)}',
            xref='paper',
            yref='paper',
            font=dict(size=25, color='red'),
            align='center',
            bgcolor='rgba(255,0,0,0.2)',
            x=0.05,
            y=0.75,
            showarrow=False,
        )
    return figure


def monthly_salesperson_graph(orders_df):
    df = (
        orders_df.groupby(
            ['dt_faturamento', 'cod_colaborador', 'nome_colaborador']
        )['valor_nota']
        .sum()
        .reset_index()
    )
    df_group = (
        orders_df.groupby('dt_faturamento')['valor_nota'].sum().reset_index()
    )

    figure = px.line(
        df, x='dt_faturamento', y='valor_nota', color='nome_colaborador'
    )
    figure.add_trace(
        go.Scatter(
            x=df_group['dt_faturamento'],
            y=df_group['valor_nota'],
            mode='lines+markers',
            fill='tonexty',
            fillcolor='rgba(255,0,0,0.2)',
            name='Total Geral',
        )
    )

    return figure


def top_five_salesperson_graph(orders_df):
    df_salesperson = (
        orders_df.groupby(['cod_colaborador', 'nome_colaborador'])[
            'valor_nota'
        ]
        .sum()
        .head(5)
        .reset_index()
    )
    df_salesperson = df_salesperson
    figure = go.Figure(
        go.Bar(
            x=df_salesperson['nome_colaborador'],
            y=df_salesperson['valor_nota'],
            textposition='auto',
        )
    )
    return figure


def total_sales_indicator(orders_df):
    figure = go.Figure()
    figure.add_trace(
        go.Indicator(
            mode='number',
            title={
                'text': f"<span style='font-size:100%'>Total de Vendas para o Período</span><br><span style='font-size:70%'>Em R$</span><br>"
            },
            value=orders_df['valor_nota'].sum(),
            number={'prefix': 'R$'},
        )
    )
    return figure


def ytd_salesperson(dff):
    for year in range(CURRENT_YEAR - 1, CURRENT_YEAR + 1):
        period = pd.period_range(
            start=f'1-{year}',
            end=f'{CURRENT_MONTH}-{year}',
            freq='M',
        )
        ytd_last_year_cols = [
            f'{MONTHS_PTBR_ABBR[p.month]}_{p.year}_liquido'
            for p in period
            if f'{MONTHS_PTBR_ABBR[p.month]}_{p.year}_liquido' in dff.columns
        ]
        dff[f'ytd_{year}'] = dff[ytd_last_year_cols].sum(axis=1)
    master_ytd_df = (
        dff.groupby(['nome_colaborador', 'equipe'])
        .agg(
            ACUMULADO_2022=('ytd_2022', 'sum'),
            ACUMULADO_2023=('ytd_2023', 'sum'),
            YEAR_TO_DATE=('FAT. LÍQ. 2023 YTD', 'sum'),
        )
        .reset_index()
    )

    ytd_2022 = px.bar(
        master_ytd_df,
        x='ACUMULADO_2022',
        y='nome_colaborador',
        orientation='h',
        title='ACUMULADO_2022',
    )
    ytd_2023 = px.bar(
        master_ytd_df,
        x='ACUMULADO_2023',
        y='nome_colaborador',
        orientation='h',
        title='ACUMULADO_2023',
    )
    ytd = px.bar(
        master_ytd_df,
        x='YEAR_TO_DATE',
        y='nome_colaborador',
        orientation='h',
        title='YEAR_TO_DATE',
    )
    return ytd_2022, ytd_2023, ytd


def frequency_sales_indicators(dff, template):
    dff = group_by_cols(dff, ['cod_cliente'])

    inativo = (
        go.Figure()
        .add_trace(
            go.Indicator(
                mode='number',
                title={
                    'text': "<span style='font-size:100%'>Total de Inativos </span>"
                },
                value=len(dff[dff['STATUS'] == 'INATIVO']),
            )
        )
        .update_layout(template=template)
    )

    pre_inativo = (
        go.Figure()
        .add_trace(
            go.Indicator(
                mode='number',
                title={
                    'text': "<span style='font-size:100%'>Total de Pre-Inativos </span>"
                },
                value=len(dff[dff['STATUS'] == 'PRE-INATIVO']),
            )
        )
        .update_layout(template=template)
    )

    ativo = (
        go.Figure()
        .add_trace(
            go.Indicator(
                mode='number',
                title={
                    'text': "<span style='font-size:100%'>Total de Ativos </span>"
                },
                value=len(dff[dff['STATUS'] == 'ATIVO']),
            )
        )
        .update_layout(template=template)
    )

    perdido = (
        go.Figure()
        .add_trace(
            go.Indicator(
                mode='number',
                title={
                    'text': "<span style='font-size:100%'>Total de Perdidos </span>"
                },
                value=len(dff[dff['STATUS'] == 'PERDIDO']),
            )
        )
        .update_layout(template=template)
    )

    return inativo, pre_inativo, ativo, perdido
