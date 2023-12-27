import streamlit as st

def grupo_enquadramento(classe):

    # Esta função retorna o grupo de enquadramento de um canal de radiodifusão, baseado em sua classe.
    # É válida apenas para as classes dos serviços de FM e TV. Não funciona para OM.
    
    if classe in ['B1', 'B2', 'C']:
        return 'A'
    elif classe in ['A', 'A1', 'A2', 'A3', 'A4', 'B']:
        return 'B'
    elif classe in ['E1', 'E2', 'E3', 'E']:
        return 'C'
    else:
        return 'classe inexistente'


def dmax_cp(classe, canal = None):
    
    # Identifica a distância máxima (dmax) ao contorno protegido (cp), 
    # com base no número e na classe do canal. Função válida apenas para 
    # canais de FM e de TV digital.

    canal = int(canal)
    
    if classe.lower() in ['e','especial']:
        if canal <= 13:
            dmax = 65.6
        elif canal <= 46:
            dmax = 58.0
        elif canal >= 47:
            dmax = 58.0
    elif classe == 'A':
        if canal <= 13:
            dmax=  47.9
        elif canal >= 14:
            dmax = 42.5
    elif classe == 'B':
        if canal <= 13:
            dmax = 32.3
        elif canal >= 14:
            dmax = 29.1        
    elif classe == 'C':
        if canal == None:
            dmax= 7.5
        else:
            if canal <= 13:
                dmax = 20.2
            elif canal >= 14 and canal <= 51:
                dmax = 18.1
            else:
                dmax = 7.5
    elif classe == 'E1':
        dmax = 78.5
    elif classe == 'E2':
        dmax = 67.5
    elif classe == 'E3':
        dmax = 54.5
    elif classe == 'A1':
        dmax = 38.5
    elif classe == 'A2':
        dmax = 35.0
    elif classe == 'A3':
        dmax = 30.0
    elif classe == 'A4':
        dmax = 24.0
    elif classe == 'B1':
        dmax = 16.5
    elif classe == 'B2':
        dmax = 12.5
    
    return dmax
   

# -----------------------------------------------------------------------------------------------------------------------------------------


def circulo_gdf(longitude, latitude, raio): 
    
    # Gera o shapefile de um círculo com centro em (latitude, longitude) e raio em metros.
    # Latitude e longitude em graus, raio em km
    
    import geopandas as gpd
    import shapely.geometry
    
    centro_circulo = shapely.geometry.Point(longitude, latitude)
    gdf_centro_circulo = gpd.GeoDataFrame(geometry=[centro_circulo], crs='EPSG:4674')
    centro_circulo_utm = gdf_centro_circulo.to_crs(epsg=5880)
    circulo_utm = centro_circulo_utm.buffer(raio * 10**3) # raio em metros
    circulo = circulo_utm.to_crs('EPSG:4674')  
    
    return gpd.GeoDataFrame(geometry=circulo)


# -----------------------------------------------------------------------------------------------------------------------------------------


def circulo(latitude, longitude, raio): 
    
    # Gera o círculo com centro em (latitude, longitude) e raio em metros.
    # Latitude e longitude em graus, raio em km
    
    import geopandas as gpd
    import shapely.geometry
    
    centro_circulo = shapely.geometry.Point(longitude, latitude)
    gdf_centro_circulo = gpd.GeoDataFrame(geometry=[centro_circulo], crs='EPSG:4674')
    centro_circulo_utm = gdf_centro_circulo.to_crs(epsg=5880)
    circulo_utm = centro_circulo_utm.buffer(raio * 10**3) # raio em metros
    circulo = circulo_utm.to_crs('EPSG:4674')  
    
    return circulo[0]


# -----------------------------------------------------------------------------------------------------------------------------------------


def setores_cobertos(arquivo_xml):
    
    # Esta função lê o arquivo xml gerado pela análise de cobertura do Mosaico, modifica o tipo de dados
    # de algumas colunas (int), cria outras colunas (moradores cobertos e área coberta) e exporta a planilha 
    # resultante na forma de um dataframe do Pandas (setores_cobertos_df).
    
    # O arquivo gerado pela análise de cobertura do Mosaico informa os setores censitários atingidos pela mancha de cobertura,
    # com seus respectivos códigos (CD_GEOCODI), códigos dos municípios a que percentecem (CD_GEOCODM), número de domicílios
    # (DOMICILIOS) do setor, número de moradores (MORADORES) do setor, área do setor censitário (AREA_M2) e percentagem de 
    # cobertura de cada setor pela mancha (pct).
    
    # Exemplo:
    # arquivo_xml = r"C:\Users\hygso\Google Drive\Python\Radiodifusão\Cobertura\RL_hygson@anatel.gov.br\poly_result.xml"
    
    import numpy as np
    import pandas as pd
    
    setores_cobertos_df = pd.read_xml(arquivo_xml)
    setores_cobertos_df['CD_GEOCODI'] = setores_cobertos_df['CD_GEOCODI'].astype('str')
    setores_cobertos_df['CD_GEOCODM'] = setores_cobertos_df['CD_GEOCODM'].astype('str')
    setores_cobertos_df['DOMICILIOS'] = setores_cobertos_df['DOMICILIOS'].astype(float).astype(int)
    setores_cobertos_df['MORADORES'] = setores_cobertos_df['MORADORES'].astype(float).astype(int)
    setores_cobertos_df["MORADORES_COBERTOS"] = (setores_cobertos_df["pct"] * setores_cobertos_df["MORADORES"])/100
    setores_cobertos_df['MORADORES_COBERTOS'] = setores_cobertos_df['MORADORES_COBERTOS'].apply(np.floor).astype(int)
    setores_cobertos_df["AREA_COBERTA_M2"] = (setores_cobertos_df["pct"] * setores_cobertos_df["AREA_M2"])/100
    
    return setores_cobertos_df


# -----------------------------------------------------------------------------------------------------------------------------------------


def setores_urbanos_cobertos(setores_cobertos_df, cod_municipio):

    # Setores censitários urbanos do município de outorga, com código cod_municipio, atingidos pela mancha de cobertura.

    filtro_setores_urbanos = setores_cobertos_df.TIPO == "URBANO"
    filtro_cod_municipio = setores_cobertos_df.CD_GEOCODM == cod_municipio
    setores_urbanos_cobertos_df = setores_urbanos_cobertos_df[filtro_setores_urbanos & filtro_cod_municipio]
    setores_urbanos_cobertos_df = setores_urbanos_cobertos_df.reset_index(drop=True)
    colunas = ["pct", "CD_GEOCODI", "TIPO", "CD_GEOCODM", "NM_MUNICIP", "MORADORES", "AREA_M2", "MORADORES_COBERTOS", "AREA_COBERTA_M2"]
    setores_urbanos_cobertos_df = setores_urbanos_cobertos_df[colunas]
    setores_urbanos_cobertos_df = setores_urbanos_cobertos_df.reset_index(drop=True)
    
    return setores_urbanos_cobertos_df


