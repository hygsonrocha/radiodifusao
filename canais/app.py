import xml.etree.ElementTree as ET
import numpy as np # type: ignore
import pandas as pd # type: ignore
import shapely.geometry # type: ignore
import geopandas as gpd # type: ignore
import folium # type: ignore
from folium import Circle # type: ignore
import matplotlib.pyplot as plt
from scipy import interpolate # type: ignore
import streamlit as st

def ocupacao_canal(status):
    status = status.upper().strip()  # Converte para maiúsculas e remove espaços em branco extras
    if 'C0' in status:
        return 'Canal Vago'
    return 'Canal Ocupado'


def mapear_servico(servico):
    servico = servico.strip()
    mapeamento_servicos = {
        'FM': 'FM',
        'RTRFM': 'RTR',
        'RTVD': 'RTVD',
        'GTVD': 'TVD',
        'PBTVD': 'TVD',
        'TVA': 'TVA',
        'TV': 'TV',
        'RTV': 'RTV',
        'OM': 'OM'
    }
    return mapeamento_servicos.get(servico, 'verificar')


def subfaixa_tv(canal):    
    if not isinstance(canal, int):
        raise ValueError("O canal deve ser um número inteiro.")
    subfaixas = {
        range(2, 7): "VHF Baixo",
        range(7, 14): "VHF Alto",
        range(14, 52): "UHF"
    }
    for faixa, nome in subfaixas.items():
        if canal in faixa:
            return nome
    return "NA"


def operacao(ocupacao):
    mapeamento = {
        'Canal Ocupado': 'Sim',
        'Canal Vago': 'Não'
    }
    return mapeamento.get(ocupacao, 'Desconhecido')


def descricao_status(status):
    status_map = {
        'C0': 'Canal Vago',
        'C1': 'Canal Outorgado - Aguardando Ato de RF',
        'C2': 'Canal Outorgado - Aguardando Dados da Estação',
        'C3': 'Canal Outorgado - Aguardando Licenciamento',
        'C4': 'Canal Licenciado',
        'C5': 'Canal Pendente de Outorga',
        'C7': 'Aguardando Ato de RF',
        'C8': 'Aguardando Dados do Contrato',
        'C98': 'Canal TVA',
        'C99': 'Canal Suspenso'
    }
    return status_map.get(status, 'Não definido')


def dmax_cp(classe, servico, canal):
    dmax = 0
    classe = classe.upper()
    dmax_fm = {
        'E1': 78.5, 'E2': 67.5, 'E3': 54.5,
        'A1': 38.5, 'A2': 35.0, 'A3': 30.0, 'A4': 24.0,
        'B1': 16.5, 'B2': 12.5, 'C': 7.5
    }
    dmax_tvd = {
        'E': {13: 65.6, 46: 58.0, 'default': 58.0},
        'ESPECIAL': {13: 65.6, 46: 58.0, 'default': 58.0},
        'A': {13: 47.9, 'default': 42.5},
        'B': {13: 32.3, 'default': 29.1},
        'C': {13: 20.2, 'default': 18.1}
    }
    dmax_tv = {
        'E': {6: 64.7, 13: 54.2, 'default': 50.9},
        'ESPECIAL': {6: 64.7, 13: 54.2, 'default': 50.9},
        'A': {6: 42.1, 13: 36.3, 'default': 35.2},
        'B': {6: 25.8, 13: 22.8, 'default': 22.6},
        'C': {6: 15.0, 13: 13.1, 'default': 13.2}
    }
    if servico in ['FM', 'RTRFM', 'RTR']:
        dmax = dmax_fm.get(classe, 0)
    elif servico in ['RTVD', 'GTVD', 'PBTVD', 'TVD']:
        if classe in dmax_tvd:
            if canal <= 13:
                dmax = dmax_tvd[classe][13]
            elif canal <= 46:
                dmax = dmax_tvd[classe].get(46, dmax_tvd[classe]['default'])
            else:
                dmax = dmax_tvd[classe]['default']
    elif servico in ['TV', 'RTV']:
        if classe in dmax_tv:
            if canal <= 6:
                dmax = dmax_tv[classe][6]
            elif canal <= 13:
                dmax = dmax_tv[classe][13]
            else:
                dmax = dmax_tv[classe]['default']
    return dmax

def gerar_circulo(latitude, longitude, raio, return_gdf=False):
    # latitude e longitude em graus, raio em km
    centro_circulo = shapely.geometry.Point(longitude, latitude)
    gdf_centro_circulo = gpd.GeoDataFrame(geometry=[centro_circulo], crs='EPSG:4674')
    centro_circulo_utm = gdf_centro_circulo.to_crs(epsg=5880)
    circulo_utm = centro_circulo_utm.buffer(raio * 10**3)  # raio em metros
    circulo = circulo_utm.to_crs('EPSG:4674')
    if return_gdf:
        return gpd.GeoDataFrame(geometry=circulo)
    else:
        return circulo.iloc[0]


def circulo_gdf(latitude, longitude, raio):
    """
    Gera um GeoDataFrame de um círculo com centro em (latitude, longitude) e raio em metros.
    Latitude e longitude em graus, raio em km.
    """
    return gerar_circulo(latitude, longitude, raio, return_gdf=True)


def circulo(latitude, longitude, raio):
    """
    Gera um objeto Polygon de um círculo com centro em (latitude, longitude) e raio em metros.
    Latitude e longitude em graus, raio em km.
    """
    return gerar_circulo(latitude, longitude, raio, return_gdf=False)


def converter_padrao_antena(padrao_antena_str):
    if padrao_antena_str:
        return np.array([float(g) for g in padrao_antena_str.split('|')])
    else:
        return np.array([])

# Streamlit app title
st.title("Busca de Canais de Radiodifusão")

arquivo_xml = r"plano_basicoTVFM.xml"
raiz = ET.parse(arquivo_xml) # type: ignore
linhas = []
for linha in raiz.findall('row'):
    dado_linha = linha.attrib 
    linhas.append(dado_linha)
df = pd.DataFrame(linhas) # type: ignore

df['Canal'] = df['Canal'].astype(int)
df['Frequencia'] = pd.to_numeric(df['Frequencia'], errors='coerce')
df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
df['ERP'] = pd.to_numeric(df['ERP'], errors='coerce')
df['Altura'] = pd.to_numeric(df['Altura'], errors='coerce')

df['TipoServico'] = df['Servico'].apply(mapear_servico)
df['SubfaixaTV'] = df['Canal'].apply(subfaixa_tv)
df['Ocupacao'] = df['Status'].apply(ocupacao_canal)
df['DescricaoStatus'] = df['Status'].apply(descricao_status)
df['distMaxCP'] = np.vectorize(dmax_cp)(df['Classe'], df['Servico'], df['Canal'])
df['PadraoAntena'] = df.apply(
    lambda row: converter_padrao_antena(row['PadraoAntena_dBd']) if row['dic'] == '1' else np.nan, 
    axis=1
)

st.write(df)





    