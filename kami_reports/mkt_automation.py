from database import get_dataframe_from_sql
from datetime import datetime as dt, timedelta as td
from constant import ORDER_ITEM_DATE_COLS
first_update = dt.now() - td(days=7)
current_update = first_update
last_update = first_update



def get_beexp_since(ordered_date):
    sql_file = 'data/in/beexp_orders.sql'
    oders_df = get_dataframe_from_sql(
    sql_query=sql_file,
    date_cols=ORDER_ITEM_DATE_COLS
    )
    mask = (oders_df['dt_implant'] >= ordered_date)
    return oders_df.loc[mask]

def get_beexp_manager_message(row):
    index, qtd, nome_colaborador, desc_comercial, preco_total, cond_pgto, cod_cliente, nome_cliente, dt_implant, email_colaborador = row
    
    return f"""Quantidade de Ingressos: {qtd} Nome do Vendedor: {nome_colaborador} Tipo de Ingresso: {desc_comercial} Valor faturado: {preco_total} Forma de pagamento: {cond_pgto} Código do cliente: {cod_cliente} Nome do Cliente: {nome_cliente} Data da venda: {dt_implant} E-mail do representante: {email_colaborador}. O respectivo vendedor já recebeu o link de cadastro do participante."""