# -----------------------------------------------------------------------------------------------------------------------------------------


def setores_censitarios_2010(arquivo_shp = r"/Users/hygson/Documents/3-Recursos/Dados/Setores Censitarios/Mosaico/Atlas_IBGE_Setores_Censitarios.shp"):
    
    import pandas as pd
    import geopandas as gpd
    
    setores_censitarios_2010_gdf = gpd.read_file(arquivo_shp, encoding='utf-8')
    setores_censitarios_2010_df = pd.DataFrame(setores_censitarios_2010_gdf)
    setores_censitarios_2010_df['DOMICILIOS'] = setores_censitarios_2010_df['DOMICILIOS'].fillna(0)
    setores_censitarios_2010_df['MORADORES'] = setores_censitarios_2010_df['MORADORES'].fillna(0)
    setores_censitarios_2010_df['AREA_M2'] = setores_censitarios_2010_df['AREA_M2'].fillna(0)
    setores_censitarios_2010_df['DOMICILIOS'] = setores_censitarios_2010_df['DOMICILIOS'].astype(float).astype(int)
    setores_censitarios_2010_df['MORADORES'] = setores_censitarios_2010_df['MORADORES'].astype(float).astype(int)
    setores_censitarios_2010_df['AREA_M2'] = setores_censitarios_2010_df['AREA_M2'].astype(float)
    
    colunas_importantes = ["CD_GEOCODI", "TIPO", "CD_GEOCODM", "NM_MUNICIP", "MORADORES", "AREA_M2"]
    setores_censitarios_2010_df = setores_censitarios_2010_df[colunas_importantes]
    setores_censitarios_2010_df = setores_censitarios_2010_df.reset_index(drop=True)
    
    return setores_censitarios_2010_df

# -----------------------------------------------------------------------------------------------------------------------------------------


def setores_censitarios_2021(arquivo_shp = r"/Users/hygson/Documents/3-Recursos/Dados/Setores Censitários/BR_Setores_2021/BR_Setores_2021.shp"):
    
    import pandas as pd
    import geopandas as gpd
    
    setores_censitarios_2021_gdf = gpd.read_file(arquivo_shp, encoding='utf-8')
    setores_censitarios_2021_df = pd.DataFrame(setores_censitarios_2021_gdf)
    
    colunas_importantes = ["CD_SETOR", "CD_SIT", "SIGLA_UF", "CD_MUN", "NM_MUN"]
    setores_censitarios_2021_df = setores_censitarios_2021_df[colunas_importantes]
    setores_censitarios_2021_df = setores_censitarios_2021_df.reset_index(drop=True)
    
    return setores_censitarios_2021_df


# -----------------------------------------------------------------------------------------------------------------------------------------


def setores_urbanos_municipio(path_setores, cod_municipio):
    
    # Exemplo:
    # cod_municipio = '5106257' # Nova Xavantina
    # path_setores = r"C:\Users\hygso\Google Drive\Dados\Setores Censitários\Mosaico\Atlas_IBGE_Setores_Censitarios.shp"
    
    import pandas as pd
    import geopandas as gpd
    
    # Setores censitários urbanos do município de outorga

    gdf_setores_censitarios = gpd.read_file(path_setores, encoding='utf-8')
    df_setores_censitarios = pd.DataFrame(gdf_setores_censitarios)
    df_setores_censitarios['DOMICILIOS'] = df_setores_censitarios['DOMICILIOS'].fillna(0)
    df_setores_censitarios['MORADORES'] = df_setores_censitarios['MORADORES'].fillna(0)
    df_setores_censitarios['AREA_M2'] = df_setores_censitarios['AREA_M2'].fillna(0)
    df_setores_censitarios['DOMICILIOS'] = df_setores_censitarios['DOMICILIOS'].astype(float).astype(int)
    df_setores_censitarios['MORADORES'] = df_setores_censitarios['MORADORES'].astype(float).astype(int)
    df_setores_censitarios['AREA_M2'] = df_setores_censitarios['AREA_M2'].astype(float)
    
    filtro_setores_urbanos = df_setores_censitarios.TIPO == "URBANO"
    filtro_cod_municipio = df_setores_censitarios.CD_GEOCODM == cod_municipio
    setores_urbanos_municipio_df = df_setores_censitarios[filtro_setores_urbanos & filtro_cod_municipio]
    setores_urbanos_municipio_df = setores_urbanos_municipio_df.reset_index(drop=True)
    colunas_importantes = ["CD_GEOCODI", "TIPO", "CD_GEOCODM", "NM_MUNICIP", "MORADORES", "AREA_M2"]
    setores_urbanos_municipio_df = setores_urbanos_municipio_df[colunas_importantes]
    setores_urbanos_municipio_df = setores_urbanos_municipio_df.reset_index(drop=True)
    
    return setores_urbanos_municipio_df
    
    
# -----------------------------------------------------------------------------------------------------------------------------------------  


def situacao_setor(CD_SIT, NM_MUN, NM_DIST):

    # Cidade é a localidade  onde  está  sediada  a  Prefeitura  Municipal. É constituída pela área urbana do distrito sede e 
    # delimitada pelo perímetro urbano (setores tipos 1 e 2) estabelecido por lei municipal. 
    
    # Setores censitários urbanos de cidades são aqueles cujo nome do município (NM_MUN) é o mesmo do nome do distrito (NM_DIST) sede.
    
    if CD_SIT in ['1', '2']:
        if NM_MUN == NM_DIST:
            return 'área urbana de cidade'
        else:
            return 'área urbana'
    elif CD_SIT == '3':
        return 'núcleo urbano'
    elif CD_SIT in ['5', '6', '7']:
        return 'aglomerado rural'
    elif CD_SIT == '8':
        return 'área rural'
    elif CD_SIT == '9':
        return "massa d'água"


# -----------------------------------------------------------------------------------------------------------------------------------------


