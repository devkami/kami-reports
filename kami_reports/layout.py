#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime

import dash_bootstrap_components as dbc
import pkg_resources
from constant import CURRENT_MONTH, CURRENT_YEAR, MONTHS_PTBR_ABBR, PAGE_SIZE
from dash import dash_table, dcc, html
from dash_bootstrap_templates import ThemeSwitchAIO

# Style ->
config_graph = {'displayModeBar': False, 'showTips': True}
config_indicator = {'displayModeBar': False, 'showTips': False}
indicator_style = {'height': '40vh'}
tab_card = {'height': '100%'}
template_ligth = 'spacelab'
template_dark = 'slate'
url_theme1 = dbc.themes.SPACELAB
url_theme2 = dbc.themes.SLATE

# Layout ->
def get_data_tab(df, cols_size):
    return (
        html.Div(
            [
                dbc.Button(
                    'Exportar Mestre',
                    color='primary',
                    className='me-1, mr-2 my-2',
                    id='export-master-button',
                ),
                dcc.Download(id='download-master'),
                dbc.Button(
                    'Exportar Produtos',
                    external_link=True,
                    color='primary',
                    className='me-1, m-2',
                    id='export-products-button',
                ),
                dcc.Download(id='download-products'),
                dash_table.DataTable(
                    id='table-paging-with-graph',
                    columns=[{'name': i, 'id': i} for i in df.columns],
                    fixed_rows={'headers': True, 'data': 0},
                    page_count=int(len(df) / PAGE_SIZE),
                    page_current=0,
                    page_size=PAGE_SIZE,
                    page_action='custom',
                    filter_action='custom',
                    filter_query='',
                    sort_action='custom',
                    sort_mode='multi',
                    sort_by=[],
                    style_cell={'whiteSpace': 'normal'},
                    style_data_conditional=[
                        {
                            'if': {'column_id': col_size['column']},
                            'width': f"{col_size['len']*13}px",
                        }
                        for col_size in cols_size
                    ],
                    virtualization=True,
                ),
            ],
            style={'height': 550, 'overflowY': 'scroll'},
            className='six columns',
        ),
    )


def get_graph_tab(sales_teams_options):
    sales_teams_options = list(sales_teams_options) + ['Todas']
    return html.Div(
        [
            html.Hr(),
            dbc.Container(
                [
                    dbc.Row(
                        [
                            html.Label(
                                'Equipe de Vendas', style={'font-size': '100%'}
                            ),
                            dcc.Dropdown(
                                options=(sales_teams_options),
                                value=sales_teams_options[-1],
                                id='select-sales-team',
                                className='dbc',
                                multi=True,
                            ),
                        ],
                        className='my-2 dbc',
                    ),
                    html.Hr(),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Card(
                                        [
                                            dbc.CardHeader(
                                                html.Center("CHURN KPI's")
                                            ),
                                            dbc.CardBody(
                                                [
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                [
                                                                    dcc.Graph(
                                                                        style=indicator_style,
                                                                        config=config_indicator,
                                                                        className='dbc',
                                                                        id='salesperson-kpi-ativo',
                                                                    ),
                                                                ],
                                                                sm=12,
                                                                md=3,
                                                            ),
                                                            dbc.Col(
                                                                [
                                                                    dcc.Graph(
                                                                        style=indicator_style,
                                                                        config=config_indicator,
                                                                        className='dbc',
                                                                        id='salesperson-kpi-inativo',
                                                                    ),
                                                                ],
                                                                sm=12,
                                                                md=3,
                                                            ),
                                                            dbc.Col(
                                                                [
                                                                    dcc.Graph(
                                                                        style=indicator_style,
                                                                        config=config_indicator,
                                                                        className='dbc',
                                                                        id='salesperson-kpi-pre_inativo',
                                                                    ),
                                                                ],
                                                                sm=12,
                                                                md=3,
                                                            ),
                                                            dbc.Col(
                                                                [
                                                                    dcc.Graph(
                                                                        style=indicator_style,
                                                                        config=config_indicator,
                                                                        className='dbc',
                                                                        id='salesperson-kpi-perdido',
                                                                    )
                                                                ],
                                                                sm=12,
                                                                md=3,
                                                            ),
                                                        ]
                                                    )
                                                ]
                                            ),
                                        ],
                                        style=tab_card,
                                    )
                                ],
                                sm=12,
                                lg=12,
                            ),
                        ],
                        className='my-2',
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Card(
                                        [
                                            dbc.CardHeader(
                                                html.Center('Year To Date')
                                            ),
                                            dbc.CardBody(
                                                [
                                                    dcc.Graph(
                                                        config=config_graph,
                                                        className='dbc',
                                                        id='salesperson-graph-ytd',
                                                    ),
                                                ]
                                            ),
                                        ],
                                        style=tab_card,
                                    )
                                ],
                                sm=12,
                                lg=12,
                            ),
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Card(
                                        [
                                            dbc.CardHeader(
                                                html.Center(
                                                    f'Acumulado de Vendas JAN à {MONTHS_PTBR_ABBR[CURRENT_MONTH]} de {CURRENT_YEAR}'
                                                )
                                            ),
                                            dbc.CardBody(
                                                [
                                                    dcc.Graph(
                                                        className='dbc',
                                                        id='salesperson-graph-ytd-2023',
                                                    )
                                                ]
                                            ),
                                        ],
                                        style=tab_card,
                                    )
                                ],
                                sm=12,
                                lg=6,
                            ),
                            dbc.Col(
                                [
                                    dbc.Card(
                                        [
                                            dbc.CardHeader(
                                                html.Center(
                                                    f'Acumulado de Vendas JAN à {MONTHS_PTBR_ABBR[CURRENT_MONTH]} de {CURRENT_YEAR-1}'
                                                )
                                            ),
                                            dbc.CardBody(
                                                [
                                                    dcc.Graph(
                                                        className='dbc',
                                                        id='salesperson-graph-ytd-2022',
                                                    )
                                                ]
                                            ),
                                        ],
                                        style=tab_card,
                                    )
                                ],
                                sm=12,
                                lg=6,
                            ),
                        ],
                        className='my-3',
                    ),
                ]
            ),
        ],
        id='graph-container',
    )


