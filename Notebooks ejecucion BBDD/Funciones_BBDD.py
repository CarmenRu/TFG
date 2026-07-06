import xml.etree.ElementTree as ET
import pandas as pd
import os
from pathlib import Path
import requests
import time

def csv_enzimas(xml_file, output_file):
    '''
    Obtiene información del id, nombre, sinonimos, targets y enzimas de drugbank y se exporta en un csv

    Parámetros
    ----------------
        xml_file - archivo xml con la documentacion de drugbank
        output_file- nombre del documento donde queremos guardar la información extraída.

    Devolución
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
    Obtiene los códigos ATC de DrugBank junto con el id y el nombre del principio activo y se exporta a otro csv

    Parámetros
    -------------
        xml_file - archivo xml con la documentacion de drugbank
        output_file- nombre del documento donde queremos guardar la información extraída.

    Devolución
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

            # Se añade
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
    
    #print explicativo
    print(f"Archivo guardado como: {output_file}")

#SIDER(efectos adversos)
def csv_sidder(path_se, path_freq, path_names, output_csv, only_pt=True):
    """
    Construye un dataset completo de SIDER uniendo los tres archivos proporcionados

    Parámetros
    ---------------------
        path_se - Ruta a meddra_all_se.tsv
        path_freq - Ruta a meddra_freq.tsv
        path_names - Ruta a drug_names.tsv
        output_csv -  Ruta donde guardar el CSV final
        only_pt - Si True, filtra solo términos PT (Preferred Terms)

    Devolución
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

    # Eliminamos duplicados y valores nulos solo existentes en la columna de frecuencias (se comprobó en un notebook alternativo)
    df_definitivo = df_definitivo.dropna()
    df_definitivo = df_definitivo.drop_duplicates()

    #Guardamos csv
    df_definitivo.to_csv(output_csv, index=False)

    #print explicativo
    print(f"CSV guardado en: {output_csv}")


#CIMA
def get_ns(root: ET.Element):
    """
    Extrae el namespace del elemento raíz del documento XML.

    Parámetros
    ---------------------
        root - Elemento raíz del árbol XML.

    Devolución
    ---------------------
        str - Namespace del documento en formato '{http://...}'. Si el XML no utiliza namespace devuelve una cadena vacía.
    """
    tag = root.tag
    if tag.startswith("{"):
        return tag.split("}")[0] + "}"
    return ""
def find_text(element: ET.Element, tag: str, ns: str = ""):
    """
    Obtiene el texto contenido en un subelemento XML.

    Parámetros
    ---------------------
        element - Elemento XML sobre el que realizar la búsqueda.
        tag - Nombre de la etiqueta a localizar.
        ns - Namespace utilizado por el documento XML.

    Devolución
    ---------------------
        str - Texto contenido en la etiqueta indicada. Si la etiqueta no existe devuelve una cadena vacía.
    """
    child = element.find(f"{ns}{tag}")
    if child is not None and child.text:
        return child.text.strip()
    return ""
def cargar_principios_activos(carpeta: Path):
    """
    Carga el diccionario de principios activos proporcionado por CIMA.

    Parámetros
    ---------------------
        carpeta - Ruta donde se encuentran los archivos XML de CIMA.

    Devolución
    ---------------------
        dict - Diccionario. clave: código del principio activo, valor: nombre correspondiente.
    """
    ruta = carpeta / "DICCIONARIO_PRINCIPIOS_ACTIVOS.xml"
    tree = ET.parse(ruta)
    root = tree.getroot()
    ns = get_ns(root)

    mapping = {}
    for pa in root.findall(f"{ns}principiosactivos"):
        # El campo que aparece en Prescripcion.xml es cod_principio_activo,
        # que coincide con nroprincipioactivo (entero)..
        nro = find_text(pa, "nroprincipioactivo", ns)
        nombre = find_text(pa, "principioactivo", ns)
        if nro:
            mapping[nro] = nombre
    return mapping
def cargar_formas_farmaceuticas(carpeta: Path):
    """
    Carga el diccionario de formas farmacéuticas de CIMA.

    Parámetros
    ---------------------
        carpeta - Ruta donde se encuentran los archivos XML de CIMA.

    Devolución
    ---------------------
        dict - Diccionario que relaciona el código de la forma farmacéutica con su descripción.
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
def cargar_situaciones_registro(carpeta: Path):
    """
    Carga el diccionario de situaciones de registro de CIMA.

    Parámetros
    ---------------------
        carpeta - Ruta donde se encuentran los archivos XML de CIMA.

    Devolución
    ---------------------
        dict - Diccionario que relaciona el código de situación de registro con su descripción.
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
    Procesa el archivo Prescripcion.xml de CIMA y construye un DataFrame con la información relevante de cada medicamento.

    Parámetros
    ---------------------
        carpeta - Ruta donde se encuentran los archivos XML de CIMA.

    Devolución
    ---------------------
        df - pandas.DataFrame con el nombre del medicamento, numero de registro, principios activos, codigos atc, forma farmaceutica y situacion de registro.
    """
    # Diccionarios necesarios
    print("Cargando diccionarios…")
    pa_dict   = cargar_principios_activos(carpeta)
    ff_dict   = cargar_formas_farmaceuticas(carpeta)
    sit_dict  = cargar_situaciones_registro(carpeta)

    # Fichero principal
    ruta_main = carpeta / "Prescripcion.xml"
    print(f"Parseando {ruta_main} (puede tardar unos segundos)…")

    # Usamos iterparse de nuevo
    registros = []
    # se detecta en el primer elemento
    ns_uri = None   

    context = ET.iterparse(str(ruta_main), events=("start", "end"))

    # diccionario del medicamento en curso
    current = None   

    for event, elem in context:
        # Detectamos namespace en el primer elemento raíz
        if ns_uri is None and event == "start":
            tag = elem.tag
            ns_uri = tag.split("}")[0] + "}" if tag.startswith("{") else ""

        tag_local = elem.tag.replace(ns_uri or "", "")

        if event == "start" and tag_local == "prescription":
            current = {
                "nombre_medicamento": "",
                "numero_registro": "",
                "principios_activos_raw": [],  
                "atc_raw": [],                 
                "forma_farmaceutica_cod": "",
                "situacion_registro_cod": "",
            }

        if event == "end" and current is not None:

            #nombre del medicamento
            if tag_local == "des_nomco":
                current["nombre_medicamento"] = (elem.text or "").strip()

            #numero de resgistro
            elif tag_local == "nro_definitivo":
                current["numero_registro"] = (elem.text or "").strip()

            #situacion del registro
            elif tag_local == "cod_sitreg":
                current["situacion_registro_cod"] = (elem.text or "").strip()

            # Forma farmacéutica: tomamos cod_forfar (no la simplificada)
            elif tag_local == "cod_forfar":
                if not current["forma_farmaceutica_cod"]:   # primer hallazgo
                    current["forma_farmaceutica_cod"] = (elem.text or "").strip()

            # Principios activos dentro de <composicion_pa>
            elif tag_local == "cod_principio_activo":
                current["principios_activos_raw"].append((elem.text or "").strip())

            # codigos ATC, que pueden ser varios
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

                #Añadimos 
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
    #Lo convertimos a df
    df = pd.DataFrame(registros, columns=[
        "nombre_medicamento",
        "numero_registro",
        "principios_activos",
        "codigo_atc",
        "forma_farmaceutica",
        "situacion_registro",
    ])
    #lo devolvemos
    return df

def csv_CIMA(carpeta, salida=None):
    """
    Genera un DataFrame con la información obtenida de CIMA y, opcionalmente, la guarda en un archivo CSV.

    Parámetros
    ---------------------
        carpeta - Ruta donde se encuentran los archivos XML de CIMA.
        salida - Ruta donde guardar el CSV generado. Si es None, únicamente devuelve el DataFrame.

    Devolución
    ---------------------
        df - pandas.DataFrame con la información procesada de CIMA.
    """
    carpeta = Path(carpeta)

    df = parsear_prescripcion(carpeta)

    if salida:
        df.to_csv(
            salida,
            index=False,
            encoding="utf-8-sig"
        )

    return df
    
#Separacion de bloques de medicamentos
def dividir_df(df, tamano):
    """
    Divide un DataFrame en varios bloques de tamaño fijo.

    Parámetros
    ---------------------
        df - DataFrame que se desea dividir.
        tamano - Número máximo de filas por bloque.

    Devolución
    ---------------------
        list - Lista de DataFrames con el tamaño especificado.
    """
    return [ df[i:i+tamano]
        for i in range(0, len(df), tamano)
    ]

#PDFs
def pdfs(carpeta, csv):
    """
    Descarga automáticamente las fichas técnicas en formato PDF de los medicamentos disponibles en CIMA.

    Para cada medicamento se intenta descargar la ficha técnica correspondiente a su número de registro. En caso de no existir, se prueban otros registros asociados al mismo principio activo.

    Parámetros
    ---------------------
        carpeta - Nombre de la carpeta donde se almacenarán los PDF descargados.
        csv - Ruta al archivo CSV que contiene los medicamentos y sus números de registro.

    Devolución
    ---------------------
        None
    """
    df = pd.read_csv(csv)
    
    # Carpeta destino
    carpeta_destino = os.path.join("D:\\", carpeta)

    os.makedirs(carpeta_destino, exist_ok=True)
    
    # Recorrer medicamentos únicos
    for fila in df.itertuples():
    
        drug_name = fila.drug_name
        numero_registro = fila.numero_registro
    
        # Lista de registros alternativos del mismo drug_name en total
        alternativas = total.loc[
            total["drug_name"] == drug_name,
            "numero_registro"
        ].drop_duplicates().tolist()
    
        # Poner primero el original
        registros_a_probar = [numero_registro] + [
            x for x in alternativas if x != numero_registro
        ]
    
        descargado = False
        #Para que no de errores de muchas requests (429)
        time.sleep(2)
    
        for reg in registros_a_probar:
    
            # URL
            url = f"https://cima.aemps.es/cima/pdfs/es/ft/{reg}/FT_{reg}.html.pdf"
    
            # Nombre archivo
            nombre_archivo = f"{drug_name}.pdf"
    
            ruta_archivo = os.path.join(carpeta_destino, nombre_archivo)
    
            try:
                print(f"Intentando {drug_name} - registro {reg}")
    
                response = requests.get(url, timeout=15)
                time.sleep(2)
    
                if response.status_code == 200:
    
                    with open(ruta_archivo, "wb") as f:
                        f.write(response.content)
    
                    print(f"Guardado en: {ruta_archivo}")
    
                    descargado = True
                    break
    
                else:
                    print(f"No encontrado ({response.status_code})")
    
            except Exception as e:
                print(f" -- Error: {e}")
    
        if not descargado:
            print(f" --------------> No se pudo descargar {drug_name}")
    
    print("\nProceso terminado.")