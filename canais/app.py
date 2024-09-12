import streamlit as st
import xml.etree.ElementTree as ET
import requests
import pandas as pd
from io import BytesIO

# Dropbox file link
dropbox_link = "https://www.dropbox.com/s/yourfileid/plano_basicoTVFM.xml?dl=1"  # Change ?dl=0 to ?dl=1 for direct download
dropbox_link = "https://www.dropbox.com/scl/fi/lebc6drdrtramrqia2jnk/plano_basicoTVFM.xml?dl=1"

# Function to download large XML file
def download_xml_from_dropbox(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BytesIO(response.content)
    else:
        st.error("Failed to download the file from Dropbox.")
        return None

# Load and parse the XML file
def parse_xml(file_obj):
    tree = ET.parse(file_obj)
    root = tree.getroot()
    return root

# Process XML data into a DataFrame
def process_xml_data(xml_root):
    rows = []
    for row in xml_root.findall('row'):
        row_data = row.attrib
        rows.append(row_data)
    return pd.DataFrame(rows)

# Streamlit app
st.title("Streamlit App for Large XML Processing")

# Download and load XML file
file_obj = download_xml_from_dropbox(dropbox_link)
if file_obj:
    xml_root = parse_xml(file_obj)
    data_df = process_xml_data(xml_root)
    st.write(data_df)