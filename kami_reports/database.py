#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from os import getenv
import pandas as pd
from dotenv import load_dotenv
from kami_logging import benchmark_with, logging_with
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from constant import starting_year

db_connector_logger = logging.getLogger('database')
load_dotenv()
connection_url = URL.create(
    'mysql+pymysql',
    username=getenv('DB_USER'),
    password=getenv('DB_USER_PASSWORD'),
    host=getenv('DB_HOST'),
    database='db_uc_kami',
)


def get_dataframe_from_sql(sql_script: str) -> pd.DataFrame:
    sql_engine = create_engine(connection_url, pool_recycle=3600)
    sql_engine.connect()
    df = pd.read_sql_query(sql_script, sql_engine)
    return pd.DataFrame(df)


@benchmark_with(db_connector_logger)
@logging_with(db_connector_logger)
def get_vw_monthly_billings() -> pd.DataFrame:
    return get_dataframe_from_sql('SELECT * FROM vw_monthly_billings')


@benchmark_with(db_connector_logger)
@logging_with(db_connector_logger)
def get_vw_daily_billings() -> pd.DataFrame:
    return get_dataframe_from_sql(
        f'SELECT * FROM vw_daily_billings AS vdb WHERE vdb.ano >= {starting_year}'
    )


@benchmark_with(db_connector_logger)
@logging_with(db_connector_logger)
def get_vw_customer_details() -> pd.DataFrame:
    return get_dataframe_from_sql(
        f'SELECT * FROM vw_customer_details AS vcd WHERE vcd.ultimo_ano_ativo >= {starting_year}'
    )
