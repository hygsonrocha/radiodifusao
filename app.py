# ---------------------------------------------------------------------
# BIBLIOTECAS
# ---------------------------------------------------------------------

import streamlit as st
import funcoes as f
import pandas as pd
import geopandas as gpd
from geopy.distance import geodesic
from shapely.geometry import Point
import numpy as np
import geemap.foliumap as geemap

import psycopg2
from sqlalchemy import create_engine
import folium
import re


st.set_page_config(
    layout="wide", page_title="App de Cálculo de Promoção de Classe")

st.markdown("<h1 style='text-align: center; color: yellow;'>Promoção de Classe de Canal de Radiodifusão em FM</h1>",
            unsafe_allow_html=True)


# ---------------------------------------------------------------------
# DADOS
# ---------------------------------------------------------------------

# ----------------
# Dados Auxiliares
# ----------------

# Acesso ao banco de dados PostGIS na Amazon AWS

SGBD = "postgresql"
HOST = "rds-postgresql.c7q26ge8uwvb.us-east-1.rds.amazonaws.com"
PORT = "5432"
USER = "postgres"
PASSWORD = 'postgres'
REGION = "us-east-1"
DBNAME = "postgres"

DB_CONNECTION_URL = f"{SGBD}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"
engine = create_engine(DB_CONNECTION_URL)

# População

sql = "SELECT * FROM populacao_residente_2022"
colunas = ['Cod.', 'Municipio', 'Pop_2022']
df_populacao = pd.read_sql(sql, engine)
df_populacao = df_populacao[colunas]

# ----------------
# Dados de Entrada
# ----------------

st.sidebar.title("Dados")

st.sidebar.markdown("Latitude", unsafe_allow_html=True)
col1, col2, col3, col4 = st.sidebar.columns(4)
lat_g = col1.number_input('Graus', format="%i", key="lat_g",
                          min_value=0, max_value=90,
                          value=None,
                          placeholder=" ")
lat_m = col2.number_input('Minutos', format="%i", key="lat_m",
                          min_value=0, max_value=60,
                          value=None,
                          placeholder=" ")
lat_s = col3.number_input('Segundos', format="%i", key="lat_s",
                          min_value=0, max_value=60,
                          value=None,
                          placeholder=" ")
lat_h = col4.selectbox("S/N", options=("S", "N"), index=0, placeholder=" ")

st.sidebar.markdown("Longitude", unsafe_allow_html=True)
col1, col2, col3, col4 = st.sidebar.columns(4)
lon_g = col1.number_input('Graus', format="%i", key="lon_g",
                          min_value=0, max_value=180,
                          value=None,
                          placeholder=" ")
lon_m = col2.number_input('Minutos', format="%i", key="lon_m",
                              min_value=0, max_value=60,
                          value=None,
                          placeholder=" ")
lon_s = col3.number_input('Segundos', format="%i", key="lon_s",
                              min_value=0, max_value=60,
                          value=None,
                          placeholder=" ")
lon_h = col4.selectbox("W/E", options=("W", "E"), index=0, placeholder=" ")

frequencias_fm = np.arange(76.1, 108.1, 0.2).round(1)
canais_fm = []

CLASSE_ATUAL = st.sidebar.selectbox("Classe Atual",
                                    options=("C", "B2", "B1", "A4",
                                             "A3", "A2", "A1", "E3",
                                             "E2", "E1"),
                                    index=None,
                                    placeholder=" "
                                    )

CLASSE_PROPOSTA = st.sidebar.selectbox("Classe Proposta",
                                       options=("C", "B2", "B1", "A4",
                                                "A3", "A2", "A1", "E3",
                                                "E2", "E1"),
                                       index=None,
                                       placeholder=" "
                                       )

for i in range(len(frequencias_fm)):
    canais_fm.append(f'{i+141} ({frequencias_fm[i]} MHz)')

CANAL_P = st.sidebar.selectbox("Canal",
                               options=tuple(canais_fm),
                               index=None,
                               placeholder=" "
                               )

# Caso algum dos campos do formulário não tenha sido preenchido
if None in [CANAL_P, CLASSE_ATUAL, CLASSE_PROPOSTA,
                lat_g, lat_m, lat_s, lat_h,
            lon_g, lon_m, lon_s, lon_h]:
    st.sidebar.warning("Preencha todos os campos.")

