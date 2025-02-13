import xml.etree.ElementTree as ET
import yaml
import os
import json
from datetime import datetime

def create_output_folders():
    os.makedirs("output", exist_ok=True)
    os.makedirs("output/noids", exist_ok=True)

def load_config():
    with open("config.yaml", "r") as file:
        return yaml.safe_load(file)

def locate_indices(root, ns):
    return root.findall(".//*[@xml:id='Indices']", ns)[0]

def process_items(matching_elements, ns):
    indexitems = {}
    noids = []
    auth_types = []

    for item in matching_elements:
        item_id = item.attrib.get(f"{{{ns['xml']}}}id")
        ids = item.findall("tei:idno", ns)
        indexitems[item_id] = {}

        if not ids:
            noids.append(item_id)
        else:
            for id in ids:
                authority_source = id.attrib.get("type")
                authority_id = id.text

                if authority_source not in auth_types:
                    auth_types.append(authority_source)

                if authority_source and authority_id:
                    indexitems[item_id][authority_source] = authority_id

    return indexitems, noids, auth_types

def write_noids_log(itemtype, noids):
    with open(f"output/noids/{itemtype}_noids.txt", "w+", encoding="utf-8") as f:
        f.write("Items with no associated authority file:\n")
        if noids:
            for item in noids:
                f.write(f"{item},\n")
        else:
            f.write("None")
        print("List of missing authority files written successfully.")

def generate_beacon_files(indexitems, auth_types, header_data, itemtype):
    predicates = {}
    for item_key, item_data in indexitems.items():
        BEACON_predicates(item_key, item_data, predicates, auth_types)

    for authority in auth_types:
        write_BEACON_file(authority, itemtype, header_data, predicates)

def BEACON_predicates(item_key, item_data, predicates, authorities):
    for authority in authorities:
        try:
            predicate = f"{item_data[authority]}||{item_key}"
            predicates.setdefault(authority, []).append(predicate)
        except KeyError:
            pass

def write_BEACON_file(authority, itemtype, header_data, predicates, filename_template="output/BEACON_{itemtype}_{authority}.txt"):
    filename = filename_template.format(authority=authority, itemtype=itemtype)
    name = header_data['name']
    try:
        prefix = cfg['authority_urls'][authority]
    except:
        prefix = "url-not-given"
        print("Warning: BEACON malformed")
    target = header_data['target'] + cfg['item_types'][itemtype]
    contact = header_data['contact']
    message = header_data['message']
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    try:
        with open(filename, "w+", encoding="utf-8") as f:
            f.write(f"#FORMAT: BEACON\n#NAME: {name}\n#PREFIX: {prefix}\n#TARGET: {target}\n#CONTACT: {contact}\n#MESSAGE: {message}\n#RELATION: http://www.w3.org/2002/07/owl#sameAs\n#TIMESTAMP:{timestamp}\n\n")
            for item in predicates[authority]:
                f.write(f"{item}\n")
            print(f"{filename} written successfully.")
    except KeyError:
        print(f"No data found for authority '{authority}'. Skipping.")

def main():
    create_output_folders()
    cfg = load_config()
    header_data = cfg['header']
    idx_path = cfg['file_location']

    if not os.path.isfile(idx_path):
        print("No .xml file located.")
        return
    else:
        print(".xml file successfully located.")

    idx_lists = cfg['item_types'].keys()
    if isinstance(idx_lists, str):
        idx_lists = list(idx_lists)

    print("Parsing...")
    tree = ET.parse(idx_path)
    root = tree.getroot()
    ns = {"tei": "http://www.tei-c.org/ns/1.0", "xml": "http://www.w3.org/XML/1998/namespace"}
    div = locate_indices(root, ns)

    for itemtype in idx_lists:
        matching_elements = div.findall(f".//*[@type='{itemtype}']", ns)

        if not matching_elements:
            print(f"No elements found for type '{itemtype}'.")
            continue

        matching_elements = matching_elements[0]
        indexitems, noids, auth_types = process_items(matching_elements, ns)
        write_noids_log(itemtype, noids)
        generate_beacon_files(indexitems, auth_types, header_data, itemtype)

if __name__ == "__main__":
    main()