def cobertura(setores_urbanos_atingidos_df, setores_urbanos_municipio_df):

    # Cobertura dos moradores urbanos do município de outorga

    num_moradores_urbanos_cobertos = setores_urbanos_atingidos_df["MORADORES_COBERTOS"].sum()
    num_moradores_urbanos_municipio = setores_urbanos_municipio_df["MORADORES"].sum()
    cobertura_moradores_urbanos = (num_moradores_urbanos_cobertos/num_moradores_urbanos_municipio)*100

    moradores_urbanos = {"cobertos": num_moradores_urbanos_cobertos,
                         "municipio": num_moradores_urbanos_municipio,
                         "cobertura": cobertura_moradores_urbanos}

    #print(f"Número de moradores urbanos cobertos: {num_moradores_urbanos_cobertos}")
    #print(f"Número de moradores urbanos do município de outorga: {num_moradores_urbanos_municipio}")
    #print(f"Cobertura dos moradores urbanos do município de outorga: {cobertura_moradores_urbanos:.3f} %")

    # Cobertura da área urbana do município de outorga

    area_urbana_coberta = setores_urbanos_atingidos_df["AREA_COBERTA_M2"].sum()
    area_urbana_municipio = setores_urbanos_municipio_df["AREA_M2"].sum()
    cobertura_area_urbana = (area_urbana_coberta / area_urbana_municipio)*100

    area_urbana = {"coberta": area_urbana_coberta,
                   "municipio": area_urbana_municipio,
                   "cobertura": cobertura_area_urbana}

    #print(f"Área urbana coberta: {area_urbana_coberta:.3f} m2")
    #print(f"Área urbana do município de outorga: {area_urbana_municipio:.3f} m2")
    #print(f"Cobertura da área urbana do município de outorga: {cobertura_area_urbana:.3f} %")
    
    return (moradores_urbanos, area_urbana)


# -----------------------------------------------------------------------------------------------------------------------------------------


def plano_basico(arquivo = r"/Users/hygson/Documents/3-Recursos/Dados/Radiodifusao/Canais/TV_FM_OM.csv"):
    
    # O arquivo foi baixado do site:
    # https://informacoes.anatel.gov.br/paineis/outorga-e-licenciamento/estacoes-de-tv-fm-e-om
    
    import pandas as pd
    import numpy as np

    # Colunas para importar
    lista_colunas = ['_id',
                 'SiglaServico', 
                 'Serviço Mongo',
                 'srd_planobasico_SiglaUF',
                 'srd_planobasico_NomeMunicipio',
                 'Município-UF',
                 'Canal',
                 'Decalagem',
                 'Frequência',
                 'Classe',
                 'Categoria da Estação',
                 'Local Específico',
                 'ERP',
                 'Serviço-Status',
                 'Sigla Status', 
                 'Entidade', 
                 'CNPJ',
                 'NumFistel',
                 'Caráter',
                 'Finalidade Cód',
                 'Fistel Geradora',
                 'sei_NumProcesso',
                 'Fase',
                 'Data',
                 'srd_planobasico_TxtObservacao',
                 'HCI',
                 'Latitude Decimal SRD',
                 'Longitude Decimal SRD',
                 'Latitude GMS SRD',
                 'Longitude GMS SRD',
                 'NumServico MONGO',
                 'Status Descrição',
                 'Finalidade'
                ]

    # Tipos das colunas
    tipos_colunas = {'_id': str,
                 'SiglaServico': str, 
                 'Serviço Mongo': str,
                 'srd_planobasico_SiglaUF': str,
                 'srd_planobasico_NomeMunicipio': str,
                 'Município-UF': str,
                 'Canal': str,
                 'Decalagem': str,
                 'Frequência': str,
                 'Classe': str,
                 'Categoria da Estação': str,
                 'Local Específico': str,
                 'ERP': str,
                 'Serviço-Status': str,
                 'Sigla Status': str, 
                 'Entidade': str, 
                 'CNPJ': str,
                 'NumFistel': str,
                 'Caráter': str,
                 'Finalidade Cód': str,
                 'Fistel Geradora': str,
                 'sei_NumProcesso': str,
                 'Fase': str,
                 'Data': str,
                 'srd_planobasico_TxtObservacao': str,
                 'HCI': str,
                 'Latitude Decimal SRD': str,
                 'Longitude Decimal SRD': str,
                 'Latitude GMS SRD': str,
                 'Longitude GMS SRD': str,
                 'NumServico MONGO': str,
                 'Status Descrição': str,
                 'Finalidade': str
                 } 

    # Importação do arquivo
    df = pd.read_csv(arquivo,
                 sep = ";",
                 encoding = "utf-8",
                 usecols = lista_colunas,
                 dtype = tipos_colunas
                )

    # Renomeando colunas
    nomes_colunas = {'_id': 'ID',
                 'SiglaServico': 'Serviço', 
                 'srd_planobasico_SiglaUF': 'UF',
                 'srd_planobasico_NomeMunicipio': 'Município',
                 'Serviço-Status': 'Status', 
                 'Sigla Status': 'Sigla do Status', 
                 'NumFistel': 'Fistel',
                 'Finalidade Cód': 'Cód. da Finalildade',
                 'Fistel Geradora': 'Fistel da Geradora',
                 'sei_NumProcesso': 'Processo SEI',
                 'srd_planobasico_TxtObservacao': 'Observações',
                 'Latitude Decimal SRD': 'Latitude',
                 'Longitude Decimal SRD': 'Longitude',
                 'Latitude GMS SRD':  'Latitude GMS',
                 'Longitude GMS SRD': 'Longitude GMS',
                 'NumServico MONGO':  'N.º do Serviço',
                 'Status Descrição': 'Descrição do Status'
                 } 
    df = df.rename(columns=nomes_colunas)

    # Modificando o tipo de algumas colunas e tratando os valores NaN
    df['Frequência'] = df['Frequência'].replace({',': '.'}, regex=True)
    df['ERP'] = df['ERP'].replace({',': '.'}, regex=True)
    df['HCI'] = df['HCI'].replace({',': '.'}, regex=True)
    df['Latitude'] = df['Latitude'].replace({',': '.'}, regex=True)
    df['Longitude'] = df['Longitude'].replace({',': '.'}, regex=True)
    df[['Canal', 'Frequência', 'ERP', 'HCI', 'Latitude', 'Longitude', 'N.º do Serviço']] = df[['Canal', 'Frequência', 'ERP', 'HCI', 'Latitude', 'Longitude', 'N.º do Serviço']].apply(pd.to_numeric)
    df[['Canal', 'Frequência', 'ERP', 'HCI', 'Latitude', 'Longitude']] = df[['Canal', 'Frequência', 'ERP', 'HCI', 'Latitude', 'Longitude']].fillna(0)
    df['Decalagem'] = df['Decalagem'].replace(np.nan, 'Nenhuma')
    df['Categoria da Estação'] = df['Categoria da Estação'].replace(np.nan, 'Desconhecida')
    df['Classe'] = df['Classe'].replace(np.nan, 'Desconhecida')
    df['Local Específico'] = df['Local Específico'].replace(np.nan, 'Nenhum')
    df['Entidade'] = df['Entidade'].replace(np.nan, 'Nenhuma')
    df['CNPJ'] = df['CNPJ'].replace(np.nan, 'Nenhum')
    df['Fistel'] = df['Fistel'].replace(np.nan, 'Nenhum')
    df['Cód. da Finalildade'] = df['Cód. da Finalildade'].replace(np.nan, 'Nenhum')
    df['Fistel da Geradora'] = df['Fistel da Geradora'].replace(np.nan, 'NA')
    df['Processo SEI'] = df['Processo SEI'].replace(np.nan, 'Nenhum')
    df['Observações'] = df['Observações'].replace(np.nan, 'Nenhuma')
    df['Finalidade'] = df['Finalidade'].replace(np.nan, 'Desconhecida')
    df['Fase'] = df['Fase'].replace(np.nan, 'Desconhecida')
    df['Canal'] = df['Canal'].astype(int)
    
    return df


