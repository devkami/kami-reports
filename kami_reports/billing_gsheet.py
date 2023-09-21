from func_tools import append_sheet, clear_sheet
import pandas as pd
from dataframe import get_vw_board_billings, get_vw_customer_details
import datetime as dt
from datetime import datetime


clear_sheet('19NnUqV0hw4BK8moFKNGiQOyGYTA7Z_JKEj2uLsl12_k','Faturamento Executivo','A','L')

df = get_vw_board_billings()

df = df.dropna(subset=['dt_faturamento'])

colunas_desejadas = [
    'cod_cliente',
    'desc_abrev_cfop',
    'desc_abreviada',
    'preco_desconto_rateado',
    'dt_faturamento',
    'marca',
    'uf_empresa_faturamento',
]

df_filtrado = df[colunas_desejadas]

def definir_status(df):
    
    data_de_hoje = datetime.now()
    lista_status = []
    lista_cliente = []
    
    for cliente in df['cod_cliente']:
        c = df_filtrado[df_filtrado['cod_cliente'] == cliente]
        c = c.sort_values(by='dt_faturamento', ascending=False)
        
        diferenca_tempo = (data_de_hoje - c['dt_faturamento'].iloc[0]).days
        
        if diferenca_tempo <= 30 and len(c) == 1:
            lista_status.append("novo")
            lista_cliente.append(cliente)
            
        elif diferenca_tempo <= 60 and len(c) == 1:
            lista_status.append("ativo")
            lista_cliente.append(cliente)
            
        elif diferenca_tempo <= 90 and len(c) == 1:
            lista_status.append("pre-inativo")
            lista_cliente.append(cliente)
        
        elif diferenca_tempo <= 365 and len(c) == 1:
            lista_status.append("inativo")
            lista_cliente.append(cliente)
            
        elif diferenca_tempo > 365 and len(c) == 1:
            lista_status.append("perdido")
            lista_cliente.append(cliente)
        
        else:
            tamanho = len(c)
            c = c.drop_duplicates(subset=['dt_faturamento'])
            if len(c) > 1 :
                tamanho = len(c)

                status = (c['dt_faturamento'].iloc[0] - c['dt_faturamento'].iloc[1]).days

                if diferenca_tempo <= 30 and status >= 180:
                    for index in range(0,tamanho):
                        lista_status.append("recuperado")
                        lista_cliente.append(cliente)

                elif diferenca_tempo <= 30 and status > 90 and status < 180:
                    for index in range(0,tamanho):
                        lista_status.append("reativado")
                        lista_cliente.append(cliente)

                elif diferenca_tempo <= 30 and status <= 60:
                    for index in range(0,tamanho):
                        lista_status.append("ativo")
                        lista_cliente.append(cliente)

            if diferenca_tempo < 60 and cliente not in lista_cliente:
                for index in range(0,tamanho):
                    lista_status.append("ativo")
                    lista_cliente.append(cliente)

            elif diferenca_tempo >= 60 and diferenca_tempo < 90 and cliente not in lista_cliente:
                for index in range(0,tamanho):
                    lista_status.append("pre-inativo")
                    lista_cliente.append(cliente)

            elif diferenca_tempo >= 90 and diferenca_tempo < 180 and cliente not in lista_cliente:
                for index in range(0,tamanho):
                    lista_status.append("inativo")
                    lista_cliente.append(cliente)

            elif diferenca_tempo >= 180 and cliente not in lista_cliente:
                for index in range(0,tamanho):
                    lista_status.append("perdido")
                    lista_cliente.append(cliente)
                        
    dados_combinados = list(zip(lista_status, lista_cliente))
    df_status = pd.DataFrame(dados_combinados, columns=['status', 'cod_cliente'])
    df_status = df_status.drop_duplicates(subset=['cod_cliente'])
    df_status_fat = pd.merge(df,df_status, how="left")
    
    return df_status_fat

df = definir_status(df_filtrado)

append_sheet(df,'Faturamento Executivo','A','L','19NnUqV0hw4BK8moFKNGiQOyGYTA7Z_JKEj2uLsl12_k')


