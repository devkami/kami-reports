#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from calendar import month_name
from datetime import datetime as dt
from os import getenv, path
from os.path import split as split_filename
from zipfile import ZIP_BZIP2, ZipFile

import pandas as pd
from dotenv import load_dotenv
from kami_filemanager import delete_files_from
from kami_gdrive import create_folder, gdrive_logger, upload_files_to
from kami_logging import benchmark_with, logging_with
from unidecode import unidecode

from kami_reports.constant import (
    CURRENT_DAY_FOLDER,
    CURRENT_MONTH,
    CURRENT_WEEK_FOLDER,
    CURRENT_YEAR,
    ROOT_DIR,
    SOURCE_DIR,
)
from kami_reports.dataframe import (
    build_master_df,
    build_sales_orders_df,
    get_board_billings_df,
    get_customer_details_df,
    get_future_bills_df,
    get_sales_lines_df,
    slice_sales_df_by_team,
)
from kami_reports.messages.messages import (
    get_contacts_from_json,
    send_message_by_group,
)

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


class ReportFormatError(Exception):
    def __init__(self, value: str, message: str):
        self.value = value
        self.message = message
        super().__init__(message)


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def zip_file(filepath: str):
    zip_filepath = ''
    filefolder, filename = split_filename(filepath)
    try:
        zip_filepath = path.join(SOURCE_DIR, f'data/out/zip/{filename}.zip')
        with ZipFile(zip_filepath, 'w') as f:
            f.write(filepath, compress_type=ZIP_BZIP2, compresslevel=9)
    except Exception as e:
        raise e
    return zip_filepath


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def generate_report(
    df: pd.DataFrame,
    type: str,
    filename: str = 'geral',
    zip: bool = False,
    format: str = 'xlsx',
) -> str:
    report_file = ''
    try:
        report_file = path.join(
            SOURCE_DIR, f'data/out/{type}_{filename}.{format}'
        )
        if format == 'xlsx':
            df.to_excel(report_file, sheet_name=str.upper(type), index=False)
        elif format == 'csv':
            df.to_csv(report_file, index=False)
        else:
            raise ReportFormatError(
                value=format,
                message=f"'{format}' Is Not a Valid Format to Generate Reports. Try use format='csv' or format='xlsx'",
            )
        if zip:
            report_file = zip_file(report_file)
    except Exception as e:
        report_bot_logger.exception(f'An error occurred: ', e)
    return report_file


def tag_client_overdue_state(row):

    if int(row['dias_atraso']) <= 30:
        return 'em atraso'

    elif int(row['dias_atraso']) > 30:
        return 'inadimplente'


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def calculate_overdue_kpi(customer_df):
    df_overdue = customer_df.copy()
    df_overdue['status'] = customer_df.apply(
        lambda row: tag_client_overdue_state(row), axis=1
    )
    df_overdue = df_overdue.loc[df_overdue['dias_atraso'] > 0].dropna(
        subset=['dt_ultima_compra']
    )

    return df_overdue


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def generate_master_report(master_df, format='xlsx'):
    return generate_report(df=master_df, type='mestre', format=format)


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def generate_board_report(board_df, format='xlsx'):
    return generate_report(df=board_df, type='faturamento', format=format)


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def generate_products_report(products_df, format='xlsx'):
    return generate_report(df=products_df, type='produtos', format=format)


