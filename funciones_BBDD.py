import xml.etree.ElementTree as ET
import pandas as pd
import argparse
import os
from pathlib import Path

#DF principal
def csv_enzimas(xml_file, output_file):
    '''

    Parámetros
    ----------------
        xml_file -
        output_file-

    Devolucion
    ---------------
        None
    '''
    #Separadoor de DB
    ns = "{http://www.drugbank.ca}"
    
    rows = []
    
    context = ET.iterparse(xml_file, events=("end",))
    
    for event, elem in context:
        if elem.tag == ns + "drug":
    
            #ID
            drug_id_elem = elem.find(ns + 'drugbank-id[@primary="true"]')
            if drug_id_elem is None:
                elem.clear()
                continue
    
            drug_id = drug_id_elem.text
    
            #Nombre
            name_elem = elem.find(ns + "name")
            drug_name = name_elem.text if name_elem is not None else ""
    
            #Sinónimos
            synonyms_list = []
            for syn in elem.findall(ns + "synonyms/" + ns + "synonym"):
                if syn.text:
                    synonyms_list.append(syn.text)
    
            synonyms = "|".join(synonyms_list)  # separados por |
    
            #Targets
            for target in elem.findall(ns + 'targets/' + ns + 'target'):
                
                poly = target.find(ns + 'polypeptide')
                if poly is not None:
                    gene = poly.findtext(ns + 'gene-name', default='')
                    uni = poly.get('id', '')
                else:
                    gene = ''
                    uni = ''
    
                actions = [a.text for a in target.findall(ns + "actions/" + ns + "action") if a.text]
                action = "|".join(actions)
    
                rows.append([drug_id, drug_name, synonyms, 'target', gene, uni, action])
    
            #Enzimas
            for enzyme in elem.findall(ns + 'enzymes/' + ns + 'enzyme'):
                poly = enzyme.find(ns + 'polypeptide')
        
                if poly is not None:
                    gene = poly.findtext(ns + 'gene-name', default='')
                    uni = poly.get('id', '')
                else:
                    gene = ''
                    uni = ''
                actions = [a.text for a in enzyme.findall(ns + "actions/" + ns + "action") if a.text]
                action = "|".join(actions)
    
                rows.append([drug_id, drug_name, synonyms, 'enzyme', gene, '', action])
    
            elem.clear()
    
    #Creamos el dataframe
    df = pd.DataFrame(rows, columns=[
        "drugbank_id",
        "drug_name",
        "synonyms",
        "type",
        "gene_name",
        "uniprot_id",
        "action"
    ])
    
    #Lo guardamos en un archivo auxiliar
    df.to_csv(output_file, index=False)

    #Print para ver que lo hemos hecho bien
    print(f"Archivo guardado como: {output_file}")

#ATC DrugBank
def csv_ATC_db (xml_file, output_file):
    '''
    Obtenemos los códigos ATC de DrugBank y lo exportamos a otro csv

    Parámetros
    -------------
        xml_file -
        output_file -

    Return
    ------------
        None
    '''
    # Separador específico de DrugBank
    ns = "{http://www.drugbank.ca}"
    
    rows = []
    
    # Leemos el documento de manera eficiente en terminos de memoria (no carga el documento entero, va leyendo evento por evento)
    context = ET.iterparse(xml_file, events=("end",))
    
    for event, elem in context:
        if elem.tag == ns + "drug":
    
            # ID
            drug_id_elem = elem.find(ns + 'drugbank-id[@primary="true"]')
            if drug_id_elem is None:
                elem.clear()
                continue
    
            drug_id = drug_id_elem.text
    
            # Nombre
            name_elem = elem.find(ns + "name")
            drug_name = name_elem.text if name_elem is not None else ""

            # Códigos ATC
            atc_list = []
            for atc in elem.findall(ns + "atc-codes/" + ns + "atc-code"):
                code = atc.get("code")
                if code:
                    atc_list.append(code)
            
            atc_codes = "|".join(atc_list)

            rows.append([drug_id, drug_name, atc_codes])
            

            elem.clear()

    # Creamos el DataFrame con las filas que hemos añadido a rows
    df = pd.DataFrame(rows, columns=[
        "drugbank_id",
        "drug_name",
        "atc_codes"
    ])
    
    # Lo guardamos en un archivo csv para poder trabajar con los datos
    df.to_csv(output_file, index=False)
    
    print(f"Archivo guardado como: {output_file}")