# -----------------------------------------------------------------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------------------------------------------------------------


def pbtvd(arquivo = r"/Users/hygson/Documents/3-Recursos/Dados/Radiodifusao/TV_FM_OM.csv"):
    
    # O arquivo foi baixado do site:
    # https://informacoes.anatel.gov.br/paineis/outorga-e-licenciamento/estacoes-de-tv-fm-e-om
    
    import pandas as pd
    import numpy as np

    # Colunas para importar
    lista_colunas = ['_id',
                 'SiglaServico', 
                 'Serviço Mongo',
                 'srd_planobasico_SiglaUF',
                 'srd_planobasico_NomeMunicipio',
                 'Município-UF',
                 'Canal',
                 'Decalagem',
                 'Frequência',
                 'Classe',
                 'Categoria da Estação',
                 'Local Específico',
                 'ERP',
                 'Serviço-Status',
                 'Sigla Status', 
                 'Entidade', 
                 'CNPJ',
                 'NumFistel',
                 'Caráter',
                 'Finalidade Cód',
                 'Fistel Geradora',
                 'sei_NumProcesso',
                 'Fase',
                 'Data',
                 'srd_planobasico_TxtObservacao',
                 'HCI',
                 'Latitude Decimal SRD',
                 'Longitude Decimal SRD',
                 'Latitude GMS SRD',
                 'Longitude GMS SRD',
                 'NumServico MONGO',
                 'Status Descrição',
                 'Finalidade'
                ]

    # Tipos das colunas
    tipos_colunas = {'_id': str,
                 'SiglaServico': str, 
                 'Serviço Mongo': str,
                 'srd_planobasico_SiglaUF': str,
                 'srd_planobasico_NomeMunicipio': str,
                 'Município-UF': str,
                 'Canal': str,
                 'Decalagem': str,
                 'Frequência': str,
                 'Classe': str,
                 'Categoria da Estação': str,
                 'Local Específico': str,
                 'ERP': str,
                 'Serviço-Status': str,
                 'Sigla Status': str, 
                 'Entidade': str, 
                 'CNPJ': str,
                 'NumFistel': str,
                 'Caráter': str,
                 'Finalidade Cód': str,
                 'Fistel Geradora': str,
                 'sei_NumProcesso': str,
                 'Fase': str,
                 'Data': str,
                 'srd_planobasico_TxtObservacao': str,
                 'HCI': str,
                 'Latitude Decimal SRD': str,
                 'Longitude Decimal SRD': str,
                 'Latitude GMS SRD': str,
                 'Longitude GMS SRD': str,
                 'NumServico MONGO': str,
                 'Status Descrição': str,
                 'Finalidade': str
                 } 

    # Importação do arquivo
    df = pd.read_csv(arquivo,
                 sep = ";",
                 encoding = "utf-8",
                 usecols = lista_colunas,
                 dtype = tipos_colunas
                )

    # Renomeando colunas
    nomes_colunas = {'_id': 'ID',
                 'SiglaServico': 'Serviço', 
                 'srd_planobasico_SiglaUF': 'UF',
                 'srd_planobasico_NomeMunicipio': 'Município',
                 'Serviço-Status': 'Status', 
                 'Sigla Status': 'Sigla do Status', 
                 'NumFistel': 'Fistel',
                 'Finalidade Cód': 'Cód. da Finalildade',
                 'Fistel Geradora': 'Fistel da Geradora',
                 'sei_NumProcesso': 'Processo SEI',
                 'srd_planobasico_TxtObservacao': 'Observações',
                 'Latitude Decimal SRD': 'Latitude',
                 'Longitude Decimal SRD': 'Longitude',
                 'Latitude GMS SRD':  'Latitude GMS',
                 'Longitude GMS SRD': 'Longitude GMS',
                 'NumServico MONGO':  'N.º do Serviço',
                 'Status Descrição': 'Descrição do Status'
                 } 
    df = df.rename(columns=nomes_colunas)

    # Modificando o tipo de algumas colunas e tratando os valores NaN
    df['Frequência'] = df['Frequência'].replace({',': '.'}, regex=True)
    df['ERP'] = df['ERP'].replace({',': '.'}, regex=True)
    df['HCI'] = df['HCI'].replace({',': '.'}, regex=True)
    df['Latitude'] = df['Latitude'].replace({',': '.'}, regex=True)
    df['Longitude'] = df['Longitude'].replace({',': '.'}, regex=True)
    df[['Canal', 'Frequência', 'ERP', 'HCI', 'Latitude', 'Longitude', 'N.º do Serviço']] = df[['Canal', 'Frequência', 'ERP', 'HCI', 'Latitude', 'Longitude', 'N.º do Serviço']].apply(pd.to_numeric)
    df[['Canal', 'Frequência', 'ERP', 'HCI', 'Latitude', 'Longitude']] = df[['Canal', 'Frequência', 'ERP', 'HCI', 'Latitude', 'Longitude']].fillna(0)
    df['Decalagem'] = df['Decalagem'].replace(np.nan, 'Nenhuma')
    df['Categoria da Estação'] = df['Categoria da Estação'].replace(np.nan, 'Desconhecida')
    df['Classe'] = df['Classe'].replace(np.nan, 'Desconhecida')
    df['Local Específico'] = df['Local Específico'].replace(np.nan, 'Nenhum')
    df['Entidade'] = df['Entidade'].replace(np.nan, 'Nenhuma')
    df['CNPJ'] = df['CNPJ'].replace(np.nan, 'Nenhum')
    df['Fistel'] = df['Fistel'].replace(np.nan, 'Nenhum')
    df['Cód. da Finalildade'] = df['Cód. da Finalildade'].replace(np.nan, 'Nenhum')
    df['Fistel da Geradora'] = df['Fistel da Geradora'].replace(np.nan, 'NA')
    df['Processo SEI'] = df['Processo SEI'].replace(np.nan, 'Nenhum')
    df['Observações'] = df['Observações'].replace(np.nan, 'Nenhuma')
    df['Finalidade'] = df['Finalidade'].replace(np.nan, 'Desconhecida')
    df['Fase'] = df['Fase'].replace(np.nan, 'Desconhecida')
    df['Canal'] = df['Canal'].astype(int)
    
    # Canais de TV digital (GTVD, PBTVD e RTVD)
    canais_tv_digital = ['GTVD', 'PBTVD', 'RTVD']
    filtro_pbtvd = df['Serviço'].isin(canais_tv_digital)
    df_pbtvd = df[filtro_pbtvd]
    df_pbtvd = df_pbtvd.reset_index(drop=True)

    return df_pbtvd