# Caso todos os campos do formulário tenham sido preenchidos
else:
    CANAL_PROPOSTO = int(CANAL_P.split("(")[0])
    LATITUDE_PROPOSTA_GMS = f"{lat_g}° {lat_m}' {lat_s}'' {lat_h}"
    LONGITUDE_PROPOSTA_GMS = f"{lon_g}° {lon_m}' {lon_s}'' {lon_h}"

    # -----------------
    # Dados Secundários
    # -----------------

    TCP = f.tcp(CLASSE_ATUAL, CLASSE_PROPOSTA)
    LONGITUDE_PROPOSTA = f.longitude_gms_para_decimal(
        LONGITUDE_PROPOSTA_GMS)
    LATITUDE_PROPOSTA = f.latitude_gms_para_decimal(LATITUDE_PROPOSTA_GMS)
    COORDENADAS_PROPOSTAS = Point(LONGITUDE_PROPOSTA, LATITUDE_PROPOSTA)
    DMAX_CONTORNO = f.dmax_cp(CLASSE_PROPOSTA, CANAL_PROPOSTO)

    # ---------------------------------------------------------------------
    # GEODATAFRAMES
    # ---------------------------------------------------------------------
        
    # ------------------
    # Contorno Protegido
    # ------------------
        
    gdf_contorno_protegido = f.circulo_gdf(LONGITUDE_PROPOSTA, LATITUDE_PROPOSTA, DMAX_CONTORNO)
    gdf_contorno_protegido.to_postgis(name='contorno_protegido', con=engine, if_exists='replace')

    # --------------------
    # Unidades Federativas
    # --------------------

    sql_uf = "SELECT sigla_uf, geometry FROM uf_2022"
    gdf_ufs = gpd.read_postgis(sql_uf, engine, geom_col='geometry')

    # ----------
    # Municípios
    # ----------

    # Criação da tabela dos municípios que fazem interseção com o contorno protegido

    sql_municipios = "\
    DROP TABLE IF EXISTS municipios_atingidos; \
    CREATE TABLE public.municipios_atingidos as \
    SELECT a.cd_mun, a.nm_mun, a.sigla_uf, a.geometry \
    FROM public.municipios_2022 a, public.contorno_protegido b \
    WHERE ST_Intersects(a.geometry, b.geometry);\
    "

    conn = psycopg2.connect(
        database=DBNAME,
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT
    )

    cur = conn.cursor()
    cur.execute(sql_municipios)
    conn.commit()
    conn.close()
    cur.close()

    # Leitura da tabela dos municípios que fazem interseção com o contorno protegido

    gdf_municipios = gpd.read_postgis("SELECT * FROM municipios_atingidos", engine, geom_col='geometry')

    # União das geometrias dos municípios para criar uma máscara

    gdf_municipios_unidos = gdf_municipios.copy()
    gdf_municipios_unidos['Unir'] = 1
    gdf_municipios_unidos = gdf_municipios_unidos.dissolve(by='Unir')
    gdf_municipios_unidos.to_postgis(name='municipios_unidos',
                                    con=engine,
                                    if_exists='replace')

    # Criação da tabela das coordenadas dos municípios atingidos

    sql_cidades = "\
    DROP TABLE IF EXISTS cidades_atingidas; \
    CREATE TABLE public.cidades_atingidas as \
    SELECT a.cid_mun_cd, a.cid_mun, a.cid_uf, a.lat_cid, a.long_cid, a.geometry \
    FROM public.cidades_2016 a, public.municipios_unidos b \
    WHERE ST_Intersects(a.geometry,b.geometry);\
    "

    conn = psycopg2.connect(
        database=DBNAME,
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT
    )

    cur = conn.cursor()
    cur.execute(sql_cidades)
    conn.commit()
    conn.close()
    cur.close()

    # Leitura da tabela das coordenadas dos municípios atingidos

    gdf_coord_municipios = gpd.read_postgis("SELECT * FROM cidades_atingidas",
                                            engine,
                                            geom_col='geometry')

    def dist_estacao_locais(lat_cid, long_cid):
        return round(geodesic((LATITUDE_PROPOSTA, LONGITUDE_PROPOSTA),
                                    (lat_cid, long_cid)).km, 1)

    gdf_coord_municipios['Dist_Est'] = np.vectorize(dist_estacao_locais)(gdf_coord_municipios['lat_cid'],
                                                                                gdf_coord_municipios['long_cid'])


    # -------------------
    # Setores Censitários
    # -------------------

    # Criação da tabela dos setores censitários dos municípios que fazem interseção com o contorno protegido

    sql_setores_municipios = "\
    DROP TABLE IF EXISTS setores_municipios_atingidos; \
    CREATE TABLE public.setores_municipios_atingidos as \
    SELECT a.cd_setor, a.cd_sit, a.nm_sit, a.cd_mun, a.nm_mun, a.nm_dist, a.sigla_uf, a.geometry \
    FROM public.setores_censitarios_2021 a, public.municipios_unidos b \
    WHERE ST_Intersects(a.geometry, b.geometry);\
    "

    conn = psycopg2.connect(
        database=DBNAME,
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT
    )

    cur = conn.cursor()
    cur.execute(sql_setores_municipios)
    conn.commit()
    conn.close()
    cur.close()

    # Leitura da tabela dos setores censitários dos municípios que fazem interseção com o contorno protegido

    gdf_setores_censitarios = gpd.read_postgis("SELECT * FROM setores_municipios_atingidos",
                                            engine,
                                            geom_col='geometry')

    gdf_setores_censitarios['sit'] = np.vectorize(f.situacao_setor)(gdf_setores_censitarios['cd_sit'],
                                                                gdf_setores_censitarios['nm_mun'],
                                                                    gdf_setores_censitarios['nm_dist'])

    filtro_setores_urbanos = gdf_setores_censitarios.sit == 'área urbana de cidade'
    gdf_setores_censitarios_cidades = gdf_setores_censitarios[filtro_setores_urbanos]

    # Área urbana das cidades dos municípios que fazem interseção com o contorno protegido
    gdf_setores_censitarios_cidades = gdf_setores_censitarios_cidades.reset_index(
    drop=True)

    # Área urbana das cidades que intersepta o contorno protegido
    gdf_intersecao_setores_urbanos_cp = gpd.overlay(gdf_setores_censitarios_cidades, gdf_contorno_protegido, how='intersection')
    gdf_intersecao_setores_urbanos_cp = gdf_intersecao_setores_urbanos_cp.reset_index(drop=True)

    # -------------------
    # Municípios Cobertos
    # -------------------

    # Municípios com área urbana interseptada pelo contorno protegido

    codigos_municipios_cobertos = list(gdf_intersecao_setores_urbanos_cp.cd_mun.unique())
    gdf_municipios_com_area_urbana_atingida_pelo_cp = gdf_municipios[gdf_municipios.cd_mun.isin(codigos_municipios_cobertos)]
    gdf_municipios_com_area_urbana_atingida_pelo_cp = gdf_municipios_com_area_urbana_atingida_pelo_cp.reset_index(drop=True)

    def municipio_uf(nm_mun, SIGLA_UF):
        return f'{nm_mun} - {SIGLA_UF}'

    gdf_municipios_com_area_urbana_atingida_pelo_cp['Município - UF'] = np.vectorize(municipio_uf)(gdf_municipios_com_area_urbana_atingida_pelo_cp['nm_mun'], 
                                                                                                gdf_municipios_com_area_urbana_atingida_pelo_cp['sigla_uf'])

    filtro = gdf_coord_municipios.cid_mun_cd.isin(list(map(int, codigos_municipios_cobertos)))
    gdf_coord_municipios_atingidos_area_urbana = gdf_coord_municipios[filtro]
    gdf_coord_municipios_atingidos_area_urbana = gdf_coord_municipios_atingidos_area_urbana.reset_index(drop=True)

    def municipio_com_codigo(codigo):
        municipio = gdf_municipios[gdf_municipios.cd_mun == codigo]['nm_mun'].values[0]
        uf = gdf_municipios[gdf_municipios.cd_mun == codigo]['sigla_uf'].values[0]
        return municipio + '/' + uf

    municipios_cobertos = []
    for codigo in codigos_municipios_cobertos:
        municipios_cobertos.append(municipio_com_codigo(codigo))

    # --------------
    # Local Proposto
    # --------------

    gdf_local_proposto = gpd.GeoDataFrame(geometry=[COORDENADAS_PROPOSTAS], crs='EPSG:4674')
    gdf_municipio_local_proposto = gpd.sjoin(gdf_municipios, gdf_local_proposto, how='inner', predicate='contains')
    municipio_local_proposto_cod = gdf_municipio_local_proposto['cd_mun'].iloc[0]
    municipio_local_proposto = gdf_municipio_local_proposto['nm_mun'].iloc[0]
    municipio_local_proposto_uf = gdf_municipio_local_proposto['sigla_uf'].iloc[0]

    # ---------------------------------------------------------------------
    # MAPA
    # ---------------------------------------------------------------------

    mapa = geemap.Map(location=[LATITUDE_PROPOSTA, LONGITUDE_PROPOSTA],
                    zoom_start=9.5,
                    tiles="cartodb positron",
                    height="700",
                    width="1200")

    # Título
    # ------

    titulo = "Municípios com área urbana atingida pelo contorno protegido"

    titulo_html = """<h1 align = "center", style = "font-family: verdana; 
    font-size: 16px; font-weight: bold; background-color: black;
    color: white; padding: 10px; text-transform: uppercase;">{}</h1>""".format(titulo)

    mapa.get_root().html.add_child(folium.Element(titulo_html))

    # UFs
    # -----

    folium.GeoJson(gdf_ufs,
                name="UFs",
                style_function=lambda x: {"fillColor": None,
                                            "color": "black",
                                            "opacity": 0.8,
                                            "fillOpacity": 0.03,
                                            "weight": 1.5
                                            }
                ).add_to(mapa)

    # Estação de FM
    # -------------

    estacao = folium.FeatureGroup("Estação de FM").add_to(mapa)
    folium.Marker([LATITUDE_PROPOSTA, LONGITUDE_PROPOSTA],
                icon=folium.Icon(icon="glyphicon glyphicon-home",
                                color="red",
                                icon_color="white",
                                prefix="glyphicon"),
                popup="Estação de FM",
                tooltip="Estação").add_to(estacao)

    # Municípios intersectados pelo contorno protegido da classe
    # ----------------------------------------------------------

    popup = folium.GeoJsonPopup(
        fields=["nm_mun", "sigla_uf"],
        aliases=["Município", "UF",],
        localize=True,
        labels=True,
        style="background-color: yellow;",
    )

    tooltip = folium.GeoJsonTooltip(
        fields=["nm_mun", "sigla_uf"],
        aliases=["Município", "UF"],
        localize=True,
        sticky=False,
        labels=True,
        style="""
            background-color: #F0EFEF;
            border: 2px solid black;
            border-radius: 3px;
            box-shadow: 3px;
        """,
        max_width=800,
    )

    folium.GeoJson(gdf_municipios,
                name="Municípios intersectados pelo contorno protegido",
                style_function=lambda x: {"fillColor": None,
                                            "color": "blue",
                                            "opacity": 0.8,
                                            "fillOpacity": 0.03,
                                            "weight": 1.5
                                            },
                tooltip=tooltip,
                popup=popup,
                ).add_to(mapa)

    # Municípios com área urbana intersectada pelo contorno protegido da classe
    # -------------------------------------------------------------------------

    gdf_municipios_com_area_urbana_atingida_pelo_cp.explore(
        m=mapa,
        column="Município - UF",
        legend_kwds={"caption": "Município - UF"},
        cmap='Set1',
        style_kwds={"color": "blue",
                    "weight": 2,
                    "fillOpacity": 0.5
                    },
        tooltip="Município - UF",
        tooltip_kwds=dict(labels=False),
        popup=["nm_mun", "sigla_uf"],
        name="Municípios com área urbana intersectada pelo contorno protegido"
    )

    # Área urbana dos municípios intersectados pelo contorno protegido da classe
    # -------------------------------------------------------------------------

    gdf_setores_censitarios_cidades.explore(
        m=mapa,
        style_kwds={"color": "orange",
                    "fillColor": "None",
                    "weight": 0.8
                    },
        tooltip=["cd_setor", "nm_sit", "nm_mun", "sigla_uf", "sit"],
        popup=["cd_setor", "nm_sit", "nm_mun", "sigla_uf", "sit"],
        name="Área urbana dos municípios intersectados pelo contorno protegido"
    )

    # Área urbana intersectada pelo contorno protegido da classe
    # -------------------------------------------------------------------------

    gdf_intersecao_setores_urbanos_cp.explore(
        m=mapa,
        style_kwds={"color": "red",
                    "fillColor": "None",
                    "weight": 0.8},
        tooltip=["cd_setor", "nm_sit", "nm_mun", "sigla_uf", "sit"],
        popup=["cd_setor", "nm_sit", "nm_mun", "sigla_uf", "sit"],
        name="Área urbana intersectada pelo contorno protegido"
    )

    # Contorno protegido da classe
    # ----------------------------

    cp_classe = folium.FeatureGroup("Contorno protegido da classe").add_to(mapa)
    folium.Circle(radius=float(DMAX_CONTORNO)*1000,
                location=[LATITUDE_PROPOSTA, LONGITUDE_PROPOSTA],
                popup="Contorno protegido da classe",
                color="green",
                weight=3,
                fill=False).add_to(cp_classe)

    # Camadas extras
    # -------------------------------------------------------------------------

    folium.TileLayer(tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
                    attr="Tiles &copy; Esri &mdash; Source: Esri, DeLorme, NAVTEQ, USGS, Intermap, iPC, NRCAN, Esri Japan, METI, Esri China (Hong Kong), Esri (Thailand), TomTom, 2012",
                    name="Esri.WorldStreetMap").add_to(mapa)

    folium.TileLayer(tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                    attr="Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community",
                    name="Esri.WorldImagery").add_to(mapa)

    folium.TileLayer(tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
                    attr="https://opentopomap.org",
                    name="OpenTopoMap").add_to(mapa)

    folium.TileLayer(tiles="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                    attr="https://www.openstreetmap.org/copyright",
                    name="OpenStreetMap.Mapnik").add_to(mapa)


    # Controle de camadas
    # -------------------------------------------------------------------------

    folium.LayerControl().add_to(mapa)


    # Coordenadas em qualquer ponto
    # -------------------------------------------------------------------------

    mapa.add_child(folium.LatLngPopup())

    # Coordenadas dos municípios
    # -------------------------------------------------------------------------

    locais = gdf_coord_municipios[['lat_cid', 'long_cid']]
    coord_municipios = locais.values.tolist()

    for ponto in range(0, len(coord_municipios)):
        folium.Marker(coord_municipios[ponto],
                    popup=gdf_coord_municipios['cid_mun'][ponto] + "/" + gdf_coord_municipios['cid_uf'][ponto] + ": " + str(
                        gdf_coord_municipios['Dist_Est'][ponto]) + " km",
                    tooltip=gdf_coord_municipios['cid_mun'][ponto] + "/" + gdf_coord_municipios['cid_uf'][ponto] + ": " + str(
                        gdf_coord_municipios['Dist_Est'][ponto]) + " km"
                    ).add_to(mapa)

    # Coordenadas dos municípios com área urbana intersectada pelo contorno protegido
    # -------------------------------------------------------------------------

    locais = gdf_coord_municipios_atingidos_area_urbana[['lat_cid', 'long_cid']]
    coord_municipios_cp = locais.values.tolist()

    for ponto in range(0, len(coord_municipios_cp)):
        folium.Marker(coord_municipios_cp[ponto],
                    icon=folium.Icon(icon="glyphicon glyphicon-map-marker",
                                    color="green",
                                    icon_color="white",
                                    prefix="glyphicon"),
                    popup=gdf_coord_municipios_atingidos_area_urbana['cid_mun'][ponto] + "/" + gdf_coord_municipios_atingidos_area_urbana['cid_uf'][ponto] + ": " + str(
                        gdf_coord_municipios_atingidos_area_urbana['Dist_Est'][ponto]) + " km",
                    tooltip=gdf_coord_municipios_atingidos_area_urbana['cid_mun'][ponto] + "/" + gdf_coord_municipios_atingidos_area_urbana['cid_uf'][ponto] + ": " + str(
                        gdf_coord_municipios_atingidos_area_urbana['Dist_Est'][ponto]) + " km"
                    ).add_to(mapa)
        
    mapa.to_streamlit(height=700)

    # ---------------------------------------------------------------------
    # CÁLCULO DO VALOR DA PROMOÇÃO DE CLASSE
    # (art. 34 da Portaria GM/MCom nº 9.018/2023)
    # ---------------------------------------------------------------------

    # Determinação do grupo de enquadramento na situação proposta (A para B ou B para C)

    grupo_atual = f.grupo_enquadramento(CLASSE_ATUAL)
    grupo_proposto = f.grupo_enquadramento(CLASSE_PROPOSTA)

    # Determinação do município de referência
    # Anexo XXVIII da Portaria GM/MCom nº 9018/2023

    cod_municipio_referencia = f.valor_referencia(municipio_local_proposto_uf,
                                                grupo_proposto, municipio_local_proposto_cod)[0]
    municipio_referencia = f.valor_referencia(municipio_local_proposto_uf,
                                            grupo_proposto, municipio_local_proposto_cod)[1]

    # População dos municípios cobertos

    df_populacao_municipios_cobertos = df_populacao[df_populacao["Cod."].isin(
        list(map(int, codigos_municipios_cobertos)))]
    df_populacao_municipios_cobertos = df_populacao_municipios_cobertos.reset_index(
        drop=True)

    # População total dos municípios cobertos

    Ptot = df_populacao_municipios_cobertos.Pop_2022.sum()

    # População do município de referência

    filtro_mun_ref = df_populacao["Cod."] == int(cod_municipio_referencia)
    Tcp = int(TCP)

    if municipio_local_proposto_uf == 'SP':
        if municipio_local_proposto_cod in ['3503901', '3505708', '3506607', '3509007', '3509205', '3510609',
                                            '3513009', '3513801', '3515004', '3515103', '3515707', '3516309',
                                            '3516408', '3518305', '3518800', '3522208', '3522505', '3523107',
                                            '3525003', '3526209', '3528502', '3529401', '3530607', '3534401',
                                            '3539103', '3539806', '3543303', '3544103', '3545001', '3546801',
                                            '3547304', '3547809', '3548708', '3548807', '3549953', '3550308',
                                            '3552502', '3552809', '3556453']:
            Pref = int(20743587)
        else: 
            Pref = int(1139047)
    else:
        Pref = int(df_populacao[filtro_mun_ref]['Pop_2022'].values[0])

    if grupo_atual == 'A':
        if grupo_proposto == 'A':
            Vab, Vbc = 0, 0
        elif grupo_proposto == 'B':
            Vab = f.valor_referencia(municipio_local_proposto_uf,
                                    grupo_proposto, municipio_local_proposto_cod)[2]
            Vbc = 0
        elif grupo_proposto == 'C':
            Vab = f.valor_referencia(municipio_local_proposto_uf, 'B', municipio_local_proposto_cod)[2]
            Vbc = f.valor_referencia(municipio_local_proposto_uf,
                                    grupo_proposto, municipio_local_proposto_cod)[2]
    elif grupo_atual == 'B':
        if grupo_proposto == 'A':
            Vab, Vbc = 0, 0
        elif grupo_proposto == 'B':
            if Tcp == 0:
                Vab, Vbc = 0, 0
            else:
                Vab = f.valor_referencia(municipio_local_proposto_uf, 'B', municipio_local_proposto_cod)[2]
                Vbc = 0
        elif grupo_proposto == 'C':
            Vab = 0
            Vbc = f.valor_referencia(municipio_local_proposto_uf,
                                    grupo_proposto, municipio_local_proposto_cod)[2]
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
                Vbc = f.valor_referencia(municipio_local_proposto_uf, 'C', municipio_local_proposto_cod)[2]

    # Cálculo do Vpc

    if Tcp != 'não se aplica':
        Vpc = (Ptot/Pref) * (Vab + Vbc) * (1+Tcp/10)
        Vpc = round(Vpc, 2)
        Tcp = str(Tcp)
    else:
        Vpc = 'não se aplica'

    # ------------------------
    # IMPRESSÃO DOS RESULTADOS
    # ------------------------

    df_populacao_municipios_cobertos.index += 1
    df_populacao_municipios_cobertos = df_populacao_municipios_cobertos[[
        'Municipio', 'Pop_2022']]
    df_populacao_municipios_cobertos = df_populacao_municipios_cobertos.rename(
        columns={"Municipio": "Município Coberto", "Pop_2022": "População"})

    df_populacao_municipios_cobertos = df_populacao_municipios_cobertos.style.format(
        thousands='.')

    def sep(s, thou=",", dec="."):
        integer, decimal = s.split(".")
        integer = re.sub(r"\B(?=(?:\d{3})+$)", thou, integer)
        return integer + dec + decimal

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(label="Município e UF da estação",
                value=f'{municipio_local_proposto}/{municipio_local_proposto_uf}')

    dmax_cp = sep("%.1f" % DMAX_CONTORNO, thou=".", dec=",")
    col2.metric(label="Distância máxima ao contorno protegido",
                value=f'{dmax_cp} km')

    col3.metric(label="Município de referência",
                value=f'{municipio_referencia}/{municipio_local_proposto_uf}')

    col4.metric(label="População do município de referência",
                value=f'{Pref:,}'.replace(',', '.'))

    col1, col2, col3, col4 = st.columns(4)

    col1.table(df_populacao_municipios_cobertos)

    col2.metric(label="População total dos municípios cobertos",
                value=f'{Ptot:,}'.replace(',', '.'))

    vpc = sep("%.2f" % Vpc, thou=".", dec=",")
    col3.metric(label="Valor da promoção de classe", value=f'R$ {vpc}')