#SIDDER (efectos adversos)
def csv_sidder(path_se, path_freq, path_names, output_csv, only_pt=True):
    """
    Construye un dataset completo de SIDER uniendo los tres archivos proporcionados

    Parámetros:
    ---------------------
        path_se - Ruta a meddra_all_se.tsv
        path_freq - Ruta a meddra_freq.tsv
        path_names - Ruta a drug_names.tsv
        output_csv -  Ruta donde guardar el CSV final
        only_pt - Si True, filtra solo términos PT

    Devuelve:
    --------------------
        df_final - pandas.DataFrame
    """

    # Cargamos datasets
    df_se = pd.read_csv(path_se, sep="\t", header=None, names=[
        "flat", "stereo", "umls_id", "meddra_type",
        "umls_id_meddra", "side_effect"
    ])

    df_freq = pd.read_csv(path_freq, sep="\t", header=None, names=[
            "flat", "stereo", "umls_id", "placebo",
            "freq_desc","lower","upper", "meddra_type", 
            "umls_id_meddra","side_effect"
        ])
    
    df_names = pd.read_csv(path_names, sep="\t", header=None, names=[
            "flat", "drug_name"
        ])

    # Filtramos por PT (prefered term)
    if only_pt:
        df_se = df_se[df_se["meddra_type"] == "PT"]

    # Merge efectos + frecuencias
    df_merge = pd.merge(df_se, df_freq,
        on=["flat", "umls_id_meddra"], how="left", suffixes=("_se", "_freq")
    )

    #Añadimos nombres
    df_final = pd.merge(df_merge,df_names,
        on="flat", how="left"
    )

    #Frecuencias medias y union al df final
    df_final["freq_mean"] = (df_final["lower"] + df_final["upper"]) / 2

    df_alternativo = df_final.groupby(["flat", "umls_id_meddra"])["freq_mean"].mean().reset_index()

    df_definitivo = pd.merge(df_final, df_alternativo,
        on=["flat","umls_id_meddra"], how="left"
    )
    
    #Seleccionamos las columnas que nos interesan
    df_definitivo = df_definitivo[[
        "flat",
        "drug_name",
        "side_effect_se",
        "freq_mean_y"
    ]]

    #7. Eliminamos duplicados y valores nulos solo existentes en la columna de frecuencias (se comprobó en un notebook alternativo)
    df_definitivo = df_definitivo.dropna()
    df_definitivo = df_definitivo.drop_duplicates()

    #Guardamos csv
    df_definitivo.to_csv(output_csv, index=False)

    print(f"CSV guardado en: {output_csv}")


#CIMA
def get_ns(root: ET.Element) -> str:
    """Extrae el namespace URI del elemento raíz (ej. '{http://...}')."""
    tag = root.tag
    if tag.startswith("{"):
        return tag.split("}")[0] + "}"
    return ""
def find_text(element: ET.Element, tag: str, ns: str = "") -> str:
    """Devuelve el texto de un subelemento o cadena vacía si no existe."""
    child = element.find(f"{ns}{tag}")
    if child is not None and child.text:
        return child.text.strip()
    return ""
def cargar_principios_activos(carpeta: Path) -> dict:
    """
    Devuelve dict {cod_principio_activo (str): nombre_pa (str)}.
    La clave es el codigoprincipioactivo (p.ej. '160'), NO el nroprincipioactivo.
    """
    ruta = carpeta / "DICCIONARIO_PRINCIPIOS_ACTIVOS.xml"
    tree = ET.parse(ruta)
    root = tree.getroot()
    ns = get_ns(root)

    mapping = {}
    for pa in root.findall(f"{ns}principiosactivos"):
        # El campo que aparece en Prescripcion.xml es cod_principio_activo,
        # que coincide con nroprincipioactivo (entero), NO con codigoprincipioactivo.
        nro = find_text(pa, "nroprincipioactivo", ns)
        nombre = find_text(pa, "principioactivo", ns)
        if nro:
            mapping[nro] = nombre
    return mapping
def cargar_formas_farmaceuticas(carpeta: Path) -> dict:
    """
    Devuelve dict {codigoformafarmaceutica (str): nombre_forma (str)}.
    """
    ruta = carpeta / "DICCIONARIO_FORMA_FARMACEUTICA.xml"
    tree = ET.parse(ruta)
    root = tree.getroot()
    ns = get_ns(root)

    mapping = {}
    for ff in root.findall(f"{ns}formasfarmaceuticas"):
        cod = find_text(ff, "codigoformafarmaceutica", ns)
        nombre = find_text(ff, "formafarmaceutica", ns)
        if cod:
            mapping[cod] = nombre
    return mapping
def cargar_situaciones_registro(carpeta: Path) -> dict:
    """
    Devuelve dict {codigosituacionregistro (str): descripcion (str)}.
    """
    ruta = carpeta / "DICCIONARIO_SITUACION_REGISTRO.xml"
    tree = ET.parse(ruta)
    root = tree.getroot()
    ns = get_ns(root)

    mapping = {}
    for sr in root.findall(f"{ns}situacionesregistro"):
        cod = find_text(sr, "codigosituacionregistro", ns)
        desc = find_text(sr, "situacionregistro", ns)
        if cod:
            mapping[cod] = desc
    return mapping