# -----------------------------------------------------------------------------------------------------------------------------------------


def pbtvd_antigo(arquivo_xml_tv_fm = r"/Users/hygson/Documents/3-Recursos/Dados/Canais/plano_basicoTVFM.xml"):
    
    # Exemplo:
    # arquivo_xml = r"/Users/hygson/Documents/Dados/Canais/plano_basicoTVFM.xml"
    
    # O arquivo_xml é baixado do site http://sistemas.anatel.gov.br/siscom =
    # = http://sistemas.anatel.gov.br/se/public/view/b/srd.php
    
    import xml.etree.ElementTree as ET
    import requests
    import pandas as pd

    tree =  ET.parse(arquivo_xml_tv_fm)
    root = tree.getroot()

    entidades = []
    ids_canal = []
    ufs = []
    municipios = []
    canais = []
    frequencias = []
    classes = []
    servicos = []
    statuss = []
    latitudes = []
    longitudes = []
    cnpjs = []
    fistels = []
    IdtPlanoBasicos = []
    CodMunicipios = []
    erps = []
    alturas = []
    decalagens = []
    caraters = []
    finalidades = []
    limitacoes = []
    observacoes = []

    for node in root.findall('row'): 
        uf = node.attrib.get("UF")
        ufs.append(uf)
        municipio = node.get("Municipio")
        municipios.append(municipio)
        canal = node.get("Canal")
        canais.append(canal)
        frequencia = node.get("Frequência")
        frequencias.append(frequencia)
        classe = node.get("Classe")
        classes.append(classe)
        servico = node.get("Servico")
        servicos.append(servico)
        status = node.get("Status")
        statuss.append(status)
        entidade = node.get("Entidade")
        entidades.append(entidade)
        latitude = node.get("Latitude")
        latitudes.append(latitude)
        longitude = node.get("Longitude")
        longitudes.append(longitude)
        cnpj = node.get("CNPJ")
        cnpjs.append(cnpj)
        fistel = node.get("Fistel")
        fistels.append(fistel)
        id_canal = node.get("id")
        ids_canal.append(id_canal)
        IdtPlanoBasico = node.get("IdtPlanoBasico")
        IdtPlanoBasicos.append(IdtPlanoBasico)
        CodMunicipio = node.get("CodMunicipio")
        CodMunicipios.append(CodMunicipio)
        erp = node.get("ERP")
        erps.append(erp)
        altura = node.get("Altura")
        alturas.append(altura)
        decalagem = node.get("Decalagem")
        decalagens.append(decalagem)
        carater = node.get("Carater")
        caraters.append(carater)
        finalidade = node.get("Finalidade")
        finalidades.append(finalidade)
        limitacao = node.get("Limitacoes")
        limitacoes.append(limitacao)
        observacao = node.get("Observacoes")
        observacoes.append(observacao)

    dados = {'entidade': entidades,
             'cnpj': cnpjs,
             'fistel': fistels,
             'id_canal': ids_canal,
             'uf': ufs,
             'municipio': municipios,
             'CodMunicipio': CodMunicipios,
             'servico': servicos,
             'carater': caraters,
             'finalidade': finalidades,
             'canal': canais,
             'decalagem': decalagens,
             'classe': classes,
             'frequencia': frequencias,
             'status': statuss,
             'latitude': latitudes,
             'longitude': longitudes,
             'IdtPlanoBasico': IdtPlanoBasicos,
             'erp': erps,
             'altura': alturas,
             'limitacoes': limitacoes,
             'observacoes': observacoes}

    # Canais de TV e FM
    canais_tvfm_df = pd.DataFrame(dados)
    canais_tvfm_df = canais_tvfm_df.apply(lambda x: x.str.replace(',','.'))
    canais_tvfm_df[["canal", "frequencia", "latitude", "longitude", "erp", "altura"]] = canais_tvfm_df[["canal", "frequencia", "latitude",                   "longitude", "erp", "altura"]].apply(pd.to_numeric)
    
    # Canais de TV digital (GTVD, PBTVD e RTVD)
    canais_tv_digital = ['GTVD', 'PBTVD', 'RTVD']
    filtro_pbtvd = canais_tvfm_df['servico'].isin(canais_tv_digital)
    canais_pbtvd_df = canais_tvfm_df[filtro_pbtvd]
    canais_pbtvd_df = canais_pbtvd_df.reset_index(drop=True)

    return canais_pbtvd_df


# -----------------------------------------------------------------------------------------------------------------------------------------


def canais_pb(arquivo_xml):
    
    # Exemplo:
    # arquivo_xml = r"C:\Users\hygso\Google Drive\Dados\Canais de Radiodifusão\plano_basicoTVFM.xml"
    
    # O arquivo_xml é baixado do site http://sistemas.anatel.gov.br/siscom =
    # = http://sistemas.anatel.gov.br/se/public/view/b/srd.php
    
    import xml.etree.ElementTree as ET
    import requests
    import pandas as pd

    tree =  ET.parse(arquivo_xml)
    root = tree.getroot()

    entidades = []
    ids_canal = []
    ufs = []
    municipios = []
    canais = []
    frequencias = []
    classes = []
    servicos = []
    statuss = []
    latitudes = []
    longitudes = []
    cnpjs = []
    fistels = []
    IdtPlanoBasicos = []
    CodMunicipios = []
    erps = []
    alturas = []

    for node in root.findall('row'): 
        uf = node.attrib.get("UF")
        ufs.append(uf)
        municipio = node.get("Municipio")
        municipios.append(municipio)
        canal = node.get("Canal")
        canais.append(canal)
        frequencia = node.get("Frequência")
        frequencias.append(frequencia)
        classe = node.get("Classe")
        classes.append(classe)
        servico = node.get("Servico")
        servicos.append(servico)
        status = node.get("Status")
        statuss.append(status)
        entidade = node.get("Entidade")
        entidades.append(entidade)
        latitude = node.get("Latitude")
        latitudes.append(latitude)
        longitude = node.get("Longitude")
        longitudes.append(longitude)
        cnpj = node.get("CNPJ")
        cnpjs.append(cnpj)
        fistel = node.get("Fistel")
        fistels.append(fistel)
        id_canal = node.get("id")
        ids_canal.append(id_canal)
        IdtPlanoBasico = node.get("IdtPlanoBasico")
        IdtPlanoBasicos.append(IdtPlanoBasico)
        CodMunicipio = node.get("CodMunicipio")
        CodMunicipios.append(CodMunicipio)
        erp = node.get("ERP")
        erps.append(erp)
        altura = node.get("Altura")
        alturas.append(altura)

    dados = {'entidade': entidades,
             'cnpj': cnpjs,
             'fistel': fistels,
             'id_canal': ids_canal,
             'uf': ufs,
             'municipio': municipios,
             'CodMunicipio': CodMunicipios,
             'servico': servicos,
             'canal': canais,
             'classe': classes,
             'frequencia': frequencias,
             'status': statuss,
             'latitude': latitudes,
             'longitude': longitudes,
             'IdtPlanoBasico': IdtPlanoBasicos,
             'erp': erps,
             'altura': alturas}

    canais_pb_df = pd.DataFrame(dados)
    canais_pb_df = canais_pb_df.apply(lambda x: x.str.replace(',','.'))
    canais_pb_df[["canal", "frequencia", "latitude", "longitude"]] = canais_pb_df[["canal", "frequencia", "latitude",                   "longitude"]].apply(pd.to_numeric)

    return canais_pb_df


