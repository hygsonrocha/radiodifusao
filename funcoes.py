import geopandas as gpd
import shapely.geometry

# -----------------------------------------------------------------------------------------------------------------------------------------

def dmax_cp(classe, canal=None):

    # Identifica a distância máxima (dmax) ao contorno protegido (cp),
    # com base no número e na classe do canal. Função válida apenas para
    # canais de FM e de TV digital.

    canal = int(canal)

    if classe.lower() in ['e', 'especial']:
        if canal <= 13:
            dmax = 65.6
        elif canal <= 46:
            dmax = 58.0
        elif canal >= 47:
            dmax = 58.0
    elif classe == 'A':
        if canal <= 13:
            dmax = 47.9
        elif canal >= 14:
            dmax = 42.5
    elif classe == 'B':
        if canal <= 13:
            dmax = 32.3
        elif canal >= 14:
            dmax = 29.1
    elif classe == 'C':
        if canal == None:
            dmax = 7.5
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

def latitude_gms_para_decimal(latitude_gms):

    g = float(latitude_gms.split('°')[0])
    m = float(latitude_gms.split('°')[1].split("'")[0])
    s = float(latitude_gms.split('°')[1].split("'")[1])
    latitude = g + m/60 + s/3600

    if latitude_gms[-1] == 'S':
        latitude = -latitude

    return latitude

# -----------------------------------------------------------------------------------------------------------------------------------------

def longitude_gms_para_decimal(longitude_gms):

    g = float(longitude_gms.split('°')[0])
    m = float(longitude_gms.split('°')[1].split("'")[0])
    s = float(longitude_gms.split('°')[1].split("'")[1])
    longitude = g + m/60 + s/3600

    if longitude_gms[-1] == 'W':
        longitude = -longitude

    return longitude

# ---------------------------------------------------------------------

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
    
# ---------------------------------------------------------------------

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

# ---------------------------------------------------------------------


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


def circulo_gdf(longitude, latitude, raio):

    # Gera o shapefile de um círculo com centro em (longitude, latitude) e raio em km.
    # Longitude e latitude em graus, raio em km

    centro_circulo = shapely.geometry.Point(longitude, latitude)
    gdf_centro_circulo = gpd.GeoDataFrame(
        geometry=[centro_circulo], crs='EPSG:4674')
    centro_circulo_utm = gdf_centro_circulo.to_crs(epsg=5880)
    circulo_utm = centro_circulo_utm.buffer(raio * 10**3)  # raio em metros
    circulo = circulo_utm.to_crs('EPSG:4674')

    return gpd.GeoDataFrame(geometry=circulo)


# -----------------------------------------------------------------------------------------------------------------------------------------

def situacao_setor(cd_sit, nm_mun, nm_dist):

    # Cidade é a localidade  onde  está  sediada  a  Prefeitura  Municipal. É constituída pela área urbana do distrito sede e
    # delimitada pelo perímetro urbano (setores tipos 1 e 2) estabelecido por lei municipal.

    # Setores censitários urbanos de cidades são aqueles cujo nome do município (nm_mun) é o mesmo do nome do distrito (nm_dist) sede.

    if cd_sit in ['1', '2']:
        if nm_mun == nm_dist:
            return 'área urbana de cidade'
        else:
            return 'área urbana'
    elif cd_sit == '3':
        return 'núcleo urbano'
    elif cd_sit in ['5', '6', '7']:
        return 'aglomerado rural'
    elif cd_sit == '8':
        return 'área rural'
    elif cd_sit == '9':
        return "massa d'água"


# -----------------------------------------------------------------------------------------------------------------------------------------
    

