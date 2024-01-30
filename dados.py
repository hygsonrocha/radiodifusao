LATITUDE_PROPOSTA_GMS = "21° 42' 33.01'' S"         
LONGITUDE_PROPOSTA_GMS = "46° 14' 2.0'' W" 
CLASSE_ATUAL = 'B1'
CLASSE_PROPOSTA = 'A4'
CANAL_PROPOSTO = 253

SGBD = "postgresql"
HOST = "rds-postgresql.c7q26ge8uwvb.us-east-1.rds.amazonaws.com"
PORT = "5432"
PORTA = "5432"
USER = "postgres"
PASSWORD = 'postgres'
REGION = "us-east-1"
DBNAME = "postgres"

DB_CONNECTION_URL = f"{SGBD}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"

# Dados armazenados localmente

MUNICIPIOS = r"/Users/hygson/Documents/3-Recursos/Dados/Municipios/BR_Municipios_2022.shp"
MUNICIPIOS_COORD = r"/Users/hygson/Documents/3-Recursos/Dados/Municipios/Coordenadas/sidra_9522_PopResid_munic_22_ptSede.shp"
SETORES_CENSITARIOS = r"/Users/hygson/Documents/3-Recursos/Dados/Setores-Censitarios/BR_Setores_2021/BR_Setores_2021.shp"
ROSA_DOS_VENTOS = r"/Users/hygson/Documents/3-Recursos/Python/Radiodifusao/promocao-de-classe/mapas/rosa-dos-ventos.png"
POPULACAO = r"/Users/hygson/Documents/3-Recursos/Dados/Populacao/2022/censo-2022-tabela-4714-população-residente.xlsx"

# Dados armazenados no provedor de hospedagem

# MUNICIPIOS = r"https://rfcalc.com/dados/BR_Municipios_2022.shp"
# MUNICIPIOS_COORD = r"https://rfcalc.com/dados/sidra_9522_PopResid_munic_22_ptSede.shp"
# SETORES_CENSITARIOS = r"https://rfcalc.com/dados/BR_Setores_2021.shp"
# ROSA_DOS_VENTOS = r"https://rfcalc.com/dados/rosa-dos-ventos.png"
# POPULACAO = r"https://rfcalc.com/dados/censo-2022-tabela-4714-população-residente.xlsx"