# -----------------------------------------------------------------------------------------------------------------------------------------


def altera_colunas_mosaico(canais_df):
    
    # Altera colunas do dataframe para importar no Mosaico

    # Alteração do nome de colunas
    canais_mosaico_df = canais_df.rename(columns={"id_canal": "dbid", 
                                                  "canal": "channel", 
                                                  "frequencia": "frequency",
                                                  "classe": "stnClass",
                                                  "entidade": "licensee",
                                                  "fistel": "NumFistel",
                                                  "status": "app_status",
                                                  "altura": "antenna_height"})

    # Inserção de novas colunas
    canais_mosaico_df["onoff"] = 1
    canais_mosaico_df["dic"] = 1
    canais_mosaico_df["uid"] = 1
    canais_mosaico_df["antenna_name"] = canais_mosaico_df["dbid"] + ".prn"

    # Remoção de colunas
    canais_mosaico_df = canais_mosaico_df.drop(['cnpj', 'servico'], axis=1)
    
    return canais_mosaico_df
    

# -----------------------------------------------------------------------------------------------------------------------------------------


def latitude_decimal_para_gms(latitude_decimal):

    lat = abs(latitude_decimal)
    graus = int(divmod(lat, 1)[0])
    M = (lat - graus)*60
    minutos = int(divmod(M, 1)[0])
    segundos = round((M - minutos)*60, 2)
    
    if "-" in str(latitude_decimal):
        return f"{graus}° {minutos}' {segundos}'' S"
    else:
        return f"{graus}° {minutos}' {segundos}'' N"


# -----------------------------------------------------------------------------------------------------------------------------------------


def latitude_gms_para_decimal(latitude_gms):

    g = float(latitude_gms.split('°')[0])
    m = float(latitude_gms.split('°')[1].split("'")[0])
    s = float(latitude_gms.split('°')[1].split("'")[1])
    latitude = g + m/60 + s/3600
    
    if latitude_gms[-1] == 'S':
        latitude = -latitude

    return latitude


# -----------------------------------------------------------------------------------------------------------------------------------------


def longitude_decimal_para_gms(longitude_decimal):

    lon = abs(longitude_decimal)
    graus = int(divmod(lon, 1)[0])
    M = (lon - graus)*60
    minutos = int(divmod(M, 1)[0])
    segundos = round((M - minutos)*60, 2)
    
    if "-" in str(longitude_decimal):
        return f"{graus}° {minutos}' {segundos}'' W"
    else:
        return f"{graus}° {minutos}' {segundos}'' L"


# -----------------------------------------------------------------------------------------------------------------------------------------


def longitude_gms_para_decimal(longitude_gms):

    g = float(longitude_gms.split('°')[0])
    m = float(longitude_gms.split('°')[1].split("'")[0])
    s = float(longitude_gms.split('°')[1].split("'")[1])
    longitude = g + m/60 + s/3600
    
    if longitude_gms[-1] == 'W':
        longitude = -longitude

    return longitude


# -----------------------------------------------------------------------------------------------------------------------------------------


def identifica_servico(canal):

    # Esta função identifica o tipo de serviço de um canal baseado apenas no número do seu canal.
    
    if '+' in str(canal) or '-' in str(canal):
        return 'TV'
    elif len(str(int(canal))) > 2:
        return 'FM'
    else:
        return 'TV'


# -----------------------------------------------------------------------------------------------------------------------------------------


def mudanca_de_classe(classe_atual, classe_proposta): 

    classes = ['C', 'B2', 'B1', 'A4', 'A3', 'A2', 'A1', 'E3', 'E2', 'E1']

    if classe_atual in classes:

        if classe_proposta in classes:
        
            if classes.index(classe_atual) == classes.index(classe_proposta):
                return "sem mudança de classe"
            elif classes.index(classe_atual) < classes.index(classe_proposta):
                return "promoção de classe"
            elif classes.index(classe_atual) > classes.index(classe_proposta):
                return "redução de classe"
        else:
            return 'classe proposta inexistente'

    else:
        if classe_proposta not in classes:
            return 'classe atual e proposta inexistentes'
        return 'classe atual inexistente'


# -----------------------------------------------------------------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------------------------------------------------------------


def mudanca_de_grupo(classe_atual, classe_proposta): 

    classes = ['C', 'B2', 'B1', 'A4', 'A3', 'A2', 'A1', 'E3', 'E2', 'E1']
    grupos = ['A', 'B', 'C']

    if classe_atual in classes:

        if classe_proposta in classes:

            grupo_atual = grupo_enquadramento(classe_atual)
            grupo_proposto = grupo_enquadramento(classe_proposta)
        
            if grupos.index(grupo_atual) == grupos.index(grupo_proposto):
                return f"sem mudança de grupo - {grupo_atual}"
            elif grupos.index(grupo_atual) < grupos.index(grupo_proposto):
                return f"promoção de grupo - {grupo_atual} para {grupo_proposto}"
            elif grupos.index(grupo_atual) > grupos.index(grupo_proposto):
                return f"redução de grupo - {grupo_atual} para {grupo_proposto}"
                
        else:
            return 'classe proposta inexistente'

    else:
        if classe_proposta not in classes:
            return 'classe atual e proposta inexistentes'
        return 'classe atual inexistente'


# -----------------------------------------------------------------------------------------------------------------------------------------


