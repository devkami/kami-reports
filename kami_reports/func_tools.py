import requests
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import date
import pandas as pd
import time
import base64
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def clear_sheet(spreadsheet_id, sheet_name,first_col,last_col):
    creds = None
    if os.path.exists(os.getenv('TOKEN')):
        creds = Credentials.from_authorized_user_file(os.getenv('TOKEN'), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.getenv('CLIENT_SECRET'), SCOPES)
            creds = flow.run_local_server(port=0)

        with open(os.getenv('TOKEN'), 'w') as token:
            token.write(creds.to_json())
    try:
        service = build('sheets', 'v4', credentials=creds)

        range_name = f'{sheet_name}!{first_col}2:{last_col}'

        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        values = result.get('values', [])

        if len(values) > 0:
            start_row = 2
            end_row = start_row + len(values) - 1
            clear_range = f'{sheet_name}!A{start_row}:{last_col}{end_row}'

            service.spreadsheets().values().clear(
                spreadsheetId=spreadsheet_id,
                range=clear_range
            ).execute()
        
        print(f"Dados na guia '{sheet_name}' foram apagados com sucesso.")

    except HttpError as err:
        print(err)

def serialize_data(value):
    if isinstance(value, pd.Timestamp):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return str(value)

def append_sheet(df, sheet, first_col, last_col, sheetlink):
    creds = None

    if os.path.exists(os.getenv('TOKEN')):
        creds = Credentials.from_authorized_user_file(os.getenv('TOKEN'), SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.getenv('CLIENT_SECRET'), SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(os.getenv('TOKEN'), 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)

        spreadsheet_id = f'{sheetlink}'
        range_name = f'{sheet}!{first_col}2:{last_col}'
        value_input_option = 'USER_ENTERED'

        # Serializar os dados do DataFrame, incluindo Timestamps
        df_serialized = df.applymap(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, pd.Timestamp) else str(x))

        # Converter DataFrame serializado em uma lista de listas
        rows_to_insert = df_serialized.values.tolist()

        body = {
            'values': rows_to_insert
        }

        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption=value_input_option,
            body=body
        ).execute()

        return df

    except HttpError as err:
        print(err)


def gsheet_reader(sheetlink,sheetname,first_col,last_col):
    creds = None

    if os.path.exists(os.getenv('TOKEN')):
        creds = Credentials.from_authorized_user_file(os.getenv('TOKEN'), SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.getenv('CLIENT_SECRET'), SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(os.getenv('TOKEN'), 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()

        result_1 = sheet.values().get(spreadsheetId=f'{sheetlink}',
                                    range=f'{sheetname}!{first_col}2:{last_col}').execute()
        
        values_1 = result_1.get('values', [])
        
        df= pd.DataFrame(values_1)
        
        return df

    except HttpError as err:
        print(err)