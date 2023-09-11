import logging
from datetime import datetime as dt
from datetime import timedelta as td
from typing import Dict, List

import pandas as pd
from constant import (
    COLUMNS_NAMES_HEAD,
    COMPANIES,
    CURRENT_MONTH,
    CURRENT_YEAR,
    MONTHS_PTBR,
    MONTHS_PTBR_ABBR,
    SALE_NOPS,
    SALES_ORDERS_GROUP_COLUMNS,
    SALES_ORDERS_SUM_COLUMNS,
    STARTING_YEAR,
    SUBSIDIZED_NOPS,
    TAGS,
    TEMPLATE_COLS,
    TROUSSEAU_NOPS,
)
from kami_uno_database import (
    get_qy_contact_sellers,
    get_qy_default_seller,
    get_qy_participant_seller,
    get_qy_sales_teams,
    get_vw_board_billings,
    get_vw_customer_details,
    get_vw_future_bills,
    get_vw_sales_lines
)
from kami_logging import benchmark_with, logging_with
from numpy import dtype
from dotenv import load_dotenv
load_dotenv()
dataframe_logger = logging.getLogger('dataframe')

@benchmark_with(dataframe_logger)
@logging_with(dataframe_logger)
def get_sales_lines_df():
    sales_lines_df = get_vw_sales_lines()
    return sales_lines_df


@benchmark_with(dataframe_logger)
@logging_with(dataframe_logger)
def get_customer_details_df():
    customer_details = get_vw_customer_details()
    return customer_details


@benchmark_with(dataframe_logger)
@logging_with(dataframe_logger)
def get_board_billings_df():
    board_billings = get_vw_board_billings()
    return board_billings


@benchmark_with(dataframe_logger)
@logging_with(dataframe_logger)
def get_future_bills_df():
    future_bills = get_vw_future_bills()
    return future_bills


def group_by_cols(df, group_cols) -> pd.DataFrame:
    df = df.sort_values(['ano', 'mes'], ascending=False)
    return df.drop_duplicates(subset=group_cols)


def clean_strtoint_col(df, number_col):
    if dtype(df[number_col]) not in ['int64', 'float64']:
        return df[number_col].str.extract(pat='(\d+)', expand=False)


def filter_orders_by_nops(orders_df, nops) -> pd.DataFrame:
    return orders_df.loc[orders_df.nop.isin(nops)]


def flat_and_tag_motnh_and_year_cols(df, tag='') -> pd.DataFrame:
    tag = f'_{tag}' if tag else tag
    df.columns = [
        f'{MONTHS_PTBR_ABBR.get(int(x[1]))}_{x[0]}{tag}' for x in df.columns
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
            filter_orders_by_nops(orders_df, SALE_NOPS), col='cod_pedido'
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
        f'{MONTHS_PTBR_ABBR[p.month]}_{p.year}_vendas'
        for p in period
        if f'{MONTHS_PTBR_ABBR[p.month]}_{p.year}_vendas'
        in count_sales_df.columns
    ]
    return count_sales_df[period_cols].sum(axis=1)


def sum_net_by_costumer(orders_df) -> pd.DataFrame:
    return flat_and_tag_motnh_and_year_cols(
        sum_col_by_costumer(
            orders_df=filter_orders_by_nops(orders_df, SALE_NOPS),
            col='valor_nota',
        ),
        tag='liquido',
    )


def sum_gross_by_costumer(orders_df) -> pd.DataFrame:
    return flat_and_tag_motnh_and_year_cols(
        sum_col_by_costumer(
            orders_df=filter_orders_by_nops(orders_df, SALE_NOPS),
            col='total_bruto',
        ),
        tag='bruto',
    )


def sum_trousseau_by_costumer(orders_df) -> pd.DataFrame:
    return flat_and_tag_motnh_and_year_cols(
        sum_col_by_costumer(
            filter_orders_by_nops(orders_df, TROUSSEAU_NOPS), col='valor_nota'
        ),
        tag='enxoval',
    )