def tcp(classe_atual, classe_proposta):   

    # Esta função retorna o tempo mínimo, em anos, para se atingir a classe desejada para o serviço de FM.
    # sem ter que pagar valor adicional de promoção de classe.

    if mudanca_de_classe(classe_atual, classe_proposta) == "promoção de classe":
        
        if classe_atual == 'C':
            if classe_proposta in ['B2', 'B1']:
                return 0
            elif classe_proposta in ['A4', 'A3']:
                return 2
            elif classe_proposta in ['A2', 'A1']:
                return 6
            elif classe_proposta == 'E3':
                return 8
            elif classe_proposta == 'E2':
                return 10
            elif classe_proposta == 'E1':
                return 12
    
        elif classe_atual == 'B2':
            if classe_proposta in ['B1', 'A4']:
                return 0
            elif classe_proposta == 'A3':
                return 2
            elif classe_proposta in ['A2', 'A1']:
                return 4
            elif classe_proposta == 'E3':
                return 6
            elif classe_proposta == 'E2':
                return 8
            elif classe_proposta == 'E1':
                return 10
    
        elif classe_atual == 'B1':
            if classe_proposta in ['A4', 'A3']:
                return 0
            elif classe_proposta in ['A2', 'A1']:
                return 2
            elif classe_proposta == 'E3':
                return 4
            elif classe_proposta == 'E2':
                return 6
            elif classe_proposta == 'E1':
                return 8
    
        elif classe_atual == 'A4':
            if classe_proposta in ['A3', 'A2']:
                return 0
            elif classe_proposta == 'A1':
                return 2
            elif classe_proposta == 'E3':
                return 4
            elif classe_proposta == 'E2':
                return 6
            elif classe_proposta == 'E1':
                return 8
    
        elif classe_atual == 'A3':
            if classe_proposta in ['A2', 'A1']:
                return 0
            elif classe_proposta == 'E3':
                return 2
            elif classe_proposta == 'E2':
                return 4
            elif classe_proposta == 'E1':
                return 6
    
        elif classe_atual == 'A2':
            if classe_proposta == 'A1':
                return 0
            elif classe_proposta == 'E3':
                return 2
            elif classe_proposta == 'E2':
                return 4
            elif classe_proposta == 'E1':
                return 6
    
        elif classe_atual == 'A1':
            if classe_proposta == 'E3':
                return 0
            elif classe_proposta == 'E2':
                return 2
            elif classe_proposta == 'E1':
                return 4
    
        elif classe_atual == 'E3':
            if classe_proposta == 'E2':
                return 0
            elif classe_proposta == 'E1':
                return 2
    
        elif classe_atual == 'E2':
            if classe_proposta == 'E1':
                return 0
    else:
        return "não se aplica"


# -----------------------------------------------------------------------------------------------------------------------------------------


def verifica_cobranca(classe_atual, classe_proposta):   
    if "redução de grupo" in mudanca_de_grupo(classe_atual, classe_proposta): 
        return "sem cobrança"
    elif "promoção de grupo" in mudanca_de_grupo(classe_atual, classe_proposta):
        return "com cobrança"
    elif "sem mudança de grupo" in mudanca_de_grupo(classe_atual, classe_proposta):
        if tcp(classe_atual, classe_proposta) == 0 or tcp(classe_atual, classe_proposta) == "não se aplica":
            return "sem cobrança"
        else:
            return "com cobrança"
    else:
        return "não se aplica"   
        

# -----------------------------------------------------------------------------------------------------------------------------------------


def tipo_de_mudanca(classe_atual, classe_proposta):    

    if mudanca_de_classe(classe_atual, classe_proposta) == "promoção de classe":
        if tcp(classe_atual, classe_proposta) == 0:
            return "gradual"
        else:
            return "não gradual"
    else:
        return "não se aplica"
        

# -----------------------------------------------------------------------------------------------------------------------------------------


def resumo_alteracao_pb(classe_atual, classe_proposta):    
    print(f"- Alteração de classe: {mudanca_de_classe(classe_atual, classe_proposta)}")
    print(f"- Grupo de enquadramento: {mudanca_de_grupo(classe_atual, classe_proposta)}")
    print(f"- Tcp = {tcp(classe_atual, classe_proposta)}")
    print(f"- Tipo de mudança: {tipo_de_mudanca(classe_atual, classe_proposta)}")
    print(f"- Cobrança: {verifica_cobranca(classe_atual, classe_proposta)}")

    
# -----------------------------------------------------------------------------------------------------------------------------------------


def valor_referencia(uf, enquadramento):    

    # Determinação do valor de referência - Anexo XXVIII da Portaria GM/MCom nº 9018/2023
    # Retorna o código, município e valor de referência
    
    if enquadramento == 'B':
        if uf == 'SC':
            return ['4205407', 'Florianópolis', 363499.72]
        elif uf == 'BA':
            return ['2927408', 'Salvador', 169291.50]
        elif uf == 'AM':
            return ['1302603', 'Manaus', 78099.69]
        elif uf == 'PA':
            return ['1501402', 'Belém', 85097.28]
        elif uf == 'SP':
            return ['3550308', 'Região Metropolitana de São Paulo', 2376643.72]
        elif uf == 'CE':
            return ['2304400', 'Fortaleza', 166419.21]
        elif uf == 'GO':
            return ['5208707', 'Goiânia', 235323.01]
        elif uf == 'SE':
            return ['2800308', 'Aracajú', 141640.89]
        elif uf == 'MG':
            return ['3106200', 'Belo Horizonte', 53718.66]
        elif uf == 'PB':
            return ['2507507', 'João Pessoa', 144582.39]        
        elif uf == 'MS':
            return ['5002704', 'Campo Grande', 215788.29]    
        elif uf == 'DF':
            return ['5300108', 'Brasília', 307127.24]
        elif uf == 'RO':
            return ['1100205', 'Porto Velho', 45590.69]
        elif uf == 'RJ':
            return ['3304557', 'Rio de Janeiro', 701663.27]
        elif uf == 'PR':
            return ['4106902', 'Curitiba', 469494.06]       
        elif uf == 'AL':
            return ['2704302', 'Maceió', 144040.28]        
        elif uf == 'PI':
            return ['2211001', 'Teresina', 144681.50]   
        elif uf == 'RS':
            return ['4314902', 'Porto Alegre', 425475.87]  
        elif uf == 'ES':
            return ['3205200', 'Vila Velha', 69587.43]  

    if enquadramento == 'C':
        if uf == 'SC':  
            return ['4205407', 'Florianópolis', 852817.55]
        elif uf == 'BA':
            return ['2927408', 'Salvador', 397584.59]
        elif uf == 'AM':
            return ['1302603', 'Manaus', 183187.51]
        elif uf == 'PA':
            return ['1501402', 'Belém', 199600.76]
        elif uf == 'SP':
            return ['3550308', 'Região Metropolitana de São Paulo', 5574558.80]
        elif uf == 'CE':
            return ['2304400', 'Fortaleza', 391262.94]
        elif uf == 'GO':
            return ['5208707', 'Goiânia', 551639.11]
        elif uf == 'SE':
            return ['2800308', 'Aracajú', 332431.61]
        elif uf == 'MG':
            return ['3106200', 'Belo Horizonte', 125672.29]
        elif uf == 'PB':
            return ['2507507', 'João Pessoa', 338855.67]  
        elif uf == 'MS':
            return ['5002704', 'Campo Grande', 505001.04] 
        elif uf == 'DF':
            return ['5300108', 'Brasília', 720385.32]
        elif uf == 'RO':
            return ['1100205', 'Porto Velho', 105637.44]
        elif uf == 'RJ':
            return ['3304557', 'Rio de Janeiro', 1629200.59]
        elif uf == 'PR':
            return ['4106902', 'Curitiba', 1098420.32]
        elif uf == 'AL':
            return ['2704302', 'Maceió', 337505.73]  
        elif uf == 'PI':
            return ['2211001', 'Teresina', 339511.65]  
        elif uf == 'RS':
            return ['4314902', 'Porto Alegre', 995714.32]  
        elif uf == 'ES':
            return ['3205200', 'Vila Velha', 79940.86] 


