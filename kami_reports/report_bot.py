#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from calendar import month_name
from os import getenv

import pandas as pd
from dotenv import load_dotenv
from kami_gdrive import create_folder, gdrive_logger, upload_files_to
from kami_logging import benchmark_with, logging_with

from constant import (
    current_day_folder,
    current_month,
    current_week_folder,
    current_year,
    current_weekday,
    comercial_week,
    current_day,
)
from filemanager import delete_old_files
from messages import send_messages_by_group
from dataframe import (
    clean_master_df,
    calculate_master_kpis,
    calculate_seller_kpis,
    build_master_df,
)
from database import (
    get_vw_customer_details,
    get_vw_daily_billings,
    get_vw_monthly_billings,
)

report_bot_logger = logging.getLogger('report_bot')
report_bot_logger.info('Loading Enviroment Variables')
load_dotenv()


@benchmark_with(gdrive_logger)
@logging_with(gdrive_logger)
def create_gdrive_folders():
    current_year_gdrive_folder = create_folder(
        getenv('FOLDER_ID'), str(current_year)
    )

    current_month_gdrive_folder = create_folder(
        current_year_gdrive_folder, month_name[current_month]
    )

    current_week_gdrive_folder = create_folder(
        current_month_gdrive_folder, current_week_folder
    )

    current_day_gdrive_folder = create_folder(
        current_week_gdrive_folder, current_day_folder
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

    current_day_brands_gdrive_folder = create_folder(
        current_day_gdrive_folder, 'marcas'
    )

    return {
        'month': current_month_gdrive_folder,
        'comercial': current_day_comercial_gdrive_folder,
        'master': current_day_master_gdrive_folder,
        'products': current_day_products_gdrive_folder,
        'account': current_day_account_gdrive_folder,
        'board': current_day_brands_gdrive_folder,
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
def generate_master_report(master_df, filename):
    if not master_df.empty:
        master_df = clean_master_df(master_df)
        master_kpi_df = calculate_master_kpis(master_df)
        sellers_kpi_df = calculate_seller_kpis(master_kpi_df)
        sellers_kpi_df.to_excel(
            f'data/out/mestre_{filename}.xlsx',
            sheet_name='MESTRE',
            index=False,
        )


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
def generate_products_report(products_df, filename):
    products_df.to_excel(
        f'data/out/produtos_{filename}.xlsx',
        sheet_name='PRODUTOS',
        index=False,
    )


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def generate_comercial_report(products_df, filename):
    delete_old_files('data/out')
    generate_products_report(products_df, filename)
    master_df = build_master_df(products_df)
    generate_master_report(master_df, filename)


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def generate_overdue_report(customer_df, filename):
    delete_old_files('data/out')
    overdue_df = calculate_overdue_kpi(customer_df)
    overdue_df.to_excel(
        f'data/out/inadimplentes_{filename}.xlsx',
        sheet_name='INADIMPLENTES',
        index=False,
    )


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def generate_future_bills_report(future_bills_df, filename):
    delete_old_files('data/out')
    future_bills_df.to_excel(
        f'data/out/contas_a_receber{filename}.xlsx',
        sheet_name='PAGAMENTOS FUTUROS',
        index=False,
    )


def is_comercial_weekday():
    return current_weekday in comercial_week


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def deliver_comercial_reports(current_folders_id):
    customer_df = get_vw_customer_details()
    products_df = get_vw_daily_billings()
    base_df = products_df.merge(
        customer_df[customer_df.columns[:-1]],
        left_on=['cod_cliente'],
        right_on=['cod_cliente'],
        how='left',
    )
    generate_comercial_report(base_df, 'geral')
    upload_files_to(
        source='data/out',
        destiny=current_folders_id['board'],
    )
    send_messages_by_group(
        gdrive_folder_id=current_folders_id['board'], group='comercial'
    )


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def generate_account_report(customer_df, filename):
    generate_overdue_report(
        customer_df, filename
    )


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def deliver_account_reports(current_folders_id):
    customer_df = get_vw_customer_details()
    generate_account_report(customer_df, 'geral')
    upload_files_to(
        source='data/out',
        destiny=current_folders_id['account'],
    )
    send_messages_by_group(
        gdrive_folder_id=current_folders_id['account'], group='account'
    ) 


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def deliver_monthly_reports(current_folders_id):
    montlhy_df = get_vw_monthly_billings()
    generate_montlhy_report(montlhy_df, 'geral')
    upload_files_to(
        source='data/out',
        destiny=current_folders_id['month'],
    )
    send_messages_by_group(
        gdrive_folder_id=current_folders_id['month'], group='board'
    )


@benchmark_with(report_bot_logger)
def main():
    report_bot_logger.info('Start Execution.')
    current_folders_id = create_gdrive_folders()

    if not is_comercial_weekday():
        deliver_comercial_reports(current_folders_id)
        deliver_account_reports(current_folders_id)

    if current_day == 1:
        deliver_monthly_reports(current_folders_id)

    delete_old_files('data/out')

def test():
    current_folders_id = create_gdrive_folders()
    deliver_account_reports(current_folders_id)

if __name__ == '__main__':
    main()
