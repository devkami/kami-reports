#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from os import getenv, system, path
from typing import Dict, List

import pandas as pd
from constant import (
    BILLINGS_DATETIME_COLS,
    CUSTOMER_DETAILS_DATETIME_COLS,
    CUSTOMER_DETAILS_NUM_COLS,
    CUSTOMER_DETAILS_SCRIPT,
    DAILY_BILLINGS_NUM_COLS,
    DAILY_BILLINGS_SCRIPT,
    MONTHLY_BILLINGS_NUM_COLS,
    MONTHLY_BILLINGS_SCRIPT,
    FUTURE_BILLS_SCRIPT,
    FUTURE_BILLS_DATETIME_COLS,
    FUTURE_BILLS_NUM_COLS
)
from dotenv import load_dotenv
from filemanager import get_file_list_from
from kami_logging import benchmark_with, logging_with
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

db_connector_logger = logging.getLogger('database')
load_dotenv()
connection_url = URL.create(
    'mysql+pymysql',
    username=getenv('DB_USER'),
    password=getenv('DB_USER_PASSWORD'),
    host=getenv('DB_HOST'),
    database='db_uc_kami',
)


@benchmark_with(db_connector_logger)
@logging_with(db_connector_logger)
def execute_query(sql_file):
    db_connector_logger.info(f'execute {sql_file}')
    system(
        f"mysql -u {getenv('DB_USER')} -p{getenv('DB_USER_PASSWORD')} -h {getenv('DB_HOST')} -P {getenv('DB_PORT')} < {sql_file}"
    )


@benchmark_with(db_connector_logger)
@logging_with(db_connector_logger)
def execute_queries(sql_files):
    sql_files.sort()
    if len(sql_files):
        for sql_file in sql_files:
            execute_query(sql_file)


@benchmark_with(db_connector_logger)
@logging_with(db_connector_logger)
def update_database_views():
    views_script = get_file_list_from('data/in')
    execute_queries(views_script)


@benchmark_with(db_connector_logger)
@logging_with(db_connector_logger)
def get_dataframe_from_sql_query(
    sql_script: str, date_cols: List[str] = None, cols_types: Dict = None
) -> pd.DataFrame:
    sql_engine = create_engine(connection_url, pool_recycle=3600)
    sql_engine.connect()  
    df = pd.read_sql_query(
        str(sql_script), sql_engine, parse_dates=date_cols, dtype=cols_types
    )
    return pd.DataFrame(df)

@benchmark_with(db_connector_logger)
@logging_with(db_connector_logger)
def get_dataframe_from_sql_file(
    sql_file: str, date_cols: List[str] = None, cols_types: Dict = None
) -> pd.DataFrame:
    query = open(sql_file, 'r')
    sql_engine = create_engine(connection_url, pool_recycle=3600)
    sql_engine.connect()  
    df = pd.read_sql(
        query.read(), sql_engine, parse_dates=date_cols, dtype=cols_types
    )
    return pd.DataFrame(df)

@benchmark_with(db_connector_logger)
@logging_with(db_connector_logger)
def get_dataframe_from_sql(
    sql_query: str, date_cols: List[str] = None, cols_types: Dict = None
) -> pd.DataFrame:
    if path.exists(sql_query):
        return get_dataframe_from_sql_file(sql_query, date_cols, cols_types)
    return get_dataframe_from_sql_query(sql_query, date_cols, cols_types)


@benchmark_with(db_connector_logger)
@logging_with(db_connector_logger)
def get_dataframe_from_sql_table(
    tablename: str, date_cols: List[str] = None
) -> pd.DataFrame:
    sql_engine = create_engine(connection_url, pool_recycle=3600)
    sql_engine.connect()
    df = pd.read_sql_table(tablename, sql_engine, parse_dates=date_cols)
    return pd.DataFrame(df)


@benchmark_with(db_connector_logger)
@logging_with(db_connector_logger)
def get_vw_monthly_billings() -> pd.DataFrame:
    return get_dataframe_from_sql_query(
        MONTHLY_BILLINGS_SCRIPT,
        date_cols=BILLINGS_DATETIME_COLS,
        cols_types=MONTHLY_BILLINGS_NUM_COLS,
    )


@benchmark_with(db_connector_logger)
@logging_with(db_connector_logger)
def get_vw_daily_billings() -> pd.DataFrame:
    return get_dataframe_from_sql_query(
        DAILY_BILLINGS_SCRIPT,
        date_cols=BILLINGS_DATETIME_COLS,
        cols_types=DAILY_BILLINGS_NUM_COLS,
    )


@benchmark_with(db_connector_logger)
@logging_with(db_connector_logger)
def get_vw_customer_details() -> pd.DataFrame:
    return get_dataframe_from_sql_query(
        CUSTOMER_DETAILS_SCRIPT,
        date_cols=CUSTOMER_DETAILS_DATETIME_COLS,
        cols_types=CUSTOMER_DETAILS_NUM_COLS,
    )

@benchmark_with(db_connector_logger)
@logging_with(db_connector_logger)
def get_vw_future_bills() -> pd.DataFrame:
    return get_dataframe_from_sql_query(
        FUTURE_BILLS_SCRIPT,
        date_cols=FUTURE_BILLS_DATETIME_COLS,
        cols_types=FUTURE_BILLS_NUM_COLS,
    )
