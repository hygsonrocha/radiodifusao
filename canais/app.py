import streamlit as st
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
import shapely.geometry
import geopandas as gpd
import folium
from folium import Circle
import matplotlib.pyplot as plt
from scipy import interpolate
import requests

# Streamlit app title
st.title("Radiodifusão XML Data Processing from GitHub")

# URL of the raw XML file hosted on GitHub
github_raw_url = "https://raw.githubusercontent.com/your-github-username/your-repo-name/main/plano_basicoTVFM.xml"

# Function to download the XML file from GitHub
def download_xml_from_github(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        st.error("Failed to download the file from GitHub.")
        return None

# Function to map service type
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

# Function to map channel occupation
def ocupacao_canal(status):
    status = status.upper().strip()
    if 'C0' in status:
        return 'Canal Vago'
    return 'Canal Ocupado'

# Function to handle XML file processing
def parse_xml(file_content):
    root = ET.fromstring(file_content)
    rows = []
    for row in root.findall('row'):
        row_data = row.attrib
        rows.append(row_data)
    return pd.DataFrame(rows)

# Streamlit app
st.info("Processing XML data from GitHub...")

# Download the XML file from GitHub
file_content = download_xml_from_github(github_raw_url)
if file_content:
    # Parse the XML data
    data_df = parse_xml(file_content)

    # Process the DataFrame
    data_df['Canal'] = pd.to_numeric(data_df['Canal'], errors='coerce')
    data_df['Frequencia'] = pd.to_numeric(data_df['Frequencia'], errors='coerce')
    data_df['Latitude'] = pd.to_numeric(data_df['Latitude'], errors='coerce')
    data_df['Longitude'] = pd.to_numeric(data_df['Longitude'], errors='coerce')
    data_df['ERP'] = pd.to_numeric(data_df['ERP'], errors='coerce')
    data_df['Altura'] = pd.to_numeric(data_df['Altura'], errors='coerce')

    # Apply custom mapping functions
    data_df['TipoServico'] = data_df['Servico'].apply(mapear_servico)
    data_df['Ocupacao'] = data_df['Status'].apply(ocupacao_canal)

    # Filter the data for TV services
    servicos_tv = ['TV', 'RTV', 'TVD', 'RTVD']
    canais_tv = data_df[data_df['TipoServico'].isin(servicos_tv)]

    # Display the processed DataFrame
    st.subheader("TV Channel Data")
    st.dataframe(canais_tv)

    # Plot a geographical map using Folium
    mapa = folium.Map(location=[-15.793889, -47.882778], zoom_start=5)

    for _, row in canais_tv.iterrows():
        if not pd.isnull(row['Latitude']) and not pd.isnull(row['Longitude']):
            popup = f"Fistel: {row['Fistel']}, Canal: {row['Canal']}"
            Circle(location=[row['Latitude'], row['Longitude']],
                   radius=10000, color='blue', fill=True, fill_opacity=0.2, popup=popup).add_to(mapa)

    # Save and display the map
    mapa.save("mapa_canais_tv.html")
    st.markdown("[View Interactive Map](mapa_canais_tv.html)", unsafe_allow_html=True)

    # Example Antenna Diagram using Matplotlib
    st.subheader("Antenna Polar Diagram")
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    fi = np.arange(0, 361, 5)
    Er_dBd = np.random.uniform(-20, 0, size=len(fi))  # Replace with real data
    ax.plot(np.deg2rad(fi), Er_dBd)
    ax.set_ylim(-20, 0)
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_yticks(np.arange(-20, 0, 5))
    st.pyplot(fig)

else:
    st.error("Failed to load the XML file from GitHub.")