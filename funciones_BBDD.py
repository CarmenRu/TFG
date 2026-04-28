import xml.etree.ElementTree as ET
import pandas as pd

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