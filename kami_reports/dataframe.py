import logging
import pandas as pd
from constant import (
    columns_names_head,
    sale_nops,
    trousseau_nops,
    subsidized_nops,
    months_ptbr_abbr,
    starting_year,
    current_year,
    tags,
    current_month,
)
from datetime import datetime as dt, timedelta as td
from numpy import dtype
from kami_logging import benchmark_with, logging_with

dataframe = logging.getLogger('dataframe')


def group_by_orders(df, order_cols) -> pd.DataFrame:
    df = df.sort_values(['ano', 'mes'], ascending=False)
    return df.drop_duplicates(subset=order_cols)


def clean_strtoint_col(df, number_col):
    if dtype(df[number_col]) not in ['int64', 'float64']:
        return df[number_col].str.extract(pat='(\d+)', expand=False)


def convert_number_cols(df):
    str_to_int_cols = [
        'cep',
        'numero',
        'empresa_nota_fiscal',
        'cod_colaborador',
        'cod_pedido',
        'nr_ped_compra_cli',
        'cod_situacao',
        'cod_forma_pagto',
        'cod_grupo_produto',
        'cod_grupo_pai',
        'cod_marca',
    ]
    int_cols = ['dias_atraso', 'qtd', 'dias_sem_compra']
    float_cols = [
        'valor_devido',
        'custo_total',
        'custo_kami',
        'preco_unit_original',
        'preco_total_original',
        'margem_bruta',
        'preco_total',
        'preco_desconto_rateado',
        'vl_total_pedido',
        'desconto_pedido',
        'valor_nota',
        'total_bruto',
    ]

    for str_to_int_col in str_to_int_cols:
        df[str_to_int_col] = clean_strtoint_col(df, str_to_int_col)

    for int_col in int_cols:
        df[int_col] = df[int_col].fillna(0).astype(int)

    for float_col in float_cols:
        df[float_col] = df[float_col].fillna(0).astype(float)

    return df


def clean_orders_df(orders_df) -> pd.DataFrame:
    int_cols = [
        'numero',
        'empresa_nota_fiscal',
        'dias_atraso',
        'cod_colaborador',
        'cod_pedido',
        'nr_ped_compra_cli',
        'cod_situacao',
        'cod_forma_pagto',
        'cod_produto',
        'cod_grupo_produto',
        'cod_grupo_pai',
        'cod_marca',
        'qtd',
    ]
    float_cols = [
        'valor_devido',
        'custo_total',
        'custo_kami',
        'preco_unit_original',
        'preco_total_original',
        'margem_bruta',
        'preco_total',
        'preco_desconto_rateado',
        'vl_total_pedido',
        'desconto_pedido',
        'valor_nota',
        'total_bruto',
    ]
    return convert_number_cols(orders_df, int_cols, float_cols)


@benchmark_with(dataframe)
@logging_with(dataframe)
def build_orders_df(df):
    return group_by_orders(convert_number_cols(df), order_cols=['cod_pedido'])


def filter_orders_by_nops(orders_df, nops) -> pd.DataFrame:
    return orders_df.loc[orders_df.nop.isin(nops)]


def flat_and_tag_motnh_and_year_cols(df, tag='') -> pd.DataFrame:
    tag = f'_{tag}' if tag else tag
    df.columns = [
        f'{months_ptbr_abbr.get(int(x[1]))}_{x[0]}{tag}' for x in df.columns
    ]
    return df


def calculate_col_by_costumer(orders_df, col, operation) -> pd.DataFrame:
    orders_df.sort_values(['ano', 'mes'], ascending=False)
    return orders_df.pivot_table(
        index=['cod_cliente', 'cod_marca'],
        columns=['ano', 'mes'],
        values=col,
        aggfunc=operation,
        fill_value=0,
    )


def count_col_by_costumer(orders_df, col) -> pd.DataFrame:
    return calculate_col_by_costumer(orders_df, col, 'count')


def sum_col_by_costumer(orders_df, col) -> pd.DataFrame:
    return calculate_col_by_costumer(orders_df, col, 'sum')


def count_sales_by_costumer(orders_df) -> pd.DataFrame:
    return flat_and_tag_motnh_and_year_cols(
        count_col_by_costumer(
            filter_orders_by_nops(orders_df, sale_nops), col='cod_pedido'
        ),
        tag='vendas',
    )


def count_sales_by_costumer_and_period(orders_df, start_date, end_date, freq):
    count_sales_df = count_sales_by_costumer(orders_df)
    period = pd.period_range(
        start=start_date,
        end=end_date,
        freq=freq,
    )
    period_cols = [
        f'{months_ptbr_abbr[p.month]}_{p.year}_vendas'
        for p in period
        if f'{months_ptbr_abbr[p.month]}_{p.year}_vendas'
        in count_sales_df.columns
    ]
    return count_sales_df[period_cols].sum(axis=1)


