import folium
import geemap.foliumap as geemap
from folium.plugins import FloatImage
import branca
import dados as d
import base64
import geopandas as gpd
import pandas as pd

## --------------------------------------------
## POLÍGONOS DAS UFs
## --------------------------------------------

# Códigos das Unidades da Federação (UFs)
url_ufs = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
df_cod_ufs = pd.read_json(url_ufs, orient="columns")
df_cod_ufs = df_cod_ufs[['id', 'sigla', 'nome']]
df_cod_ufs = df_cod_ufs.rename(columns={'id': 'cod_uf', 
                                        'sigla': 'sigla_uf',
                                        'nome': 'nome_uf'
                                        })
cod_ufs = list(df_cod_ufs['cod_uf'])

gdfs = []
for cod in cod_ufs: 
    url = f"https://servicodados.ibge.gov.br/api/v3/malhas/estados/{cod}?formato=application/vnd.geo+json"
    gdf = gpd.read_file(url)
    gdfs.append(gdf)    
gdf_ufs = pd.concat(gdfs)

## --------------------------------------------

def mapa_brasil_ufs():

    mapa = geemap.Map(location = [-15.7801, -47.9292], 
                      zoom_start = 4,
                      tiles = "cartodb positron")

    # popup = folium.GeoJsonPopup(
    #     fields=["NM_MUN", "SIGLA_UF", "AREA_KM2"],
    #     aliases=["Município", "UF", "Área (km2)"],
    #     localize=True,
    #     labels=True,
    #     style="background-color: yellow;",
    # )

    # tooltip = folium.GeoJsonTooltip(
    #     fields=["NM_MUN", "SIGLA_UF"],
    #     aliases=["Município", "UF"],
    #     localize=True,
    #     sticky=False,
    #     labels=True,
    #     style="""
    #         background-color: #F0EFEF;
    #         border: 2px solid black;
    #         border-radius: 3px;
    #         box-shadow: 3px;
    #     """,
    #     max_width=800,
    # )

    folium.GeoJson(gdf_ufs, 
                   name="UFs",
                   style_function=lambda x: {"fillColor": None,
                                             "color": "blue",
                                             "opacity": 0.7,
                                             "fillOpacity": 0.03,
                                             "weight": 1.5
                                             },
                   # tooltip=tooltip,
                   # popup=popup,
                   ).add_to(mapa)

    return mapa

## --------------------------------------------

