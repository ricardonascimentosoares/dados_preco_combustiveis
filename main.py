import pylightxl as xl
import pandas as pd
import requests
import unidecode
import json
from bs4 import BeautifulSoup
from slugify import slugify
from google_coordinates_creator import GoogleCoordinatesCreator


def get_coordinates_from_google(d):
    g = GoogleCoordinatesCreator()
    d['COORDINATES'] = d.apply(lambda r:
                               g.get_coordinates(address=r.ENDERECO,
                                                 city=r.MUNICIPIO,
                                                 state=r.ESTADO),
                               axis=1)
    d['LAT'] = d.apply(lambda r: r.COORDINATES['lat'] if r.COORDINATES is not None else None, axis=1)
    d['LNG'] = d.apply(lambda r: r.COORDINATES['lng'] if r.COORDINATES is not None else None, axis=1)



url_preco_combustiveis = 'https://www.gov.br/anp/pt-br/assuntos/precos-e-defesa-da-concorrencia/precos/levantamento-de-precos-de-combustiveis-ultimas-semanas-pesquisadas'
url_dados_cadastrais_postos = 'https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/arquivos-dados-cadastrais-dos-revendedores-varejistas-de-combustiveis-automotivos/dados-cadastrais-revendedores-varejistas-combustiveis-automoveis.csv'

reqs = requests.get(url_preco_combustiveis)
soup = BeautifulSoup(reqs.text, 'html.parser')

# busca os links de download dos precos
url_dados_preco_combustivel = ''
for link in soup.find_all('a'):
    if 'xlsx' in link.get('href') and 'semanal' not in link.get('href'):
        url_dados_preco_combustivel = link.get('href')
        break

# baixa o arquivo com os precos
file_data = requests.get(url_dados_preco_combustivel).content
# create the file in write binary mode, because the data we get from net is in binary
with open("dados_preco_combustivel.xlsx", "wb") as file:
    file.write(file_data)

# le arquivo xlsx
db = xl.readxl(fn='dados_preco_combustivel.xlsx')

# cria dataframe preco combustivel
df = pd.DataFrame(db.ws(ws='POSTOS REVENDEDORES').rows, index=None)
df_preco_combustivel = df.iloc[10:, :]  # desconsidera 10 as primeiras linhas do arquivo
df_preco_combustivel.columns = df.iloc[9]  # seta o cabecalho
df_preco_combustivel = df_preco_combustivel.reset_index(drop=True)
df_preco_combustivel = df_preco_combustivel.pivot_table(values='PREÇO DE REVENDA',
                                                        index=['CNPJ', 'RAZÃO', 'FANTASIA', 'ENDEREÇO', 'NÚMERO',
                                                               'COMPLEMENTO',
                                                               'BAIRRO', 'CEP', 'MUNICÍPIO', 'ESTADO', 'BANDEIRA',
                                                               'DATA DA COLETA'], columns='PRODUTO').reset_index()
df_preco_combustivel = df_preco_combustivel.rename(
    columns={"MUNICÍPIO": "MUNICIPIO",
             "ENDEREÇO": "ENDERECO",
             "NÚMERO": "NUMERO",
             "RAZÃO": "RAZAO",
             "DIESEL S10": "DIESEL_S10",
             "DIESEL S500": "DIESEL_S500",
             "GASOLINA ADITIVADA": "GASOLINA_ADITIVADA",
             "GASOLINA COMUM": "GASOLINA_COMUM",
             "DATA DA COLETA": "DATA_DA_COLETA"})
df_preco_combustivel['DIESEL_S10'] = df_preco_combustivel['DIESEL_S10'].fillna(0)
df_preco_combustivel['DIESEL_S500'] = df_preco_combustivel['DIESEL_S500'].fillna(0)
df_preco_combustivel['ETANOL'] = df_preco_combustivel['ETANOL'].fillna(0)
df_preco_combustivel['GASOLINA_ADITIVADA'] = df_preco_combustivel['GASOLINA_ADITIVADA'].fillna(0)
df_preco_combustivel['GASOLINA_COMUM'] = df_preco_combustivel['GASOLINA_COMUM'].fillna(0)
df_preco_combustivel['GLP'] = df_preco_combustivel['GLP'].fillna(0)
df_preco_combustivel['GNV'] = df_preco_combustivel['GNV'].fillna(0)
df_preco_combustivel['NUMERO'] = df_preco_combustivel['NUMERO'].astype(str)
df_preco_combustivel['COMPLEMENTO'] = df_preco_combustivel['COMPLEMENTO'].astype(str)
df_preco_combustivel['FANTASIA'] = df_preco_combustivel['FANTASIA'].astype(str)


del df

# gera o arquivo resultante
results_dict = df_preco_combustivel.to_dict(orient='records')
with open("results.json", "w") as outfile:
    json.dump(results_dict, outfile)

# get_coordinates_from_google(df_preco_combustivel)

# drive = GoogleDriverHelper()
# drive.save_file('dados_preco_combustiveis_final.csv')