def sum_net_by_costumer(orders_df) -> pd.DataFrame:
    return flat_and_tag_motnh_and_year_cols(
        sum_col_by_costumer(
            orders_df=filter_orders_by_nops(orders_df, sale_nops),
            col='valor_nota',
        ),
        tag='liquido',
    )


def sum_gross_by_costumer(orders_df) -> pd.DataFrame:
    return flat_and_tag_motnh_and_year_cols(
        sum_col_by_costumer(
            orders_df=filter_orders_by_nops(orders_df, sale_nops),
            col='total_bruto',
        ),
        tag='bruto',
    )


def sum_trousseau_by_costumer(orders_df) -> pd.DataFrame:
    return flat_and_tag_motnh_and_year_cols(
        sum_col_by_costumer(
            filter_orders_by_nops(orders_df, trousseau_nops), col='valor_nota'
        ),
        tag='enxoval',
    )


def sum_subsidized_by_costumer(orders_df) -> pd.DataFrame:
    return flat_and_tag_motnh_and_year_cols(
        sum_col_by_costumer(
            filter_orders_by_nops(orders_df, subsidized_nops), col='valor_nota'
        ),
        tag='bonificado',
    )


def sum_discount_by_costumer(orders_df) -> pd.DataFrame:
    return flat_and_tag_motnh_and_year_cols(
        sum_col_by_costumer(
            filter_orders_by_nops(orders_df, sale_nops), 'desconto_pedido'
        ),
        tag='desconto',
    )


def sum_sales_by_costumer_and_period(orders_df, start_date, end_date, freq):
    period = pd.period_range(
        start=start_date,
        end=end_date,
        freq=freq,
    )
    period_cols = [
        f'{months_ptbr_abbr[p.month]}_{p.year}_liquido'
        for p in period
        if f'{months_ptbr_abbr[p.month]}_{p.year}_liquido' in orders_df.columns
    ]
    return orders_df[period_cols].astype('float').sum(axis=1)


@benchmark_with(dataframe)
@logging_with(dataframe)
def build_master_df(df) -> pd.DataFrame:
    master_df = pd.DataFrame()
    orders_df = build_orders_df(df)
    head_df = group_by_orders(df, order_cols=['cod_cliente', 'cod_marca'])[
        columns_names_head
    ]
    index_cols = ['cod_cliente', 'cod_marca']
    trousseau_df = sum_trousseau_by_costumer(orders_df)
    subsidized_df = sum_subsidized_by_costumer(orders_df)
    discount_df = sum_discount_by_costumer(orders_df)
    net_df = sum_net_by_costumer(orders_df)
    gross_df = sum_gross_by_costumer(orders_df)
    amount_sales_df = count_sales_by_costumer(orders_df)
    end_date = f'{dt.now().year}-{dt.now().month - 1}'

    net_df['qtd_total_compras'] = count_sales_by_costumer_and_period(
        df,
        start_date=starting_year,
        end_date=dt.now().strftime('%Y-%m'),
        freq='M',
    )
    start_date = dt.now() - td(days=180)
    net_df['qtd_compras_semestre'] = count_sales_by_costumer_and_period(
        df,
        start_date=start_date.strftime('%Y-%m'),
        end_date=end_date,
        freq='M',
    )
    net_df['total_compras_semestre'] = sum_sales_by_costumer_and_period(
        net_df,
        start_date=start_date.strftime('%Y-%m'),
        end_date=end_date,
        freq='M',
    )
    start_date = dt.now() - td(days=90)
    net_df['total_compras_trimestre'] = sum_sales_by_costumer_and_period(
        net_df,
        start_date=start_date.strftime('%Y-%m'),
        end_date=end_date,
        freq='M',
    )
    start_date = dt.now() - td(days=60)
    net_df['total_compras_bimestre'] = sum_sales_by_costumer_and_period(
        net_df,
        start_date=start_date.strftime('%Y-%m'),
        end_date=end_date,
        freq='M',
    )
    df_list = [
        net_df,
        discount_df,
        gross_df,
        subsidized_df,
        trousseau_df,
        amount_sales_df,
    ]
    dfs = [df for df in df_list if not df.empty]

    if len(dfs) > 0:
        master_kpis_df = pd.concat(dfs, ignore_index=False, axis=1)
        master_df = head_df.merge(
            master_kpis_df.reset_index(), on=index_cols, how='outer'
        )

    return master_df


def get_tagged_columns():
    period = pd.period_range(
        start=starting_year, end=f'{current_year}-{current_month}', freq='M'
    )
    return [
        f'{months_ptbr_abbr[p.month]}_{p.year}{tag}'
        for p in period
        for tag in tags
    ]


