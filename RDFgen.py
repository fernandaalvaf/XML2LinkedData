from lxml import etree
import yaml
import os
import json
from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS, OWL, FOAF


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


# define namespaces
NAMESPACES = {
    "pdperson": "http://www.pessoadigital.pt/index/names#",
    "pdperiodical": "http://www.pessoadigital.pt/index/periodicals#",
    "pdpublication": "http://www.pessoadigital.pt/pub/",
    "crm": "http://www.cidoc-crm.org/cidoc-crm/",
    "viaf": "http://viaf.org/viaf/",
    "wd": "http://www.wikidata.org/entity/",
    "gnd": "http://d-nb.info/gnd/",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "owl": "http://www.w3.org/2002/07/owl#"
    }

# initialize RDF graph
g = Graph()

# convert dictionary content to namespace objects and bind them
NAMESPACE_OBJECTS = {prefix: Namespace(uri) for prefix, uri in NAMESPACES.items()}

for prefix, namespace in NAMESPACE_OBJECTS.items():
    g.bind(prefix, namespace)

PDP = NAMESPACE_OBJECTS["pdperson"]
CRM = NAMESPACE_OBJECTS["crm"]
VIAF = NAMESPACE_OBJECTS["viaf"]
FOAF = NAMESPACE_OBJECTS["foaf"]
OWL = NAMESPACE_OBJECTS["owl"]
WD = NAMESPACE_OBJECTS["wd"]
GND = NAMESPACE_OBJECTS["gnd"]

# parse the .xml file
print("parsing...")
tree = etree.parse(idx_path)
root = tree.getroot()

TEI_NAMESPACE = {"tei": "http://www.tei-c.org/ns/1.0",
                 "xml": "http://www.w3.org/XML/1998/namespace"}

# PERSONS

for person in root.xpath("//tei:listPerson/tei:person", namespaces=TEI_NAMESPACE):
    person_id = person.get(f"{{{TEI_NAMESPACE['xml']}}}id")
    person_uri = PDP[person_id] 
    
    # declare rdf:type as crm:E21_Person
    g.add((person_uri, RDF.type, CRM.E21_Person))

    # declare main name for rdfs:label
    main_name = person.xpath("tei:persName[@type='main']", namespaces=TEI_NAMESPACE)
    if main_name:
        #g.add((person_uri, RDFS.label, Literal(main_name[0].text))) # main_name > rdf:label
        g.add((person_uri, FOAF.name,Literal(main_name[0].text))) # main_name > foaf:name

    # declare viaf id (owl:sameAs)
    viaf_id = person.find("tei:idno[@type='viaf']", namespaces=TEI_NAMESPACE)
    if viaf_id is not None:
        g.add((person_uri, OWL.sameAs, VIAF[viaf_id.text]))  

    # declare wikidata id (owl:sameAs)
    wd_id = person.find("tei:idno[@type='wd']", namespaces=TEI_NAMESPACE)
    if wd_id is not None:
        g.add((person_uri, OWL.sameAs, WD[wd_id.text]))  

    # declare gnd id (owl:sameAs)
    gnd_id = person.find("tei:idno[@type='gnd']", namespaces=TEI_NAMESPACE)
    if gnd_id is not None:
        g.add((person_uri, OWL.sameAs, GND[gnd_id.text]))
    
    # declare gender (foaf:gender)
    sex = person.find("tei:sex", namespaces=TEI_NAMESPACE)
    if sex is not None:
        g.add((person_uri, FOAF.gender, Literal(sex.text)))

    # status check
    print(f"Processed: {person_id} → {main_name[0].text if main_name else 'No Name'}")

# Save RDF output in multiple formats
g.serialize(destination="output/output.ttl", format="turtle")
g.serialize(destination="output/output.rdf", format="xml")