def sum_subsidized_by_costumer(orders_df) -> pd.DataFrame:
    return flat_and_tag_motnh_and_year_cols(
        sum_col_by_costumer(
            filter_orders_by_nops(orders_df, SUBSIDIZED_NOPS), col='valor_nota'
        ),
        tag='bonificado',
    )


def sum_discount_by_costumer(orders_df) -> pd.DataFrame:
    return flat_and_tag_motnh_and_year_cols(
        sum_col_by_costumer(
            filter_orders_by_nops(orders_df, SALE_NOPS), 'desconto_pedido'
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
        f'{MONTHS_PTBR_ABBR[p.month]}_{p.year}_liquido'
        for p in period
        if f'{MONTHS_PTBR_ABBR[p.month]}_{p.year}_liquido' in orders_df.columns
    ]
    return orders_df[period_cols].astype('float').sum(axis=1)


@benchmark_with(dataframe_logger)
@logging_with(dataframe_logger)
def calculate_master_df(sales_orders_df: pd.DataFrame) -> pd.DataFrame:
    master_df = pd.DataFrame()
    index_cols = ['cod_cliente', 'cod_marca']
    customer_details_df = get_customer_details_df()
    head_df = sales_orders_df.merge(
        customer_details_df, on='cod_cliente', how='outer'
    )[COLUMNS_NAMES_HEAD]
    head_df['cep'] = clean_strtoint_col(head_df, 'cep')
    trousseau_df = sum_trousseau_by_costumer(sales_orders_df)
    subsidized_df = sum_subsidized_by_costumer(sales_orders_df)
    discount_df = sum_discount_by_costumer(sales_orders_df)
    net_df = sum_net_by_costumer(sales_orders_df)
    gross_df = sum_gross_by_costumer(sales_orders_df)

    df_list = [net_df, discount_df, gross_df, subsidized_df, trousseau_df]
    dfs = [df for df in df_list if not df.empty]

    if len(dfs) > 0:
        master_df_kpis = pd.concat(dfs, ignore_index=False, axis=1)
        master_df = head_df.merge(
            master_df_kpis.reset_index(), on=index_cols, how='outer'
        )
        master_df = calculate_master_kpis(clean_master_df(master_df))

    return master_df


@benchmark_with(dataframe_logger)
@logging_with(dataframe_logger)
def add_sellers_on_sales_df(sales: pd.DataFrame) -> pd.DataFrame:
    sellers_df = get_sellers_details()
    sales_sellers_df = sellers_df.merge(
        sales,
        on='cod_cliente',
        how='inner',
    )
    return sales_sellers_df


@benchmark_with(dataframe_logger)
@logging_with(dataframe_logger)
def add_sales_teams_on_sellers_df(sellers_df: pd.DataFrame) -> pd.DataFrame:
    sales_teams_df = get_qy_sales_teams()
    master_sales_teams_df = sales_teams_df[
        ['cod_colaborador', 'equipe']
    ].merge(
        sellers_df,
        on='cod_colaborador',
        how='inner',
    )
    return master_sales_teams_df


@benchmark_with(dataframe_logger)
@logging_with(dataframe_logger)
def build_master_df(sales_orders_df: pd.DataFrame) -> pd.DataFrame:
    master_sales_teams_df = pd.DataFrame()
    try:
        master_df = calculate_master_df(sales_orders_df)
        master_sellers_df = add_sellers_on_sales_df(master_df)
        master_sales_teams_df = add_sales_teams_on_sellers_df(
            master_sellers_df
        )
    except Exception as e:
        dataframe_logger.exception(f'An error occurred: ', e)
    return master_sales_teams_df.drop_duplicates(keep='first')


def get_tagged_columns():
    period = pd.period_range(
        start=str(STARTING_YEAR),
        end=f'{CURRENT_YEAR}-{CURRENT_MONTH}',
        freq='M',
    )
    return [
        f'{MONTHS_PTBR_ABBR[p.month]}_{p.year}{tag}'
        for p in period
        for tag in TAGS
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


@benchmark_with(dataframe_logger)
@logging_with(dataframe_logger)
def calculate_accumulated_past_years(master_df):
    df = master_df
    month_period = pd.period_range(
        start=str(STARTING_YEAR), end=f'{CURRENT_YEAR - 1}-12', freq='M'
    )
    year_period = pd.period_range(
        start=str(STARTING_YEAR), end=str(CURRENT_YEAR - 1), freq='Y'
    )
    for y in year_period:
        for tag in TAGS:
            accumulated = [
                f'{MONTHS_PTBR_ABBR[p.month]}_{y.year}{tag}'
                for p in month_period
                if p.year == y.year
                and f'{MONTHS_PTBR_ABBR[p.month]}_{y.year}{tag}' in df.columns
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


@benchmark_with(dataframe_logger)
@logging_with(dataframe_logger)
def calculate_year_to_date(master_df):
    df = master_df
    this_year = pd.period_range(
        start=str(CURRENT_YEAR),
        end=f'{CURRENT_YEAR}-{CURRENT_MONTH -1}',
        freq='M',
    )
    for tag in TAGS:
        this_year_accumulated = [
            f'{ MONTHS_PTBR_ABBR[p.month]}_{p.year}{tag}'
            for p in this_year
            if f'{ MONTHS_PTBR_ABBR[p.month]}_{p.year}{tag}' in df.columns
        ]
        last_year_accumulated = [
            f'{ MONTHS_PTBR_ABBR[p.month]}_{p.year-1}{tag}'
            for p in this_year
            if f'{ MONTHS_PTBR_ABBR[p.month]}_{p.year-1}{tag}' in df.columns
        ]

        if tag == '_liquido':
            df[f'FAT. LÍQ. {CURRENT_YEAR} YTD'] = df[
                this_year_accumulated
            ].sum(axis=1) - df[last_year_accumulated].sum(axis=1)
        if tag == '_desconto':
            df[f'TT  DESC. {CURRENT_YEAR} YTD'] = (
                df[this_year_accumulated].sum(axis=1) * -1
            ) - (df[last_year_accumulated].sum(axis=1) * -1)
        if tag == '_bonificado':
            df[f'TT BONIFICADO {CURRENT_YEAR} YTD'] = df[
                this_year_accumulated
            ].sum(axis=1) - df[last_year_accumulated].sum(axis=1)
        if tag == '_enxoval':
            df[f'TT ENXOVAL {CURRENT_YEAR} YTD'] = df[
                this_year_accumulated
            ].sum(axis=1) - df[last_year_accumulated].sum(axis=1)

    df[f'FAT.  BRUTO {CURRENT_YEAR} YTD'] = (
        df[f'FAT. LÍQ. {CURRENT_YEAR} YTD']
        + df[f'TT  DESC. {CURRENT_YEAR} YTD']
    )

    df[f'DESC. % {CURRENT_YEAR} YTD'] = (
        df[f'TT  DESC. {CURRENT_YEAR} YTD']
        / df[f'FAT.  BRUTO {CURRENT_YEAR} YTD']
    )

    df[f'BONIF. % {CURRENT_YEAR} YTD'] = (
        df[f'TT BONIFICADO {CURRENT_YEAR} YTD']
        / df[f'FAT. LÍQ. {CURRENT_YEAR} YTD']
    )

    return df


@benchmark_with(dataframe_logger)
@logging_with(dataframe_logger)
def calculate_master_kpis(master_df):
    past_years_df = calculate_accumulated_past_years(master_df)
    year_to_date_df = calculate_year_to_date(past_years_df)

    return year_to_date_df


@benchmark_with(dataframe_logger)
@logging_with(dataframe_logger)
def get_sales_bi_df(sales_lines_df):
    sales_bi_df = pd.DataFrame()
    customer_df = get_customer_details_df()
    sales_bi_df = sales_lines_df.merge(
        customer_df,
        left_on=['cod_cliente'],
        right_on=['cod_cliente'],
        how='left',
    )
    sales_bi_df['cep'] = clean_strtoint_col(sales_bi_df, 'cep')

    return sales_bi_df


@benchmark_with(dataframe_logger)
@logging_with(dataframe_logger)
def get_template_df(df) -> pd.DataFrame:
    return df[TEMPLATE_COLS]


def get_opt_list_from_cols(
    df_template, value_col, label_col, label_sort=True
) -> List[Dict]:
    sort_col = label_col if label_sort else value_col
    option_list = [{'value': 0, 'label': 'Todos'}]
    df_opt = (
        df_template[[label_col, value_col]]
        .drop_duplicates(subset=[value_col])
        .dropna()
        .sort_values(by=[sort_col])
    )
    opt_list = list(zip(*map(df_opt.get, df_opt)))
    option_list.extend(
        [{'value': value, 'label': label} for label, value in opt_list]
    )

    return option_list


def get_opt_list_from_col(df_template, col) -> List[Dict]:
    option_list = [{'value': 0, 'label': 'Todos'}]
    opt_list = (
        df_template[[col]]
        .drop_duplicates(subset=[col])
        .sort_values(by=[col])[col]
        .dropna()
        .unique()
    )
    option_list.extend([{'value': opt, 'label': opt} for opt in opt_list])

    return option_list


def get_month_opt_list(df_template) -> List[Dict]:
    df_template['mes_abbr'] = df_template['mes'].apply(
        lambda x: MONTHS_PTBR[x]
    )
    months_list = get_opt_list_from_cols(
        df_template, value_col='mes', label_col='mes_abbr', label_sort=False
    )
    return months_list


def get_year_opt_list(df_template) -> List[Dict]:
    return get_opt_list_from_col(df_template, 'ano')


def get_value_by_id(dict_list, key):
    for item in dict_list:
        if item['value'] == key:
            return item['label']
    return None


def get_salesperson_opt_list(df_template) -> List[Dict]:
    return get_opt_list_from_cols(
        df_template, value_col='cod_colaborador', label_col='nome_colaborador'
    )


def get_branch_opt_list(df_template) -> List[Dict]:
    return get_opt_list_from_col(df_template, 'ramo_atividade')


def get_uf_opt_list(df_template) -> List[Dict]:
    return get_opt_list_from_col(df_template, 'uf')


def get_city_opt_list(df_template) -> List[Dict]:
    return get_opt_list_from_col(df_template, 'cidade')


def get_district_opt_list(df_template) -> List[Dict]:
    return get_opt_list_from_col(df_template, 'bairro')


def get_status_opt_list(df_template) -> List[Dict]:
    return get_opt_list_from_cols(
        df_template, value_col='cod_situacao', label_col='desc_situacao'
    )


def get_sub_prod_group_opt_list(df_template) -> List[Dict]:
    return get_opt_list_from_cols(
        df_template,
        value_col='cod_grupo_produto',
        label_col='desc_grupo_produto',
    )


def get_prod_group_opt_list(df_template) -> List[Dict]:
    return get_opt_list_from_cols(
        df_template, value_col='cod_grupo_pai', label_col='desc_grupo_pai'
    )


def get_prod_band_opt_list(df_template) -> List[Dict]:
    return get_opt_list_from_cols(
        df_template, value_col='cod_marca', label_col='desc_marca'
    )


def get_company_opt_list(df_template) -> List[Dict]:
    df_template['nome_empresa'] = (
        df_template.loc[df_template['empresa_nota_fiscal'] > 0][
            'empresa_nota_fiscal'
        ]
        .dropna()
        .apply(lambda x: COMPANIES[x])
    )
    return get_opt_list_from_cols(
        df_template,
        value_col='empresa_nota_fiscal',
        label_col='nome_empresa',
        label_sort=False,
    )


def get_key_from_value(dictionary, value):
    keys = [key for key, val in dictionary.items() if val == value]
    if keys:
        return keys[0]
    return None


def get_opt_lists_from_df(df, cols) -> Dict:
    opt_lists = {}
    df_template = get_template_df(df)
    all_lists = {
        'month': get_month_opt_list(df_template),
        'year': get_year_opt_list(df_template),
        'salesperson': get_salesperson_opt_list(df_template),
        'branch': get_branch_opt_list(df_template),
        'uf': get_uf_opt_list(df_template),
        'city': get_city_opt_list(df_template),
        'district': get_district_opt_list(df_template),
        'status': get_status_opt_list(df_template),
        'sub_prod_group': get_sub_prod_group_opt_list(df_template),
        'prod_group': get_prod_group_opt_list(df_template),
        'prod_band': get_prod_band_opt_list(df_template),
        'company': get_company_opt_list(df_template),
    }
    return opt_lists


def slice_sales_df_by_team(sales_df: pd.DataFrame) -> List[pd.DataFrame]:
    sales_df_list = []
    sales_df = sales_df.drop_duplicates(keep='first')
    for team in sales_df['equipe'].unique():
        sales_df_list.append({team: sales_df.loc[sales_df['equipe'] == team]})
    return sales_df_list


def add_ytd_cols(master_df):
    for year in range(CURRENT_YEAR - 1, CURRENT_YEAR + 1):

        period = pd.period_range(
            start=f'1-{year}',
            end=f'{CURRENT_MONTH}-{year}',
            freq='M',
        )
        ytd_last_year_cols = [
            f'{MONTHS_PTBR_ABBR[p.month]}_{p.year}_liquido'
            for p in period
            if f'{MONTHS_PTBR_ABBR[p.month]}_{p.year}_liquido'
            in master_df.columns
        ]
        master_df[f'ytd_{year}'] = master_df[ytd_last_year_cols].sum(axis=1)
    return master_df


def get_sellers_details() -> pd.DataFrame:
    sellers_details_df = pd.DataFrame()
    try:
        sellers_details_df = get_qy_contact_sellers()[['id', 'name']].rename(
            columns={'id': 'cod_colaborador', 'name': 'nome_colaborador'}
        )
        sellers_customers_df = pd.concat(
            [get_qy_default_seller(), get_qy_participant_seller()],
            ignore_index=True,
        )
        sellers_details_df = sellers_customers_df.merge(
            sellers_details_df,
            on=['cod_colaborador'],
            how='left',
        )
    except Exception as e:
        dataframe_logger.exception('An unknow error occurred:', e)
    return sellers_details_df


def group_sales_lines(
    sales_lines_df: pd.DataFrame, group_cols: List[str], sum_cols: List[str]
) -> pd.DataFrame:
    sales_orders_df = pd.DataFrame()
    """
    Group and aggregate sales data based on specified columns.

    Args:
        sales_lines_df (pd.DataFrame): The original DataFrame with sales data.
        group_cols (List[str]): List of columns to be used for grouping.
        sum_cols (List[str]): List of columns to be summed.

    Returns:
        pd.DataFrame: The resulting DataFrame with aggregated sales orders.
    """
    try:
        sales_orders_df = (
            sales_lines_df.groupby(group_cols)[sum_cols].sum().reset_index()
        )
    except Exception as e:
        dataframe_logger.exception(f'An error occurred: ', e)
    return sales_orders_df


@benchmark_with(dataframe_logger)
@logging_with(dataframe_logger)
def build_sales_orders_df(sales_lines_df: pd.DataFrame) -> pd.DataFrame:
    sales_orders_df = pd.DataFrame()
    try:
        sales_orders_df = group_sales_lines(
            sales_lines_df,
            SALES_ORDERS_GROUP_COLUMNS,
            SALES_ORDERS_SUM_COLUMNS,
        )
    except Exception as e:
        dataframe_logger.exception(f'An error occurred: ', e)
    return sales_orders_df
