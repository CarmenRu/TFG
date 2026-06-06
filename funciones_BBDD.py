import xml.etree.ElementTree as ET
import pandas as pd

def csv_enzimas(output_file, xml_file):
    
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

    Retorna:
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