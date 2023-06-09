#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from calendar import month_name
from os import getenv

import pandas as pd
from constant import (
    COMERCIAL_WEEK,
    CURRENT_DAY,
    CURRENT_DAY_FOLDER,
    CURRENT_MONTH,
    CURRENT_WEEK_FOLDER,
    CURRENT_WEEKDAY,
    CURRENT_YEAR,
)
from dataframe import (
    build_master_df,
    get_customer_details_df,
    get_monthly_billings_df,
    get_sales_bi_df,
    get_sales_lines_df,
    slice_sales_df_by_team,
)
from dotenv import load_dotenv
from filemanager import delete_old_files
from kami_gdrive import create_folder, gdrive_logger, upload_files_to
from kami_logging import benchmark_with, logging_with
from messages import send_messages_by_group
from unidecode import unidecode

report_bot_logger = logging.getLogger('report_bot')
report_bot_logger.info('Loading Enviroment Variables')
load_dotenv()


@benchmark_with(gdrive_logger)
@logging_with(gdrive_logger)
def create_gdrive_folders():
    current_year_gdrive_folder = create_folder(
        getenv('FOLDER_ID'), str(CURRENT_YEAR)
    )

    current_month_gdrive_folder = create_folder(
        current_year_gdrive_folder, month_name[CURRENT_MONTH]
    )

    current_week_gdrive_folder = create_folder(
        current_month_gdrive_folder, CURRENT_WEEK_FOLDER
    )

    current_day_gdrive_folder = create_folder(
        current_week_gdrive_folder, CURRENT_DAY_FOLDER
    )

    current_day_account_gdrive_folder = create_folder(
        current_day_gdrive_folder, 'financeiro'
    )

    current_day_comercial_gdrive_folder = create_folder(
        current_day_gdrive_folder, 'comercial'
    )

    current_day_master_gdrive_folder = create_folder(
        current_day_comercial_gdrive_folder, 'mestres'
    )

    current_day_products_gdrive_folder = create_folder(
        current_day_comercial_gdrive_folder, 'produtos'
    )

    return {
        'month': current_month_gdrive_folder,
        'comercial': current_day_comercial_gdrive_folder,
        'master': current_day_master_gdrive_folder,
        'products': current_day_products_gdrive_folder,
        'account': current_day_account_gdrive_folder,
    }


def tag_client_overdue_state(row):

    if int(row['dias_atraso']) <= 30:
        return 'em atraso'

    elif int(row['dias_atraso']) > 30:
        return 'inadimplente'


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def calculate_overdue_kpi(customer_df):
    df_overdue = customer_df.copy()
    number_cols = ['dias_atraso', 'valor_devido']
    df_overdue[number_cols] = df_overdue[number_cols].apply(pd.to_numeric)
    df_overdue[number_cols].fillna(0, inplace=True)
    df_overdue['status'] = customer_df.apply(
        lambda row: tag_client_overdue_state(row), axis=1
    )
    df_overdue = df_overdue.loc[df_overdue['dias_atraso'] > 0].dropna(
        subset=['dt_ultima_compra']
    )

    return df_overdue


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def generate_master_report(sales_bi_df, filename='geral'):
    master_df = build_master_df(sales_bi_df)
    if not master_df.empty:
        master_df.to_excel(
            f'data/out/mestre_{filename}.xlsx',
            sheet_name='MESTRE',
            index=False,
        )
        return True
    return False


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def generate_montlhy_report(montlhy_df, filename):
    delete_old_files('data/out')
    montlhy_df.to_excel(
        f'data/out/faturamento_mensal_{filename}.xlsx',
        sheet_name='FATURAMENTO',
        index=False,
    )


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def generate_products_report(products_df, filename='geral'):
    products_df.to_excel(
        f'data/out/produtos_{filename}.xlsx',
        sheet_name='PRODUTOS',
        index=False,
    )