def parsear_prescripcion(carpeta: Path) -> pd.DataFrame:
    """
    Lee Prescripcion.xml y los diccionarios auxiliares y devuelve un DataFrame
    con las 6 columnas requeridas.
    """
    # -- Diccionarios --------------------------------------------------------
    print("Cargando diccionarios…")
    pa_dict   = cargar_principios_activos(carpeta)
    ff_dict   = cargar_formas_farmaceuticas(carpeta)
    sit_dict  = cargar_situaciones_registro(carpeta)

    # -- Fichero principal ---------------------------------------------------
    ruta_main = carpeta / "Prescripcion.xml"
    print(f"Parseando {ruta_main} (puede tardar unos segundos)…")

    # Usamos iterparse para no cargar 190 MB enteros en memoria de golpe
    registros = []
    ns_uri = None   # se detecta en el primer elemento

    context = ET.iterparse(str(ruta_main), events=("start", "end"))

    current = None   # dict del medicamento en curso

    for event, elem in context:
        # Detectar namespace en el primer elemento raíz
        if ns_uri is None and event == "start":
            tag = elem.tag
            ns_uri = tag.split("}")[0] + "}" if tag.startswith("{") else ""

        tag_local = elem.tag.replace(ns_uri or "", "")

        if event == "start" and tag_local == "prescription":
            current = {
                "nombre_medicamento": "",
                "numero_registro": "",
                "principios_activos_raw": [],   # lista de (cod, dosis, unidad)
                "atc_raw": [],                  # lista de cod_atc
                "forma_farmaceutica_cod": "",
                "situacion_registro_cod": "",
            }

        if event == "end" and current is not None:

            if tag_local == "des_nomco":
                current["nombre_medicamento"] = (elem.text or "").strip()

            elif tag_local == "nro_definitivo":
                current["numero_registro"] = (elem.text or "").strip()

            elif tag_local == "cod_sitreg":
                current["situacion_registro_cod"] = (elem.text or "").strip()

            # Forma farmacéutica: tomamos cod_forfar (no la simplificada)
            elif tag_local == "cod_forfar":
                if not current["forma_farmaceutica_cod"]:   # primer hallazgo
                    current["forma_farmaceutica_cod"] = (elem.text or "").strip()

            # Principios activos dentro de <composicion_pa>
            elif tag_local == "cod_principio_activo":
                current["principios_activos_raw"].append((elem.text or "").strip())

            # ATC: puede haber varios <atc><cod_atc>…
            elif tag_local == "cod_atc":
                val = (elem.text or "").strip()
                if val and val not in current["atc_raw"]:
                    current["atc_raw"].append(val)

            elif tag_local == "prescription":
                # Resolver principios activos
                pas = [
                    pa_dict.get(cod, cod)
                    for cod in current["principios_activos_raw"]
                ]
                principios_activos = " / ".join(dict.fromkeys(pas))   # únicos, orden

                # Resolver código ATC (tomamos el primero — el principal)
                codigo_atc = current["atc_raw"][0] if current["atc_raw"] else ""

                # Resolver forma farmacéutica
                ff_cod = current["forma_farmaceutica_cod"]
                forma_farmaceutica = ff_dict.get(ff_cod, ff_cod)

                # Resolver situación de registro
                sit_cod = current["situacion_registro_cod"]
                situacion_registro = sit_dict.get(sit_cod, sit_cod)

                registros.append({
                    "nombre_medicamento": current["nombre_medicamento"],
                    "numero_registro":    current["numero_registro"],
                    "principios_activos": principios_activos,
                    "codigo_atc":         codigo_atc,
                    "forma_farmaceutica": forma_farmaceutica,
                    "situacion_registro": situacion_registro,
                })

                current = None
                elem.clear()   # liberar memoria

    print(f"Registros procesados: {len(registros):,}")
    df = pd.DataFrame(registros, columns=[
        "nombre_medicamento",
        "numero_registro",
        "principios_activos",
        "codigo_atc",
        "forma_farmaceutica",
        "situacion_registro",
    ])
    return df
def main():
    parser = argparse.ArgumentParser(
        description="Genera un DataFrame con 6 columnas a partir de la carpeta "
                    "prescripcion de la AEMPS."
    )
    parser.add_argument(
        "--carpeta",
        default="prescripcion",
        help="Ruta a la carpeta descomprimida (por defecto: ./prescripcion)",
    )
    parser.add_argument(
        "--salida",
        default="medicamentos.csv",
        help="Fichero CSV de salida (por defecto: medicamentos.csv)",
    )
    args = parser.parse_args()

    carpeta = Path(args.carpeta)
    if not carpeta.is_dir():
        raise FileNotFoundError(f"No se encuentra la carpeta: {carpeta}")

    df = parsear_prescripcion(carpeta)

    print(df.head(5).to_string())
    print(f"\nShape: {df.shape}")

    df.to_csv(args.salida, index=False, encoding="utf-8-sig")
    print(f"\nCSV guardado en: {args.salida}")

    return df
    