def clean_master_df(df):
    number_cols = [
        'dias_atraso',
        'valor_devido',
        'qtd_total_compras',
        'qtd_compras_semestre',
        'total_compras_bimestre',
        'total_compras_trimestre',
        'total_compras_semestre',
    ] + get_tagged_columns()
    master_df = df.dropna(subset=['dt_ultima_compra', 'dt_primeira_compra'])
    for number_col in number_cols:
        if number_col in master_df.columns:
            master_df[number_col] = master_df[number_col].apply(pd.to_numeric)
            master_df[number_col].fillna(0, inplace=True)

    return master_df


@benchmark_with(dataframe)
@logging_with(dataframe)
def calculate_accumulated_past_years(master_df):
    df = master_df
    month_period = pd.period_range(
        start=starting_year, end=f'{current_year - 1}-12', freq='M'
    )
    year_period = pd.period_range(
        start=starting_year, end=current_year - 1, freq='Y'
    )
    for y in year_period:
        for tag in tags:
            accumulated = [
                f'{months_ptbr_abbr[p.month]}_{y.year}{tag}'
                for p in month_period
                if p.year == y.year
                and f'{months_ptbr_abbr[p.month]}_{y.year}{tag}' in df.columns
            ]
            if tag == '_liquido':
                df[f'FAT. LÍQ. {y.year}'] = df[accumulated].sum(axis=1)
            if tag == '_desconto':
                df[f'TT  DESC. {y.year}'] = df[accumulated].sum(axis=1) * -1
            if tag == '_bonificado':
                df[f'TT BONIFICADO {y.year}'] = df[accumulated].sum(axis=1)
            if tag == '_enxoval':
                df[f'TT ENXOVAL {y.year}'] = df[accumulated].sum(axis=1)

        df[f'FAT.  BRUTO {y.year}'] = (
            df[f'FAT. LÍQ. {y.year}'] + df[f'TT  DESC. {y.year}']
        )
        df[f'DESC. % {y.year}'] = (
            df[f'TT  DESC. {y.year}'] / df[f'FAT.  BRUTO {y.year}']
        )
        df[f'BONIF. % {y.year}'] = (
            df[f'TT BONIFICADO {y.year}'] / df[f'FAT. LÍQ. {y.year}']
        )
    return df


@benchmark_with(dataframe)
@logging_with(dataframe)
def calculate_year_to_date(master_df):
    df = master_df
    this_year = pd.period_range(
        start=current_year, end=f'{current_year}-{current_month -1}', freq='M'
    )
    for tag in tags:
        this_year_accumulated = [
            f'{ months_ptbr_abbr[p.month]}_{p.year}{tag}'
            for p in this_year
            if f'{ months_ptbr_abbr[p.month]}_{p.year}{tag}' in df.columns
        ]
        last_year_accumulated = [
            f'{ months_ptbr_abbr[p.month]}_{p.year-1}{tag}'
            for p in this_year
            if f'{ months_ptbr_abbr[p.month]}_{p.year-1}{tag}' in df.columns
        ]

        if tag == '_liquido':
            df[f'FAT. LÍQ. {current_year} YTD'] = df[
                this_year_accumulated
            ].sum(axis=1) - df[last_year_accumulated].sum(axis=1)
        if tag == '_desconto':
            df[f'TT  DESC. {current_year} YTD'] = (
                df[this_year_accumulated].sum(axis=1) * -1
            ) - (df[last_year_accumulated].sum(axis=1) * -1)
        if tag == '_bonificado':
            df[f'TT BONIFICADO {current_year} YTD'] = df[
                this_year_accumulated
            ].sum(axis=1) - df[last_year_accumulated].sum(axis=1)
        if tag == '_enxoval':
            df[f'TT ENXOVAL {current_year} YTD'] = df[
                this_year_accumulated
            ].sum(axis=1) - df[last_year_accumulated].sum(axis=1)

    df[f'FAT.  BRUTO {current_year} YTD'] = (
        df[f'FAT. LÍQ. {current_year} YTD']
        + df[f'TT  DESC. {current_year} YTD']
    )

    df[f'DESC. % {current_year} YTD'] = (
        df[f'TT  DESC. {current_year} YTD']
        / df[f'FAT.  BRUTO {current_year} YTD']
    )

    df[f'BONIF. % {current_year} YTD'] = (
        df[f'TT BONIFICADO {current_year} YTD']
        / df[f'FAT. LÍQ. {current_year} YTD']
    )

    return df


@benchmark_with(dataframe)
@logging_with(dataframe)
def calculate_master_kpis(master_df):
    past_years_df = calculate_accumulated_past_years(master_df)
    year_to_date_df = calculate_year_to_date(past_years_df)

    return year_to_date_df