def normalize_name(name):
    return unidecode(
        ''.join(
            ch for ch in name.replace(' ', '_') if ch.isalpha() or ch == '_'
        ).lower()
    )


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def generate_overdue_report(customer_df, filename):
    overdue_df = calculate_overdue_kpi(customer_df)
    overdue_df.to_excel(
        f'data/out/inadimplentes_{filename}.xlsx',
        sheet_name='INADIMPLENTES',
        index=False,
    )


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def generate_future_bills_report(future_bills_df, filename):
    future_bills_df.to_excel(
        f'data/out/contas_a_receber{filename}.xlsx',
        sheet_name='PAGAMENTOS FUTUROS',
        index=False,
    )


def is_comercial_weekday():
    return CURRENT_WEEKDAY in COMERCIAL_WEEK


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def generate_products_reports_by_team(team_products_dfs):
    for team_products_df_dict in team_products_dfs:
        for team_name, team_product_df in team_products_df_dict.items():
            team_name = normalize_name(team_name)
            generate_products_report(team_product_df, team_name)


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def deliver_products_reports(team_products_dfs, current_folders_id):
    generate_products_reports_by_team(team_products_dfs)
    upload_files_to(
        source='data/out',
        destiny=current_folders_id['products'],
    )
    delete_old_files('data/out')


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def generate_master_reports_by_team(team_sales_bi_dfs):
    for team_sales_bi_df_dict in team_sales_bi_dfs:
        for team_name, team_sales_bi_df in team_sales_bi_df_dict.items():
            team_name = normalize_name(team_name)
            generate_master_report(team_sales_bi_df, team_name)


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def deliver_master_reports(team_sales_bi_dfs, current_folders_id):
    generate_master_reports_by_team(team_sales_bi_dfs)
    upload_files_to(
        source='data/out',
        destiny=current_folders_id['master'],
    )
    delete_old_files('data/out')


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def deliver_comercial_reports(current_folders_id):
    products_df = get_sales_lines_df()
    sales_bi_df = get_sales_bi_df(products_df)
    """ generate_products_report(sales_bi_df)
    upload_files_to(
        source='data/out',
        destiny=current_folders_id['products'],
    )
    delete_old_files('data/out')
    generate_master_report(sales_bi_df)
    upload_files_to(
        source='data/out',
        destiny=current_folders_id['master'],
    ) """
    delete_old_files('data/out')
    team_sales_bi_dfs = slice_sales_df_by_team(sales_bi_df)
    deliver_products_reports(team_sales_bi_dfs, current_folders_id)
    deliver_master_reports(team_sales_bi_dfs, current_folders_id)
    send_messages_by_group(
        gdrive_folder_id=current_folders_id['comercial'], group='comercial'
    )


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def generate_account_report(filename):
    customer_df = get_customer_details_df()
    generate_overdue_report(customer_df, filename)


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def deliver_account_reports(current_folders_id):
    generate_account_report('geral')
    upload_files_to(
        source='data/out',
        destiny=current_folders_id['account'],
    )
    delete_old_files('data/out')
    send_messages_by_group(
        gdrive_folder_id=current_folders_id['account'], group='account'
    )


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def deliver_monthly_reports(current_folders_id):
    delete_old_files('data/out')
    montlhy_df = get_monthly_billings_df()
    generate_montlhy_report(montlhy_df, 'geral')
    upload_files_to(
        source='data/out',
        destiny=current_folders_id['month'],
    )
    delete_old_files('data/out')
    send_messages_by_group(
        gdrive_folder_id=current_folders_id['month'], group='board'
    )


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def main():
    report_bot_logger.info('Start Execution.')
    delete_old_files('data/out')
    current_folders_id = create_gdrive_folders()

    if is_comercial_weekday():
        deliver_comercial_reports(current_folders_id)
        deliver_account_reports(current_folders_id)

    if CURRENT_DAY == 1:
        deliver_monthly_reports(current_folders_id)

    delete_old_files('data/out')


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def test():
    current_folders_id = create_gdrive_folders()
    delete_old_files('data/out')
    deliver_monthly_reports(current_folders_id)


if __name__ == '__main__':
    main()
