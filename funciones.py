import xml.etree.ElementTree as ET
import pandas as pd

def parsear_drugbank(xml_file, output_file):
    
    ns = "{http://www.drugbank.ca}"
    
    rows = []
    
    context = ET.iterparse(xml_file, events=("end",))
    
    for event, elem in context:
        if elem.tag == ns + "drug":
    
            # -------- ID --------
            drug_id_elem = elem.find(ns + 'drugbank-id[@primary="true"]')
            if drug_id_elem is None:
                elem.clear()
                continue
    
            drug_id = drug_id_elem.text
    
            # -------- NOMBRE --------
            name_elem = elem.find(ns + "name")
            drug_name = name_elem.text if name_elem is not None else ""
    
            # -------- SINÓNIMOS --------
            synonyms_list = []
            for syn in elem.findall(ns + "synonyms/" + ns + "synonym"):
                if syn.text:
                    synonyms_list.append(syn.text)
    
            synonyms = "|".join(synonyms_list)  # separados por |
    
            # -------- TARGETS --------
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
    
            # -------- ENZYMES --------
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
    
    # -------- DATAFRAME --------
    df = pd.DataFrame(rows, columns=[
        "drugbank_id",
        "drug_name",
        "synonyms",
        "type",
        "gene_name",
        "uniprot_id",
        "action"
    ])
    
    # -------- GUARDAR --------
    df.to_csv(output_file, index=False)
    
    print(f"Archivo guardado como: {output_file}")