def get_cols_size(customer_df):
    cdf = customer_df.astype(str)
    for column in cdf.columns:
        cdf[f'len_{column}'] = cdf[column].apply(len)
    return [
        {
            'column': column,
            'len': max([cdf[f'len_{column}'].max(), len(column)]),
        }
        for column in cdf.columns
        if 'len_' not in column
    ]


def get_sales_dashboard(df):
    return html.Div(
        id='maindiv',
        children=[
            html.Div(
                children=[
                    dcc.Tabs(
                        id='tabs',
                        children=[
                            dcc.Tab(
                                label='Métricas',
                                children=get_graph_tab(df['equipe'].unique()),
                            ),
                            dcc.Tab(
                                label='Dados',
                                children=get_data_tab(df, get_cols_size(df)),
                            ),
                        ],
                        className='dbc',
                    ),
                ]
            ),
        ],
    )


menu_head = dbc.Card(
    [
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dbc.Col([html.Legend('KAMI CO')], sm=8),
                        dbc.Col(
                            [
                                html.I(
                                    className='fa fa-chart-line',
                                    style={'font-size': '250%'},
                                )
                            ],
                            sm=4,
                            align='center',
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                ThemeSwitchAIO(
                                    aio_id='theme',
                                    themes=[url_theme1, url_theme2],
                                ),
                                html.Legend('Sales Analytics'),
                            ]
                        )
                    ],
                    style={'margin-top': '5px'},
                ),
            ]
        )
    ]
)


def build_sidebar(components=[]):
    return html.Div(
        [
            dbc.Button(
                html.I(className='fa fa-bars', style={'font-size': '150%'}),
                id='open-sidebar',
                n_clicks=0,
            ),
            dbc.Offcanvas(
                [
                    menu_head,
                    html.Hr(),
                ]
                + components
                + [
                    html.Hr(),
                    html.Center(
                        [
                            dbc.Row(
                                [
                                    dbc.Button(
                                        'Intranet',
                                        href='https://intranet.kamico.com.br/',
                                        target='_blank',
                                    ),
                                ],
                                style={'margin-top': '5px'},
                            ),
                        ]
                    ),
                ],
                id='sidebar',
                is_open=False,
            ),
        ],
        className='my-3',
    )


footer_row = html.Footer(
    [
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.A(
                                            html.I(className='fa fa-question'),
                                            href='https://intranet.kamico.com.br/abrirchamado',
                                            target='_blank',
                                        )
                                    ],
                                    width='auto',
                                ),
                                dbc.Col(
                                    [
                                        html.A(
                                            html.I(className='fa fa-phone'),
                                            href='https://wha.me/5511916654692',
                                            target='_blank',
                                        )
                                    ],
                                    width='auto',
                                ),
                                dbc.Col(
                                    [
                                        html.A(
                                            html.I(className='fa fa-envelope'),
                                            href='mailto:dev@kamico.com.br?subject=Ajuda Com Dashboard',
                                            target='_blank',
                                        )
                                    ],
                                    width='auto',
                                ),
                            ],
                            justify='start',
                        )
                    ],
                    sm=12,
                    md=4,
                    lg=4,
                ),
                dbc.Col(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.P(
                                            [
                                                f"version: {pkg_resources.get_distribution('kami-reports').version} - ",
                                                f'@ {datetime.now().year} Copyright: ',
                                                html.A(
                                                    'KAMI CO.',
                                                    href='https://intranet.kamico.com.br',
                                                    target='_blank',
                                                ),
                                                'IT Team. - developed by',
                                                html.A(
                                                    '@maicondmenezes',
                                                    href='https://github.com/maicondmenezes',
                                                    target='_blank',
                                                ),
                                            ]
                                        )
                                    ],
                                    width='auto',
                                ),
                            ],
                            justify='end',
                        ),
                    ],
                    sm=12,
                    md=4,
                    lg=8,
                ),
            ],
            className='g-2 my-auto',
            style={'margin-top': '7px'},
        ),
    ]
)


def get_page_layout(df):
    return [
        build_sidebar(),
        get_sales_dashboard(df),
        footer_row,
    ]