#LO QUE YA TENIA

def drugbank_enzimas(xml_file, output_file):
    '''
    Obtención de un csv con las columnas necesarias de DrugBank 

    Parámetros
    -------------
        
    Return
    --------------
        None
    '''
    # Separador específico de DrugBank
    ns = "{http://www.drugbank.ca}"
    
    rows = []
    
    # Leemos el documento de manera eficiente en terminos de memoria (no carga el documento entero, va leyendo evento por evento)
    context = ET.iterparse(xml_file, events=("end",))
    
    for event, elem in context:
        if elem.tag == ns + "drug":
    
            # ID
            drug_id_elem = elem.find(ns + 'drugbank-id[@primary="true"]')
            if drug_id_elem is None:
                elem.clear()
                continue
    
            drug_id = drug_id_elem.text
    
            # Nombre
            name_elem = elem.find(ns + "name")
            drug_name = name_elem.text if name_elem is not None else ""
    
            # Lista de sinónimos
            synonyms_list = []
            for syn in elem.findall(ns + "synonyms/" + ns + "synonym"):
                if syn.text:
                    synonyms_list.append(syn.text)
            
            synonyms = "|".join(synonyms_list) #Separamos cada sinónimo existente en DrugBank con | 
    
            # Targets de cada fármaco
            for target in elem.findall(ns + 'targets/' + ns + 'target'):
                
                poly = target.find(ns + 'polypeptide')
                if poly is not None:
                    gene = poly.findtext(ns + 'gene-name', default='')
                    uni = poly.get('id', '')
                else:
                    gene = ''
                    uni = ''
    
                actions = [a.text for a in target.findall(ns + "actions/" + ns + "action") if a.text]
                action = "|".join(actions)
    
                rows.append([drug_id, drug_name, synonyms, 'target', gene, uni, action])
    
            # Enzymes metabolizadas por cada fármaco
            for enzyme in elem.findall(ns + 'enzymes/' + ns + 'enzyme'):
                poly = enzyme.find(ns + 'polypeptide')
        
                if poly is not None:
                    gene = poly.findtext(ns + 'gene-name', default='')
                    uni = poly.get('id', '')
                else:
                    gene = ''
                    uni = ''
                actions = [a.text for a in enzyme.findall(ns + "actions/" + ns + "action") if a.text]
                action = "|".join(actions)
    
                rows.append([drug_id, drug_name, synonyms, 'enzyme', gene, '', action])
    
                elem.clear()
    
    # Creamos el DataFrame con las filas que hemos añadido a rows
    df = pd.DataFrame(rows, columns=[
        "drugbank_id",
        "drug_name",
        "synonyms",
        "type",
        "gene_name",
        "uniprot_id",
        "action"
    ])
    
    # Lo guardamos en un archivo csv para poder trabajar con los datos
    df.to_csv(output_file, index=False)
    
    print(f"Archivo guardado como: {output_file}")


def drugbank_clasificacion (xml_file, output_file):
    '''
    Obtenemos los códigos ATC y el id de la FDA

    Parámetros
    ------------

    Return
    ------------
        None
    '''
    # Separador específico de DrugBank
    ns = "{http://www.drugbank.ca}"
    
    rows = []
    
    # Leemos el documento de manera eficiente en terminos de memoria (no carga el documento entero, va leyendo evento por evento)
    context = ET.iterparse(xml_file, events=("end",))
    
    for event, elem in context:
        if elem.tag == ns + "drug":
    
            # ID
            drug_id_elem = elem.find(ns + 'drugbank-id[@primary="true"]')
            if drug_id_elem is None:
                elem.clear()
                continue
    
            drug_id = drug_id_elem.text
    
            # Nombre
            name_elem = elem.find(ns + "name")
            drug_name = name_elem.text if name_elem is not None else ""

            # Códigos ATC
            atc_list = []
            for atc in elem.findall(ns + "atc-codes/" + ns + "atc-code"):
                code = atc.get("code")
                if code:
                    atc_list.append(code)
            
            atc_codes = "|".join(atc_list)

            rows.append([drug_id, drug_name, atc_codes])
            

            elem.clear()

    # Creamos el DataFrame con las filas que hemos añadido a rows
    df = pd.DataFrame(rows, columns=[
        "drugbank_id",
        "drug_name",
        "atc_codes"
    ])
    
    # Lo guardamos en un archivo csv para poder trabajar con los datos
    df.to_csv(output_file, index=False)
    
    print(f"Archivo guardado como: {output_file}")