def mapa_dinamico(latitude_proposta, 
                  longitude_proposta,
                  gdf_municipios,
                  gdf_municipios_com_area_urbana_atingida_pelo_cp,
                  gdf_setores_censitarios_cidades,
                  gdf_intersecao_setores_urbanos_cp,
                  dmax_contorno
                  ):

    mapa = geemap.Map(location = [latitude_proposta, longitude_proposta], 
                      zoom_start = 9.5,
                      tiles = "cartodb positron")

    # Título 
    # ------

    titulo = "Municípios com área urbana atingida pelo contorno protegido"

    titulo_html = """<h1 align = "center", style = "font-family: verdana; 
    font-size: 16px; font-weight: bold; background-color: black;
    color: white; padding: 10px; text-transform: uppercase;">{}</h1>""".format(titulo)

    mapa.get_root().html.add_child(folium.Element(titulo_html))

    # Colocação de uma lupa no mapa
    # Geocoder(collapsed = True,
    #         position = "topleft",
    #         add_marker = True).add_to(mapa)

    mapa.add_basemap("OpenTopoMap")

    folium.GeoJson(gdf_ufs, 
                name = "UFs",
                style_function=lambda x: {"fillColor": None,
                                            "color": "blue",
                                            "opacity": 0.8,
                                            "fillOpacity": 0.03,
                                            "weight": 1.5
                                            },
                # tooltip=tooltip,
                # popup=popup,
                ).add_to(mapa)

    # Estação de FM 
    # -------------

    estacao = folium.FeatureGroup("Estação de FM").add_to(mapa)    
    folium.Marker([latitude_proposta, longitude_proposta], 
                icon = folium.Icon(icon = "glyphicon glyphicon-home",
                                    color = "red", 
                                    icon_color = "white",
                                    prefix = "glyphicon"),
                popup = "Estação de FM", 
                tooltip = "Estação").add_to(estacao)    

    # Municípios intersectados pelo contorno protegido da classe
    # ----------------------------------------------------------

    popup = folium.GeoJsonPopup(
        fields=["NM_MUN", "SIGLA_UF", "AREA_KM2"],
        aliases=["Município", "UF", "Área (km2)"],
        localize=True,
        labels=True,
        style="background-color: yellow;",
    )

    tooltip = folium.GeoJsonTooltip(
        fields=["NM_MUN", "SIGLA_UF"],
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
                name = "Municípios intersectados pelo contorno protegido",
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
        m = mapa,
        column = "MUNICIPIO-UF",
        legend_kwds = {"caption": "Município - UF"}, 
        cmap = 'Set1',
        style_kwds = {"color": "blue", 
                      "weight": 2, 
                      "fillOpacity": 0.5
                      },
        tooltip = "MUNICIPIO-UF",
        tooltip_kwds = dict(labels=False),
        popup = ["NM_MUN", "SIGLA_UF", "AREA_KM2"],
        name = "Municípios com área urbana intersectada pelo contorno protegido"
    )
        
    # Área urbana dos municípios intersectados pelo contorno protegido da classe
    # -------------------------------------------------------------------------

    gdf_setores_censitarios_cidades.explore(
            m = mapa,
            style_kwds = {"color": "orange", 
                          "fillColor": "None", 
                          "weight": 0.8
                          },
            tooltip = ["CD_SETOR", "NM_SIT", "NM_MUN", "SIGLA_UF", "SIT"],
            popup = ["CD_SETOR", "NM_SIT", "NM_MUN", "SIGLA_UF", "SIT"],
            name = "Área urbana dos municípios intersectados pelo contorno protegido"
    )

    # Área urbana intersectada pelo contorno protegido da classe
    # -------------------------------------------------------------------------

    gdf_intersecao_setores_urbanos_cp.explore(
            m = mapa,
            style_kwds = {"color": "red", 
                        "fillColor": "None", 
                        "weight": 0.8},
            tooltip = ["CD_SETOR", "NM_SIT", "NM_MUN", "SIGLA_UF", "SIT"],
            popup = ["CD_SETOR", "NM_SIT", "NM_MUN", "SIGLA_UF", "SIT"],
            name = "Área urbana intersectada pelo contorno protegido"
    )

    # Contorno protegido da classe
    # ----------------------------

    cp_classe = folium.FeatureGroup("Contorno protegido da classe").add_to(mapa)
    folium.Circle(radius = float(dmax_contorno)*1000, 
                location=[latitude_proposta, longitude_proposta], 
                popup="Contorno protegido da classe", 
                color="red", 
                weight = 3, 
                fill=False).add_to(cp_classe)
    
    # Contorno protegido da estação
    # -------------------------------------------------------------------------
    
    # cp_estacao = folium.FeatureGroup("Contorno protegido da estação").add_to(mapa)
    
    # folium.Polygon(coord_contorno_protegido,
    #               color = "green",
    #               fill_color = "green",
    #               fill_opacity = 0.1).add_to(cp_estacao)

    # Camadas extras 
    # -------------------------------------------------------------------------

    folium.TileLayer(tiles = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
                    attr = "Tiles &copy; Esri &mdash; Source: Esri, DeLorme, NAVTEQ, USGS, Intermap, iPC, NRCAN, Esri Japan, METI, Esri China (Hong Kong), Esri (Thailand), TomTom, 2012", 
                    name = "Esri.WorldStreetMap").add_to(mapa)

    folium.TileLayer(tiles = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                    attr = "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community", 
                    name = "Esri.WorldImagery").add_to(mapa)

    folium.TileLayer(tiles = "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
                    attr = "https://opentopomap.org", 
                    name = "OpenTopoMap").add_to(mapa)

    folium.TileLayer(tiles = "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                    attr = "https://www.openstreetmap.org/copyright", 
                    name = "OpenStreetMap.Mapnik").add_to(mapa)

    # Controle de camadas
    # -------------------------------------------------------------------------

    folium.LayerControl().add_to(mapa)

    # Rosa dos ventos 
    # -------------------------------------------------------------------------

    with open(d.ROSA_DOS_VENTOS, "rb") as arquivo_imagem:
        string_imagem = base64.b64encode(arquivo_imagem.read()).decode("utf-8")

    FloatImage("data:image/png; base64, {}".format(string_imagem), bottom = 1, left = 1).add_to(mapa)

    # Ferramenta para desenhar polígonos 
    # -------------------------------------------------------------------------

    # Draw().add_to(mapa)

    # Coordenadas em qualquer ponto 
    # -------------------------------------------------------------------------

    mapa.add_child(folium.LatLngPopup())

    # Legenda extra 
    # -------------------------------------------------------------------------

    legenda_mapa = """
    {% macro html(this,kwargs) %}

    <div style = "position: fixed;
    bottom: 12px;
    left: 100px;
    width: 250px;
    height: 90px;
    font-size: 14px;
    z-index: 9999;
    ">

    <p><a style = "color: black; margin-left: 20px;"></a><b>Legenda (contornos)</b></p>

    <a style = "color:red; margin-left: 20px">&HorizontalLine;
    </a>Contorno protegido da classe

    <p><a style = "color:green; margin-left: 20px;">&HorizontalLine;
    </a>Contorno protegido da estação</p>

    </div>

    <div style = "position: fixed;
    bottom: 12px;
    left: 100px;
    width: 250px;
    height: 90px;
    font-size: 14px;
    background-color: white;
    z-index: 9998;
    opacity: 0.7;
    border: 2px solid grey;
    border-radius: 6px;
    ">
    </div>

    {% endmacro %}
    """
    legenda = branca.element.MacroElement()
    legenda._template = branca.element.Template(legenda_mapa)
    mapa.add_child(legenda)

    return mapa
