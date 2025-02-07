import xml.etree.ElementTree as ET
import yaml
import os
import json
from datetime import datetime


def BEACON_predicates(item_key, item_data, predicates, authorities):
    """
    Processes a single index item and appends formatted URLs to predicates.
    
    :param item_key: Key of the current item (e.g., 'FP')
    :param item_data: Dictionary of authority IDs for the item (e.g., {'viaf': '29010497'})
    :param predicates: Dictionary to store processed URLs for each authority
    :param authorities: list of authorities
    """

    for authority in authorities:
        try:            
            
            predicate = f"{item_data[authority]}||{item_key}"
            #print(predicate)
            if authority not in predicates:
                predicates[authority] = []
            predicates[authority].append(predicate)
        except KeyError:
            # Skip if the authority ID is missing
            pass


def write_BEACON_file(authority, itemtype, header_data, predicates, filename_template="output/BEACON_{itemtype}_{authority}.txt"):
    """
    Writes a BEACON file for a given authority.

    :param authority: The key representing the authority (e.g., 'wiki', 'viaf', 'gnd')
    :param predicates: The dictionary containing data for all authorities
    :param filename_template: A template for the output file name (default: "BEACON_{authority}.txt")
    """
    filename = filename_template.format(authority=authority,itemtype=itemtype)
    name = header_data['name']
    target = header_data['target'] + cfg['item_types'][itemtype]
    contact= header_data['contact']
    message = header_data['message']
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    try:
        with open(filename, "w+", encoding="utf-8") as f:
            f.write(f"#FORMAT: BEACON\n#NAME: {name}\n#TARGET: {target}\n#CONTACT: {contact}\n#MESSAGE: {message}\n#RELATION: http://www.w3.org/2002/07/owl#sameAs\n#TIMESTAMP:{timestamp}\n\n")
            for item in predicates[authority]:
                f.write(f"{item}\n")
            print(f"{filename} written successfully.")
    except KeyError:
        print(f"No data found for authority '{authority}'. Skipping.")


# read settings from the config.yaml
with open ("config.yaml", "r") as file:
    cfg = yaml.safe_load(file)

# read header data settings
header_data = cfg['header']

# define and validate config dat
idx_path = cfg['file_location'] # path of the xml file
if not os.path.isfile(idx_path):
    print("No .xml file located.")
    exit()
else:
    print(".xml file successfully located.")

idx_lists = cfg['item_types'].keys() # defined list of indices
if type(idx_lists) is str:
    idx_lists = list(idx_lists)

# parse the .xml file
print("parsing...")
tree = ET.parse(idx_path)
root = tree.getroot()

# define namespaces
ns = {"tei":"http://www.tei-c.org/ns/1.0",
      "xml":"http://www.w3.org/XML/1998/namespace"}

# create container to define authority file types
auth_types = []

# locate indices in the tree
div = root.findall(".//*[@xml:id='Indices']", ns)[0]

# Iterating through indices

for itemtype in idx_lists:
    
    # Locate all parent elements (e.g., <list>, <listPerson>, etc.) that match the type
    matching_elements = div.findall(f".//*[@type='{itemtype}']", ns)

    if not matching_elements:
        print(f"No elements found for type '{itemtype}'.")
        continue
    else:
        # Access the first (and only) parent element from the list
        matching_elements = matching_elements[0]

    indexitems = {}
    noids = []

    # Iterate over the children of the parent element
    for item in matching_elements:

        # Use the namespace dictionary to access the xml:id attribute, this is the project internal id of this item
        item_id = item.attrib.get(f"{{{ns['xml']}}}id")
        #print(f"item...\nitem id: {item_id}")

        # find all <idno> children element given in this item
        ids = item.findall("tei:idno",ns)
        #print(ids)

        indexitems[item_id] = {}

        if len(ids) == 0:
            # if there is none, we do not need to store this item
            #print("no ids available")
            noids.append(item_id)
        else:
            # iterate through all given idno's
            for id in ids:
                # identify the source (e.g. wikidata, gnd) and id
                authority_source = id.attrib.get("type") # source
                authority_id = id.text # id

                # add to list of authority files if not already stored
                if authority_source not in auth_types:
                    auth_types.append(authority_source)
                
                # store in the dictionary along with the id itself
                if authority_source and authority_id:  # Ensure both source and ID are not None
                    indexitems[item_id][authority_source] = authority_id

    # Create a log of all items with no authority file associated to them
    with open(f"output/noids/{itemtype}_noids.txt","w+", encoding="utf-8") as f:
        f.write("items with no associated authority file:\n")
        if noids:
            for item in noids:
                f.write("%s,\n" %item)
        else:
            f.write("None")
        print("list of misisng authority files written successfully.")

    # Now we generate a BEACON file for each of the authority file types and each of the indices
    predicates = {}

    # Process all index items
    for item_key, item_data in indexitems.items():
        #print(item_key, item_data)
        BEACON_predicates(item_key, item_data, predicates, auth_types)

    # write BEACON
    for authority in auth_types:
        write_BEACON_file(authority, itemtype, header_data, predicates)
