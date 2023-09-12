# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import numpy as np

APP_VERSION = "0.3.4"
TIMEOUT = 3600
PAGE_SIZE = 100
OPERATORS = [
    ['ge ', '>='],
    ['le ', '<='],
    ['lt ', '<'],
    ['gt ', '>'],
    ['ne ', '!='],
    ['eq ', '='],
    ['contains '],
    ['datestartswith '],
]

MONTHS_PTBR = {
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
MONTHS_PTBR_ABBR = {
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

TAGS = ['_liquido', '_bruto', '_desconto', '_bonificado', '_enxoval']
STARTING_YEAR = 2022
CURRENT_MONTH = datetime.now().month
CURRENT_YEAR = datetime.now().year
MASTER_COLUMNS_HEAD = [
    'cod_cliente',
    'nome_cliente',
    'razao_social',
    'ramo_atividade',
    'dt_cadastro',
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
    'cod_marca',
    'desc_marca',
    'STATUS',
]
SALE_NOPS = [
    '6.102',
    '6.404',
    'BLACKFRIDAY',
    'VENDA',
    'VENDA_S_ESTOQUE',
    'WORKSHOP',
]
SUBSIDIZED_NOPS = [
    'BONIFICADO',
    'BONIFICADO_F',
    'BONI_COMPRA',
    'PROMOCAO',
    'PROMO_BLACK',
    'CAMPANHA',
]
TROUSSEAU_NOPS = ['ENXOVAL']
COMPANIES = {
    1: 'KAMI CO',
    2: 'NEW HAUSS',
    3: 'MOVEMENT SP',
    4: 'ENERGY',
    5: 'HAIRPRO',
    6: 'SOUTH',
    9: 'MMS',
    10: '3MKO MATRIZ',
    11: '3MKO FILIAL SP',
    12: '3MKO FILIAL ES',
    13: 'MOVEMENT RJ',
    14: '3MKO FILIAL PR',
    15: 'MOVEMENT MT',
    16: 'MOVEMENT RS',
}
TEMPLATE_COLS = [
    'ano',
    'mes',
    'cod_cliente',
    'nome_cliente',
    'ramo_atividade',
    'bairro',
    'cidade',
    'uf',
    'cod_colaborador',
    'nome_colaborador',
    'cod_situacao',
    'desc_situacao',
    'cod_grupo_produto',
    'desc_grupo_produto',
    'cod_grupo_pai',
    'desc_grupo_pai',
    'cod_marca',
    'desc_marca',
    'empresa_nota_fiscal',
]

CUSTOMER_DETAILS_NUM_COLS = {
    'cod_cliente': np.int64,
    'dias_atraso': np.int64,
    'valor_devido': np.float64,
    'ultimo_ano_ativo': np.int64,
}
CUSTOMER_DETAILS_DATETIME_COLS = [
    'data_cadastro',
    'dt_primeira_compra',
    'dt_ultima_compra',
]
DAILY_BILLINGS_NUM_COLS = {
    'ano': np.int64,
    'mes': np.int64,
    'empresa_pedido': np.int64,
    'empresa_nota_fiscal': np.int64,
    'cod_cliente': np.int64,
    'cod_colaborador': np.int64,
    'cod_pedido': np.int64,
    'cod_situacao': np.int64,
    'cod_grupo_produto': np.int64,
    'cod_grupo_pai': np.int64,
    'cod_marca': np.int64,
    'custo_total': np.float64,
    'custo_kami': np.float64,
    'qtd': np.int64,
    'preco_unit_original': np.float64,
    'preco_total_original': np.float64,
    'margem_bruta': np.float64,
    'preco_total': np.float64,
    'preco_desconto_rateado': np.float64,
    'vl_total_pedido': np.float64,
    'desconto_pedido': np.float64,
    'valor_nota': np.float64,
    'total_bruto': np.float64,
}
MONTHLY_BILLINGS_NUM_COLS = {
    'ano': np.int64,
    'mes': np.int64,
    'cod_empresa': np.int64,
    'cod_pedido': np.int64,
    'cod_cliente': np.int64,
    'situacao_pedido': np.int64,
    'cod_colaborador': np.int64,
    'qtd': np.int64,
    'custo_total': np.float64,
    'custo_kami': np.float64,
    'preco_unit_original': np.float64,
    'preco_total_original': np.float64,
    'margem_bruta': np.float64,
    'preco_total': np.float64,
    'preco_desconto_rateado': np.float64,
    'vl_total_pedido': np.float64,
    'desconto_pedido': np.float64,
    'valor_nota': np.float64,
    'situacao_entrega': np.int64,
    'empresa_pedido': np.int64,
    'empresa_nf': np.int64,
}
MONTHLY_BILLINGS_SCRIPT = 'SELECT * FROM vw_monthly_billings'
DAILY_BILLINGS_SCRIPT = f'SELECT * FROM vw_daily_billings AS vdb \
    WHERE vdb.ano >= {STARTING_YEAR}'
CUSTOMER_DETAILS_SCRIPT = f'SELECT * FROM vw_customer_details AS vcd WHERE vcd.ultimo_ano_ativo >= {STARTING_YEAR}'
BILLINGS_DATETIME_COLS = [
    'dt_implante_pedido',
    'dt_entrega_comprometida',
    'dt_faturamento',
]
FUTURE_BILLS_SCRIPT = 'SELECT * FROM vw_future_bills'
FUTURE_BILLS_DATETIME_COLS = ['dt_vencimento']
FUTURE_BILLS_NUM_COLS = {'cod_empresa': np.int64, 'total_a_receber': np.float64}
ODERS_COLS_HEAD = [
    'ano',
    'mes',
    'empresa_pedido',
    'empresa_nota_fiscal',
    'cod_cliente',
    'cod_colaborador',
    'nome_colaborador',
    'cod_pedido',
    'nr_ped_compra_cli',
    'cod_situacao',
    'desc_situacao',
    'nop',
    'cfop',
    'cod_cond_pagto',
    'cod_forma_pagto',
    'forma_pgto',
    'tb_preco',
    'vl_total_pedido',
    'desconto_pedido',
    'valor_nota',
    'total_bruto',
    'dt_implante_pedido',
    'dt_entrega_comprometida',
    'dt_faturamento',
]
SALES_ORDERS_GROUP_COLUMNS = [
    'ano',
    'mes',
    'empresa_pedido',
    'empresa_nota_fiscal',
    'cod_cliente',
    'cod_pedido',
    'nr_ped_compra_cli',
    'cod_situacao',
    'desc_situacao',
    'nop',
    'cfop',
    'cod_cond_pagto',
    'cod_forma_pagto',
    'forma_pagto',
    'cod_grupo_produto',
    'desc_grupo_produto',
    'cod_grupo_pai',
    'desc_grupo_pai',
    'cod_marca',
    'desc_marca',    
]
SALES_ORDERS_SUM_COLUMNS = ['desconto_pedido', 'valor_nota', 'total_bruto']