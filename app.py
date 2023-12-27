import dados as d
import streamlit as st
from mapas import mapa_dinamico
from mapas import mapa_brasil_ufs
import funcoes as f
import pandas as pd
import geopandas as gpd
from geopy.distance import geodesic
from shapely.geometry import Point
import numpy as np  
import re


def main():

    ## ----------------------

    st.set_page_config(layout="wide", page_title="App de Cálculo de Promoção de Classe")

    ## ------------------------------------------
    ## ENTRADA DE DADOS
    ## ------------------------------------------

    st.sidebar.title("Dados")

    frequencias_fm = np.arange(76.1, 108.1, 0.2).round(1)
    canais_fm = []

    for i in range(len(frequencias_fm)):
        canais_fm.append(f'{i+141} ({frequencias_fm[i]} MHz)')

    CANAL_P = st.sidebar.selectbox("Canal", 
                                options = tuple(canais_fm), 
                                index=None, 
                                placeholder=" "
                                )

    CLASSE_ATUAL = st.sidebar.selectbox("Classe Atual", 
                                        options = ("C", "B2", "B1", "A4", 
                                                "A3", "A2", "A1", "E3", 
                                                "E2", "E1"),
                                        index=None, 
                                        placeholder=" "
                                        )

    CLASSE_PROPOSTA = st.sidebar.selectbox("Classe Proposta", 
                                        options = ("C", "B2", "B1", "A4", 
                                                    "A3", "A2", "A1", "E3", 
                                                    "E2", "E1"), 
                                        index=None, 
                                        placeholder=" "
                                        )

    st.sidebar.markdown("Latitude", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.sidebar.columns(4)
    lat_g = col1.number_input('Graus', format="%i", key="lat_g",
                                min_value=0, max_value=90,
                                value = None,
                                placeholder=" ")
    lat_m = col2.number_input('Minutos', format="%i", key="lat_m",
                                min_value=0, max_value=60,
                                value = None,
                                placeholder=" ")
    lat_s = col3.number_input('Segundos', format="%i", key="lat_s",
                                min_value=0, max_value=60,
                                value = None,
                                placeholder=" ")
    lat_h = col4.selectbox("S/N", options = ("S", "N"), index=0, placeholder=" ")

    st.sidebar.markdown("Longitude", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.sidebar.columns(4)
    lon_g = col1.number_input('Graus', format="%i", key="lon_g",
                                min_value=0, max_value=180,
                                value = None,
                                placeholder=" ")
    lon_m = col2.number_input('Minutos', format="%i", key="lon_m",
                                min_value=0, max_value=60,
                                value = None,
                                placeholder=" ")
    lon_s = col3.number_input('Segundos', format="%i", key="lon_s",
                                min_value=0, max_value=60,
                                value = None,
                                placeholder=" ")
    lon_h = col4.selectbox("W/E", options = ("W", "E"), index=0, placeholder=" ")

    ## ------------------------------------------

    st.title("Promoção de Classe de Canal de Radiodifusão em FM")

    if None in [CANAL_P, CLASSE_ATUAL, CLASSE_PROPOSTA,
                lat_g, lat_m, lat_s, lat_h,
                lon_g, lon_m, lon_s, lon_h]:
        st.warning("Preencha todos os campos ao lado.")
        m = mapa_brasil_ufs()
        m.to_streamlit(height=700)

    # Caso todos os campos do formulário tenham sido preenchidos
    else:

        ## ------------------------------------------
        ## DADOS INICIAIS
        ## ------------------------------------------

        CANAL_PROPOSTO = int(CANAL_P.split("(")[0])
        LATITUDE_PROPOSTA_GMS = f"{lat_g}° {lat_m}' {lat_s}'' {lat_h}"    
        LONGITUDE_PROPOSTA_GMS = f"{lon_g}° {lon_m}' {lon_s}'' {lon_h}"  
        Tcp = f.tcp(CLASSE_ATUAL, CLASSE_PROPOSTA)
        mudanca = f.tipo_de_mudanca(CLASSE_ATUAL, CLASSE_PROPOSTA)
        longitude_proposta = f.longitude_gms_para_decimal(LONGITUDE_PROPOSTA_GMS)
        latitude_proposta = f.latitude_gms_para_decimal(LATITUDE_PROPOSTA_GMS)
        coordenadas_propostas = Point(longitude_proposta, latitude_proposta)
        gdf_local_proposto = gpd.GeoDataFrame(geometry=[coordenadas_propostas], 
                                            crs='EPSG:4674')
        dmax_contorno = f.dmax_cp(CLASSE_PROPOSTA, CANAL_PROPOSTO)
        gdf_contorno_protegido = f.circulo_gdf(longitude_proposta, latitude_proposta, 
                                            dmax_contorno)      

        ## --------------------------------------------
        ## MUNICÍPIOS ATINGIDOS PELO CONTORNO PROTEGIDO
        ## --------------------------------------------

        gdf_municipios = gpd.read_file(d.MUNICIPIOS, 
                                    mask=gdf_contorno_protegido['geometry'][0])

        gdf_municipios_unidos = gdf_municipios.copy()
        gdf_municipios_unidos['Unir'] = 1
        gdf_municipios_unidos = gdf_municipios_unidos.dissolve(by='Unir')
        municipios_unidos = gdf_municipios_unidos['geometry'][1]

        gdf_coord_municipios = gpd.read_file(d.MUNICIPIOS_COORD,
                                            mask=municipios_unidos)
        gdf_coord_municipios['geometry'] = gdf_coord_municipios.representative_point()
        gdf_coord_municipios['LON'] = gdf_coord_municipios['geometry'].x
        gdf_coord_municipios['LAT'] = gdf_coord_municipios['geometry'].y

        def dist_estacao_locais(lati, long):
            return round(geodesic((latitude_proposta, longitude_proposta), 
                                (lati, long)).km, 1)

        gdf_coord_municipios['Dist_Est'] = np.vectorize(dist_estacao_locais)(gdf_coord_municipios['LAT'], 
                                                                            gdf_coord_municipios['LON'])

        ## ---------------------------------
        ##  MUNICÍPIO E UF DO LOCAL PROPOSTO
        ## ---------------------------------

        gdf_municipio_local_proposto = gpd.sjoin(gdf_municipios, gdf_local_proposto, 
                                                how='inner', predicate='contains')
        municipio_local_proposto_cod = gdf_municipio_local_proposto['CD_MUN'].iloc[0] 
        municipio_local_proposto = gdf_municipio_local_proposto['NM_MUN'].iloc[0]
        municipio_local_proposto_uf = gdf_municipio_local_proposto['SIGLA_UF'].iloc[0]

        ## -----------------------------------------------------
        ## SETORES CENSITÁRIOS ATINGIDOS PELO CONTORNO PROTEGIDO
        ## -----------------------------------------------------

        gdf_setores_censitarios = gpd.read_file(d.SETORES_CENSITARIOS,
                                                mask=municipios_unidos)

        gdf_setores_censitarios['SIT'] = np.vectorize(f.situacao_setor) (gdf_setores_censitarios['CD_SIT'],                                                                 gdf_setores_censitarios['NM_MUN'], 
        gdf_setores_censitarios['NM_DIST'])
        filtro_setores_urbanos = gdf_setores_censitarios.SIT == 'área urbana de cidade'
        gdf_setores_censitarios_cidades = gdf_setores_censitarios[filtro_setores_urbanos]
        gdf_setores_censitarios_cidades = gdf_setores_censitarios_cidades.reset_index(drop=True)

        gdf_intersecao_setores_urbanos_cp = gpd.overlay(gdf_setores_censitarios_cidades, gdf_contorno_protegido, how='intersection')
        gdf_intersecao_setores_urbanos_cp = gdf_intersecao_setores_urbanos_cp.reset_index(drop=True)

        ## ---------------------------------------------------------------
        ## MUNICÍPIOS COM ÁREA URBANA INTERSECTADA PELO CONTORNO PROTEGIDO
        ## ---------------------------------------------------------------

        codigos_municipios_cobertos = list(gdf_intersecao_setores_urbanos_cp.CD_MUN.unique())
        gdf_municipios_com_area_urbana_atingida_pelo_cp = gdf_municipios[gdf_municipios.CD_MUN.isin(codigos_municipios_cobertos)]
        gdf_municipios_com_area_urbana_atingida_pelo_cp = gdf_municipios_com_area_urbana_atingida_pelo_cp.reset_index(drop=True)

        def municipio_uf(NM_MUN, SIGLA_UF):
            return f'{NM_MUN} - {SIGLA_UF}'

        gdf_municipios_com_area_urbana_atingida_pelo_cp['MUNICIPIO-UF'] = np.vectorize(municipio_uf)(
            gdf_municipios_com_area_urbana_atingida_pelo_cp['NM_MUN'], gdf_municipios_com_area_urbana_atingida_pelo_cp['SIGLA_UF'])

        filtro = gdf_coord_municipios.Geocodigo.isin(codigos_municipios_cobertos)
        gdf_coord_municipios_atingidos_area_urbana = gdf_coord_municipios[filtro]
        gdf_coord_municipios_atingidos_area_urbana = gdf_coord_municipios_atingidos_area_urbana.reset_index(drop=True)

        def municipio_com_codigo(codigo):
            municipio = gdf_municipios[gdf_municipios.CD_MUN == codigo]['NM_MUN'].values[0]
            uf = gdf_municipios[gdf_municipios.CD_MUN == codigo]['SIGLA_UF'].values[0]
            return municipio + '/' + uf

        municipios_cobertos = []
        for codigo in codigos_municipios_cobertos:
            municipios_cobertos.append(municipio_com_codigo(codigo))

        ## ----
        ## MAPA
        ## ----
            
        mapa = mapa_dinamico(latitude_proposta, 
                            longitude_proposta,
                            gdf_municipios,
                            gdf_municipios_com_area_urbana_atingida_pelo_cp,
                            gdf_setores_censitarios_cidades,
                            gdf_intersecao_setores_urbanos_cp,
                            dmax_contorno)

        mapa.to_streamlit(height=700)

        ## -----------------------------
        ## CÁLCULO DA PROMOÇÃO DE CLASSE
        ## -----------------------------

        resultados = f.calcular_vpc(d.POPULACAO, 
                                    d.CLASSE_ATUAL,
                                    d.CLASSE_PROPOSTA,
                                    municipio_local_proposto_uf,
                                    codigos_municipios_cobertos,
                                    Tcp)

        grupo_proposto = resultados['grupo proposto']
        municipio_referencia = resultados['município de referência']
        Pref = resultados['Pref']
        Ptot = resultados['Ptot']
        Vab = resultados['Vab']
        Vbc = resultados['Vbc']
        Vpc = resultados['Vpc']
        df_populacao_municipios_cobertos = resultados['df_populacao']
        
        ## ------------------------
        ## IMPRESSÃO DOS RESULTADOS
        ## ------------------------

        # print(f"Classe proposta: {d.CLASSE_PROPOSTA}\n")
        # print(f"Distância máxima ao contorno protegido: dmax = {dmax_contorno} km\n")
        # print(f"Município e UF da estação: {municipio_local_proposto}/{municipio_local_proposto_uf}\n")
        # print(f"Grupo de enquadramento proposto: {grupo_proposto}\n")

        # print(f'{len(municipios_cobertos)} municípios com área urbana atingida pelo CP da classe: \n')

        municipios_cob = ""

        for i in range(len(municipios_cobertos)):
            municipios_cob = municipios_cob + municipios_cobertos[i] + ", " 
            
        # print(f"{municipios_cob[:-2]}\n")

        # for municipio in municipios_cobertos:
        #     print(municipio)
            
        # print(f'\nPopulação total dos municípios cobertos: Ptot = {Ptot:,}\n'.replace(',','.'))
        # print(f"Município de referência: {municipio_referencia}/{municipio_local_proposto_uf}\n")
        # print(f"Valores de referência: Vab = R$ {Vab} e Vbc = R$ {Vbc}\n")
        # print(f'População do município de referência: Pref = {Pref:,}\n'.replace(',','.'))
        # print(f'Valor da promoção de classe: Vpc = R$ {Vpc}\n')

        df_populacao_municipios_cobertos.index += 1 
        df_populacao_municipios_cobertos = df_populacao_municipios_cobertos[['Municipio','Populacao']]
        df_populacao_municipios_cobertos = df_populacao_municipios_cobertos.rename(columns={"Municipio": "Município Coberto", "Populacao": "População"})
        # tabela_municipios_cobertos = df_populacao_municipios_cobertos.to_latex()
        # print(tabela_municipios_cobertos)
        # print(gdf_coord_municipios_atingidos_area_urbana)
        df_populacao_municipios_cobertos = df_populacao_municipios_cobertos.style.format(thousands='.') 
        # print(df_populacao_municipios_cobertos)

        def sep(s, thou=",", dec="."):
            integer, decimal = s.split(".")
            integer = re.sub(r"\B(?=(?:\d{3})+$)", thou, integer)
            return integer + dec + decimal

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(label="Município e UF da estação", value=f'{municipio_local_proposto}/{municipio_local_proposto_uf}')

        dmax_cp = sep("%.1f" % dmax_contorno, thou=".", dec=",")
        col2.metric(label="Distância máxima ao contorno protegido", value=f'{dmax_cp} km')

        col3.metric(label="Município de referência", value=f'{municipio_referencia}/{municipio_local_proposto_uf}')

        col4.metric(label="População do município de referência", value=f'{Pref:,}'.replace(',','.'))

        col1, col2, col3, col4 = st.columns(4)

        col1.table(df_populacao_municipios_cobertos)

        col2.metric(label="População total dos municípios cobertos", value=f'{Ptot:,}'.replace(',','.'))

        vpc = sep("%.2f" % Vpc, thou=".", dec=",")
        col3.metric(label="Valor da promoção de classe", value=f'R$ {vpc}')

        # ------------------------------------


if __name__ == "__main__":
    main()