# -----------------------------------------------------------------------------------------------------------------------------------------

def mapa_estatico(gdf_municipios,
                  gdf_coord_municipios,
                  gdf_municipios_com_area_urbana_atingida_pelo_cp,
                  gdf_setores_censitarios_cidades,
                  gdf_intersecao_setores_urbanos_cp,
                  gdf_local_proposto,
                  gdf_contorno_protegido):
    
    import matplotlib.pyplot as plt
    import contextily as cx
    
    fig, ax = plt.subplots(1,1,figsize=(12,10))
    #ax.grid(color='grey', linestyle='--', linewidth=0.5)
    
    # Municípios atingidos pelo contorno protegido
    gdf_municipios.plot(ax=ax, color='None', edgecolor='black', linewidth=1)
    
    # Coordenadas dos municípios atingidos pelo contorno protegido
    gdf_coord_municipios.plot(ax=ax, color='white', edgecolor='black', linewidth=1)
    
    # Municípios com áreas urbanas atingidas pelo contorno protegido
    gdf_municipios_com_area_urbana_atingida_pelo_cp.plot(ax=ax, column='MUNICIPIO-UF', categorical=True, edgecolor='black', cmap='Set3', linewidth=2, alpha = 0.7, legend=True)
    
    # Setores urbanos dos municípios atingidos pelo contorno protegido
    gdf_setores_censitarios_cidades.plot(ax=ax, color='None', edgecolor='orange', linewidth=0.5)
    
    # Áreas urbanas atingidas pelo contorno protegido
    gdf_intersecao_setores_urbanos_cp.plot(ax=ax, color='None', edgecolor='red', linewidth=0.5)
    
    # Estação na situação proposta
    gdf_local_proposto.plot(ax=ax, color='yellow', edgecolor='black', linewidth=1.5)
    #ax.annotate("ESTAÇÃO", xy=(gdf_estacao.geometry.x, gdf_estacao.geometry.y), xytext=(3, 3), textcoords="offset points", fontsize=6, color='black')
    
    # Circunferência do contorno protegido teórico
    gdf_contorno_protegido.plot(ax = ax, color='none', edgecolor='red', linewidth=1.5, linestyle='dashed')
    
    cx.add_basemap(ax, crs=gdf_municipios.crs)
    
# -----------------------------------------------------------------------------------------------------------------------------------------    
    
@st.cache_data
def calcular_vpc(POPULACAO, 
                 CLASSE_ATUAL,
                 CLASSE_PROPOSTA,
                 municipio_local_proposto_uf,
                 codigos_municipios_cobertos,
                 Tcp):
    
    import pandas as pd

    ## Criar o dataframe com as populações dos municípios
    
    df_populacao = pd.read_excel(POPULACAO, sheet_name = "Tabela", header = 3)
    df_populacao.columns = ['Cod_Mun', 'Municipio', 'Populacao', 'Area_km2', 'Dens_Demo']
    df_populacao = df_populacao[:-1]
    df_populacao = df_populacao.astype({"Populacao":"int","Area_km2":"int"})
    
    ## Determinação do grupo de enquadramento na situação proposta (A para B ou B para C)
    
    grupo_atual = grupo_enquadramento(CLASSE_ATUAL)
    grupo_proposto = grupo_enquadramento(CLASSE_PROPOSTA)
    
    ## Determinação do município de referência
    # Anexo XXVIII da Portaria GM/MCom nº 9018/2023
    
    cod_municipio_referencia = valor_referencia(municipio_local_proposto_uf, 
                                                  grupo_proposto)[0]
    municipio_referencia = valor_referencia(municipio_local_proposto_uf, 
                                              grupo_proposto)[1]
    
    ## População dos municípios cobertos
    
    df_populacao_municipios_cobertos = df_populacao[df_populacao.Cod_Mun.isin(codigos_municipios_cobertos)]
    df_populacao_municipios_cobertos = df_populacao_municipios_cobertos.reset_index(drop=True)
    
    ## Cálculo do valor da promoção de classe 
    #(art. 34 da Portaria GM/MCom nº 9.018/2023)
    
    # população dos municípios cobertos
    Ptot = df_populacao_municipios_cobertos.Populacao.sum() 
    
    filtro_mun_ref = df_populacao["Cod_Mun"] == cod_municipio_referencia
    
    Tcp = int(Tcp)
    
    # população do município de referência
    if municipio_local_proposto_uf == 'SP': 
        Pref = int(20743587) 
    else:
        Pref = int(df_populacao[filtro_mun_ref]['Populacao'].values[0])
    
    if grupo_atual == 'A':
        if grupo_proposto == 'A':
            Vab, Vbc = 0, 0
        elif grupo_proposto == 'B':
            Vab = valor_referencia(municipio_local_proposto_uf, 
                                     grupo_proposto)[2]
            Vbc = 0
        elif grupo_proposto == 'C':
            Vab = valor_referencia(municipio_local_proposto_uf, 'B')[2]
            Vbc = valor_referencia(municipio_local_proposto_uf,
                                      grupo_proposto)[2]
    elif grupo_atual == 'B':
        if grupo_proposto == 'A':
            Vab, Vbc = 0, 0
        elif grupo_proposto == 'B':
            if Tcp == 0:
                Vab, Vbc = 0, 0
            else:
                Vab = valor_referencia(municipio_local_proposto_uf, 'B')[2]
                Vbc = 0
        elif grupo_proposto == 'C':
            Vab = 0
            Vbc = valor_referencia(municipio_local_proposto_uf,
                                      grupo_proposto)[2]
    elif grupo_atual == 'C':
        if grupo_proposto == 'A':
            Vab, Vbc = 0, 0
        elif grupo_proposto == 'B':
            Vab, Vbc = 0, 0
        elif grupo_proposto == 'C':
            if Tcp == 0:
                Vab, Vbc = 0, 0
            else:
                Vab = 0
                Vbc = valor_referencia(municipio_local_proposto_uf, 'C')[2] 
                
    if Tcp != 'não se aplica':
        Vpc = (Ptot/Pref) * (Vab + Vbc) * (1+Tcp/10)
        Vpc = round(Vpc,2)
        Tcp = str(Tcp)
    else:
        Vpc = 'não se aplica'
        
    return {'grupo proposto': grupo_proposto,
            'município de referência': municipio_referencia,
            'Pref': Pref,
            'Ptot': Ptot,
            'Vab': Vab,
            'Vbc': Vbc,
            'Vpc': Vpc,
            'df_populacao': df_populacao_municipios_cobertos,
            }



    
    