def normalize_name(name):
    return unidecode(
        ''.join(
            ch for ch in name.replace(' ', '_') if ch.isalpha() or ch == '_'
        ).lower()
    )


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def generate_overdue_report(customer_df):
    overdue_df = calculate_overdue_kpi(customer_df)
    return generate_report(
        df=overdue_df, type='inadimplentes', filename='geral'
    )


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def generate_future_bills_report(future_bills_df):
    return generate_report(
        df=future_bills_df, type='contas_a_receber', filename='geral'
    )


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def generate_products_reports_by_team(team_products_dfs):
    for team_products_df_dict in team_products_dfs:
        for team_name, team_product_df in team_products_df_dict.items():
            team_name = normalize_name(team_name)
            generate_report(
                df=team_product_df, type='produtos', filename=team_name
            )


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def deliver_products_reports(products_df, current_folders_id):
    delete_files_from(path.join(SOURCE_DIR, f'data/out'))
    generate_report(df=products_df, type='produtos')
    team_products_dfs = slice_sales_df_by_team(products_df)
    generate_products_reports_by_team(team_products_dfs)
    upload_files_to(
        source=path.join(SOURCE_DIR, f'data/out'),
        destiny=current_folders_id['products'],
    )
    delete_files_from(path.join(SOURCE_DIR, f'data/out'))


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def generate_master_reports_by_team(team_sales_master_dfs):
    for team_sales_master_df_dict in team_sales_master_dfs:
        for team_name, team_master_df in team_sales_master_df_dict.items():
            team_name = normalize_name(team_name)
            generate_report(
                df=team_master_df, type='mestre', filename=team_name
            )


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def deliver_master_reports(master_df, current_folders_id):
    delete_files_from(path.join(SOURCE_DIR, f'data/out'))
    master_df = master_df.drop_duplicates(keep='first')
    generate_report(df=master_df, type='mestre')
    team_master_dfs = slice_sales_df_by_team(master_df)
    generate_master_report(master_df)
    generate_master_reports_by_team(team_master_dfs)
    upload_files_to(
        source=path.join(SOURCE_DIR, f'data/out'),
        destiny=current_folders_id['master'],
    )
    delete_files_from(path.join(SOURCE_DIR, f'data/out'))


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def deliver_comercial_reports(current_folders_id, contacts):
    sales_lines_df = get_sales_lines_df()
    sales_orders_df = build_sales_orders_df(sales_lines_df)
    master_df = build_master_df(sales_orders_df)
    deliver_products_reports(sales_lines_df, current_folders_id)
    deliver_master_reports(master_df, current_folders_id)
    send_message_by_group(
        template_name='comercial',
        group='test',
        message_dict={
            'subject': 'Faturamento Geral Diário',
            'gdrive_folder_id': current_folders_id['comercial'],
        },
        contacts=contacts,
    )


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def generate_account_report():
    customer_df = get_customer_details_df()
    future_bills_df = get_future_bills_df()
    generate_overdue_report(customer_df)
    generate_future_bills_report(future_bills_df)


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def deliver_account_reports(current_folders_id, contacts):
    delete_files_from(path.join(SOURCE_DIR, f'data/out'))
    generate_account_report()
    upload_files_to(
        source=path.join(SOURCE_DIR, f'data/out'),
        destiny=current_folders_id['account'],
    )
    delete_files_from(path.join(SOURCE_DIR, f'data/out'))
    send_message_by_group(
        template_name='account',
        group='test',
        message_dict={
            'subject': 'Relatórios Financeiros Diários',
            'gdrive_folder_id': current_folders_id['account'],
        },
        contacts=contacts,
    )


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def deliver_board_reports(current_folders_id, contacts):
    delete_files_from(path.join(SOURCE_DIR, f'data/out'))
    board_df = get_board_billings_df()
    generate_board_report(board_df)
    upload_files_to(
        source=path.join(SOURCE_DIR, f'data/out'),
        destiny=current_folders_id['comercial'],
    )
    delete_files_from(path.join(SOURCE_DIR, f'data/out'))
    send_message_by_group(
        template_name='board',
        group='test',
        message_dict={
            'subject': 'Faturamento Geral Diário',
            'gdrive_folder_id': current_folders_id['comercial'],
        },
        contacts=contacts,
    )


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def deliver_reports():
    report_bot_logger.info('Start Execution.')
    current_folders_id = create_gdrive_folders()
    contacts = get_contacts_from_json(
        path.join(SOURCE_DIR, 'messages/contacts.json')
    )
    deliver_account_reports(current_folders_id, contacts)
    deliver_comercial_reports(current_folders_id, contacts)
    deliver_board_reports(current_folders_id, contacts)


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def test():
    report_bot_logger.info('Start Execution.')
    current_folders_id = create_gdrive_folders()
    upload_files_to(
        source=path.join(SOURCE_DIR, f'data/out'),
        destiny=current_folders_id['account'],
    )


@benchmark_with(report_bot_logger)
@logging_with(report_bot_logger)
def main():
    ...


if __name__ == '__main__':
    main()