def valor_referencia(uf, enquadramento, cd_mun):

    # Determinação do valor de referência - Anexo XXVIII da Portaria GM/MCom nº 9018/2023
    # Retorna o código, município e valor de referência

    if enquadramento == 'B':
        if uf == 'SC':
            return ['4205407', 'Florianópolis', 363499.72]
        elif uf == 'AC':
            return ['1200401', 'Rio Branco', 32586.82]
        elif uf == 'AL':
            return ['2704302', 'Maceió', 144040.28]
        elif uf == 'AP':
            return ['1600303', 'Macapá', 60014.83]
        elif uf == 'BA':
            return ['2927408', 'Salvador', 169291.50]
        elif uf == 'AM':
            return ['1302603', 'Manaus', 78099.69]
        elif uf == 'MA':
            return ['2111300', 'São Luís', 144005.30]
        elif uf == 'PA':
            return ['1501402', 'Belém', 85097.28]
        elif uf == 'SP':
            if cd_mun in ['3503901', '3505708', '3506607', '3509007', '3509205', '3510609', 
                          '3513009', '3513801', '3515004', '3515103', '3515707', '3516309',
                          '3516408', '3518305', '3518800', '3522208', '3522505', '3523107',
                          '3525003', '3526209', '3528502', '3529401', '3530607', '3534401',
                          '3539103', '3539806', '3543303', '3544103', '3545001', '3546801',
                          '3547304', '3547809', '3548708', '3548807', '3549953', '3550308',
                          '3552502', '3552809', '3556453']:
                return ['NA', 'Região Metropolitana de São Paulo', 2376643.72]
            else:
                return ['3509502', 'Campinas', 249622.55]
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
        elif uf == 'MT':
            return ['5103403', 'Cuiabá', 164843.20]
        elif uf == 'MS':
            return ['5002704', 'Campo Grande', 215788.29]
        elif uf == 'DF':
            return ['5300108', 'Brasília', 307127.24]
        elif uf == 'RO':
            return ['1100205', 'Porto Velho', 45590.69]
        elif uf == 'RJ':
            return ['3304557', 'Rio de Janeiro', 701663.27]
        elif uf == 'PE':
            return ['2611606', 'Recife', 157833.60]
        elif uf == 'PR':
            return ['4106902', 'Curitiba', 469494.06]
        elif uf == 'PI':
            return ['2211001', 'Teresina', 144681.50]
        elif uf == 'RN':
            return ['2408102', 'Natal', 145172.62]
        elif uf == 'RR':
            return ['1400100', 'Boa Vista', 27459.32]
        elif uf == 'RS':
            return ['4314902', 'Porto Alegre', 425475.87]
        elif uf == 'ES':
            return ['3205200', 'Vila Velha', 69587.43]
        elif uf == 'TO':
            return ['1721000', 'Palmas', 15473.83]

    if enquadramento == 'C':
        if uf == 'SC':
            return ['4205407', 'Florianópolis', 852817.55]
        elif uf == 'AC':
            return ['1200401', 'Rio Branco', 77202.31]
        elif uf == 'AL':
            return ['2704302', 'Maceió', 337505.73]
        elif uf == 'AP':
            return ['1600303', 'Macapá', 111663.65]
        elif uf == 'BA':
            return ['2927408', 'Salvador', 397584.59]
        elif uf == 'AM':
            return ['1302603', 'Manaus', 183187.51]
        elif uf == 'MA':
            return ['2111300', 'São Luís', 338625.89]
        elif uf == 'PA':
            return ['1501402', 'Belém', 199600.76]        
        elif uf == 'SP':
            if cd_mun in ['3503901', '3505708', '3506607', '3509007', '3509205', '3510609', 
                          '3513009', '3513801', '3515004', '3515103', '3515707', '3516309',
                          '3516408', '3518305', '3518800', '3522208', '3522505', '3523107',
                          '3525003', '3526209', '3528502', '3529401', '3530607', '3534401',
                          '3539103', '3539806', '3543303', '3544103', '3545001', '3546801',
                          '3547304', '3547809', '3548708', '3548807', '3549953', '3550308',
                          '3552502', '3552809', '3556453']:
                return ['3550308', 'Região Metropolitana de São Paulo', 5574558.80]
            else:
                return ['3509502', 'Campinas', 585504.63]
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
        elif uf == 'MT':
            return ['5103403', 'Cuiabá', 387763.39]
        elif uf == 'MS':
            return ['5002704', 'Campo Grande', 505001.04]
        elif uf == 'DF':
            return ['5300108', 'Brasília', 720385.32]
        elif uf == 'RO':
            return ['1100205', 'Porto Velho', 105637.44]
        elif uf == 'RJ':
            return ['3304557', 'Rio de Janeiro', 1629200.59]
        elif uf == 'PE':
            return ['2611606', 'Recife', 369776.49]
        elif uf == 'PR':
            return ['4106902', 'Curitiba', 1098420.32]
        elif uf == 'PI':
            return ['2211001', 'Teresina', 339511.65]
        elif uf == 'RN':
            return ['2408102', 'Natal', 340511.07]
        elif uf == 'RR':
            return ['1400100', 'Boa Vista', 64624.06]
        elif uf == 'RS':
            return ['4314902', 'Porto Alegre', 995714.32]
        elif uf == 'ES':
            return ['3205200', 'Vila Velha', 79940.86]
        elif uf == 'TO':
            return ['1721000', 'Palmas', 36039.46]
        
# -----------------------------------------------------------------------------------------------------------------------------------------