import xml.etree.ElementTree as ET
import yaml
import os
from datetime import datetime


# check if output folder exists and create it if it does not
os.makedirs("output", exist_ok=True)
os.makedirs("output/noids", exist_ok=True)


# read settings from the config.yaml
with open ("config.yaml", "r") as file:
    cfg = yaml.safe_load(file)


# read header data settings
header_data = cfg['header_data']


# define and validate config dat
idx_path = cfg['file_location'] # path of the xml file
if not os.path.isfile(idx_path):
    print("No .xml file located.")
    exit()
else:
    print(f"{idx_path} file successfully located.")

class LinkedPair():
    def __init__(self, local_id, authority_id, authority_label):
        self.local_id = local_id
        self.authority_id = authority_id
        self.authority_label = authority_label

    def paired_entities(self):
        
        return f"{self.authority_id}||{self.local_id}"

    def show_pair(self):
        pair = self.paired_entities()
        print(pair)


class LinkedCollection():
    
    
    def __init__(self, register_data, register_type, authority_data):
        self.register_data = register_data
        self.register_type = register_type
        self.authority_data = authority_data
        self.data = {}
    

    def add_linkedpair(self, local_id, authority_id, authority_type):
        prefix = self.authority_data[f'{authority_type}']
                
        if authority_id.startswith(prefix):
            authority_id =authority_id[len(prefix)::]
            
        new_pair = LinkedPair(local_id, authority_id,authority_type)
        if authority_type not in self.data:
            self.data[authority_type] = []  
        self.data[authority_type].append(new_pair)  


    def show_pairs(self):
        for key, value in self.data.items():  
            for pair in value: 
                print(f"  {pair.paired_entities()}")


    def show_authority_types(self):
        all_auths = list(self.data.keys())
        print(all_auths)

    def write_BEACON(self):
            for key, value in self.data.items():  
                authority_label = key
                filename= f"output/BEACON_{self.register_type}_{authority_label}.txt"
                name = header_data['name']
                target = self.register_data['target']
                prefix = self.authority_data[f'{key}']
                contact= header_data['contact']
                message = header_data['message']
                timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                with open(filename, "w+", encoding="utf-8") as f:
                    f.write(f"#FORMAT: BEACON\n#NAME: {name}\n#PREFIX: {prefix}\n#TARGET: {target}\n#CONTACT: {contact}\n#MESSAGE: {message}\n#RELATION: http://www.w3.org/2002/07/owl#sameAs\n#TIMESTAMP:{timestamp}\n\n")
                    for pair in value:
                        f.write(f"{pair.paired_entities()}\n")
                    print(f"{filename} written successfully.")


def save_log(register_type,missing_authority):
    """ Creates a log of all items with no authority file associated to them.
    :param register_type: type of register being processed, ex. Names.
    :param missing_authority: list of entities with missing authority files.
    """

    with open(f"output/noids/{register_type}_noids.txt","w+", encoding="utf-8") as f:
        f.write("items with no associated authority file:\n")
        if missing_authority:
            for item in missing_authority:
                f.write("%s,\n" %item)
        else:
            f.write("None")
        print("list of misisng authority files written successfully.")


def iter_items(tei_list):
    """ Iterates over all entities in a given tei:list

    :param tei_list: tei list element that contains all entities of a register
    :param missing_authority: list of entities with missing authority files.
    """

    for child in tei_list:
        project_id = child.attrib[f"{{{ns['xml']}}}id"]
        
        
        authority_ids = child.findall("tei:idno", ns)
        if not authority_ids:
            authority_id = None
            missing_authority.append(project_id)
            
        else:
            for authority_id in authority_ids:
                if multiple_auth_types is True:
                    authority_type = authority_id.attrib["type"]
                else:
                    authority_type = next(iter(authority_data))

                if authority_type not in list(authority_data.keys()):
                    print(f'Some authority types might be wrong: check "{project_id}": "{authority_type}"')
                else:
                    collection.add_linkedpair(project_id,authority_id.text,authority_type)


# parse the .xml file
print("parsing...")
tree = ET.parse(idx_path)
root = tree.getroot()

# define namespaces
ns = cfg['namespaces']

authority_data = cfg['authority_files']

if len(authority_data) > 1:
    multiple_auth_types = True
else:
    multiple_auth_types = False


for register_type in cfg['register_types']:
    
    
    register = cfg['register_types'][register_type]
    missing_authority = []

    print(f'extracting info about "{register_type}"')
    collection = LinkedCollection(register, register_type, authority_data)

    if register['attribute_type'] == 'None':

        tei_list = root.find(f".//tei:{register['element']}", ns)
        iter_items(tei_list,missing_authority)
            
            
    else:
        tei_list = root.find(f".//tei:{register['element']}[@{register['attribute_type']}='{register['attribute_value']}']", ns)
        iter_items(tei_list)

    # collection.show_pairs()
    collection.write_BEACON()
    save_log(register_type,missing_authority)
    

            
            
