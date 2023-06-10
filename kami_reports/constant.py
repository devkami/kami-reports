# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

months_ptbr = {
    1: 'Janeiro',
    2: 'Fevereiro',
    3: 'Março',
    4: 'Abril',
    5: 'Maio',
    6: 'Junho',
    7: 'Julho',
    8: 'Agosto',
    9: 'Setembro',
    10: 'Outubro',
    11: 'Novembro',
    12: 'Dezembro',
}

months_ptbr_abbr = {
    1: 'JAN',
    2: 'FEV',
    3: 'MAR',
    4: 'ABR',
    5: 'MAI',
    6: 'JUN',
    7: 'JUL',
    8: 'AGO',
    9: 'SET',
    10: 'OUT',
    11: 'NOV',
    12: 'DEZ',
}

weekdays_ptbr = {
    0: 'Segunda',
    1: 'Terça',
    2: 'Quarta',
    3: 'Quinta',
    4: 'Sexta',
    5: 'Sábado',
    6: 'Domingo',
}

weekdays_ptbr_abbr = {
    0: 'SEG',
    1: 'TER',
    2: 'QUA',
    3: 'QUI',
    4: 'SEX',
    5: 'SAB',
    6: 'DOM',
}

industry_areas = ['SITE', 'SALAO', 'PERFUMARIA']

tags = ['_liquido', '_bruto', '_desconto', '_bonificado', '_enxoval']
starting_year = 2022
scope = 'https://www.googleapis.com/auth/drive'
key_file_location = 'service_account_credentials.json'
current_month = datetime.now().month
current_year = datetime.now().year
current_day = datetime.now().day
end_week = datetime.now() - timedelta(days=datetime.today().weekday())
start_week = end_week - timedelta(days=7)
current_weekday = datetime.today().weekday()
week_year_number = datetime.now().strftime('%V')
current_week_folder = f'Semana-{week_year_number} ({start_week.day}-{start_week.month} a {end_week.day}-{end_week.month})'
current_day_folder = f'{current_day}-{weekdays_ptbr_abbr[current_weekday]}'
comercial_week = [0, 1, 2, 3, 4]
columns_names_head = [
    'cod_colaborador',
    'nome_colaborador',
    'cod_cliente',
    'nome_cliente',
    'razao_social',
    'ramo_atividade',
    'data_cadastro',
    'bairro',
    'cidade',
    'uf',
    'endereco',
    'numero',
    'cep',
    'dias_atraso',
    'valor_devido',
    'dt_primeira_compra',
    'dt_ultima_compra',
    'dias_sem_compra',
    'cod_marca',
    'desc_marca',
]
sale_nops = [
    '6.102',
    '6.404',
    'BLACKFRIDAY',
    'VENDA',
    'VENDA_S_ESTOQUE',
    'WORKSHOP',
]
subsidized_nops = [
    'BONIFICADO',
    'BONIFICADO_F',
    'BONI_COMPRA',
    'PROMOCAO',
    'PROMO_BLACK',
    'CAMPANHA',
]
trousseau_nops = ['ENXOVAL']
