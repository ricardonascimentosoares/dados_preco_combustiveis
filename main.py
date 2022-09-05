import pylightxl as xl
import pandas as pd
import requests
from bs4 import BeautifulSoup
from google_coordinates_creator import GoogleCoordinatesCreator
from google_drive_helper import GoogleDriverHelper

url_preco_combustiveis = 'https://www.gov.br/anp/pt-br/assuntos/precos-e-defesa-da-concorrencia/precos/levantamento-de-precos-de-combustiveis-ultimas-semanas-pesquisadas'
url_dados_cadastrais_postos = 'https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/arquivos-dados-cadastrais-dos-revendedores-varejistas-de-combustiveis-automotivos/dados-cadastrais-revendedores-varejistas-combustiveis-automoveis.csv'


reqs = requests.get(url_preco_combustiveis)
soup = BeautifulSoup(reqs.text, 'html.parser')

#busca os links de download dos precos
url_dados_preco_combustivel = ''
contador = 0
for link in soup.find_all('a'):
    if 'xlsx' in link.get('href'):
        if contador < 1:
            contador = contador + 1
        else:
            url_dados_preco_combustivel = link.get('href')
            break

# baixa o arquivo com os precos
file_data = requests.get(url_dados_preco_combustivel).content
# create the file in write binary mode, because the data we get from net is in binary
with open("url_dados_preco_combustivel.xlsx", "wb") as file:
    file.write(file_data)

# le arquivo xlsx
db = xl.readxl(fn='url_dados_preco_combustivel.xlsx')

# cria dataframe preco combustivel
df = pd.DataFrame(db.ws(ws='POSTOS REVENDEDORES').rows, index=None)
df_preco_combustivel = df.iloc[12:, :]  # desconsidera 12 as primeiras linhas do arquivo
df_preco_combustivel.columns = df.iloc[11]  # seta o cabecalho

del df

df_preco_combustivel = df_preco_combustivel.reset_index(drop=True)
df_preco_combustivel['CNPJ'] = df_preco_combustivel['CNPJ'].str.replace(r'\D+', '', regex=True)
# carrega o dataframe com os dados cadastrais
df_dados_cadastrais = pd.read_csv(url_dados_cadastrais_postos, sep=';')
df_dados_cadastrais['CNPJ'] = df_dados_cadastrais['CNPJ'].apply(str)

df_final = pd.merge(df_preco_combustivel, df_dados_cadastrais[['CNPJ',
                                                               'ENDERECO',
                                                               'BANDEIRA']],
                    on='CNPJ')

#df_final = df_final.head(5) teste

g = GoogleCoordinatesCreator()
df_final['COORDINATES'] = df_final.apply(lambda r:
                                         g.get_coordinates(address=r.ENDERECO,
                                                           city=r.MUNICIPIO,
                                                           state=r.ESTADO),
                                         axis=1)
df_final['LAT'] = df_final.apply(lambda r:  r.COORDINATES['lat'] if r.COORDINATES is not None else None, axis=1)
df_final['LNG'] = df_final.apply(lambda r: r.COORDINATES['lng'] if r.COORDINATES is not None else None, axis=1)
df_final.to_csv('dados_preco_combustiveis_final.csv')

drive = GoogleDriverHelper()
drive.save_file('dados_preco_combustiveis_final.csv')