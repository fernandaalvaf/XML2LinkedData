# BEACON & RDF Generator

XML2LinkedData is a Python-based tool for generating BEACON and RDF link dumps from structured data sources.

This repository contains two Python scripts, `BEACONgen.py` and `RDFgen.py`, designed to process XML index data and generate BEACON and RDF output files for structured data representation. The repository also contains a jupyter notebook `BEACONgenNotebook.ipynb` with a guided overview of the script.

## Table of Contents
- [Overview](#overview)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [BEACON Generator](#beacon-generator)
  - [RDF Generator](#rdf-generator)
- [Configuration](#configuration)
- [Output](#output)
- [License](#license)

## Overview
- **BEACONgen.py**: Extracts structured index data from an XML file and generates BEACON files with authority references.
- **RDFgen.py**: Processes the same XML file and converts the data into RDF format for use in semantic web applications.

Both scripts rely on an external `config.yaml` file for settings such as XML file location, item types, and authority sources.

## Requirements
Ensure you have the following dependencies installed:
- Python 3.x
- `PyYAML`
- `lxml`
- `rdflib`

## Installation
1. Clone this repository:
```sh
git clone https://github.com/fernandaalvaf/XML2LinkedData.git
cd XML2LinkedData
```
2. Edit the content of the `config.yaml` file accordingly, it should be in the root directory.
3. Ensure the required XML index file is accessible.

## Usage

### BEACON Generator
To generate BEACON files, run:
```sh
python BEACONgen.py
```
This script:
- Reads the XML file and extracts index data.
- Generates BEACON files for each authority type.
- Logs missing authority references.


## Configuration
Modify `config.yaml` to specify:
- XML file location (`file_location`)
- Item types (`item_types`)
- Header information (`header`)

Example `config.yaml`:

```yaml
file_location: "Data/indices.xml"

register_types: {'names': {
                    'element': 'listPerson',
                    'attribute_type': 'type',
                    'attribute_value': 'all',
                    'target': 'http://www.pessoadigital.pt/index/names#'},
                'periodicals': {
                    'element': 'list',
                    'attribute_type': 'type',
                    'attribute_value': 'periodical',
                    'target':'http://www.pessoadigital.pt/index/periodicals#'},
                'publications': {
                    'element': 'list',
                    'attribute_type': 'type',
                    'attribute_value': 'publications',
                    'target': 'http://www.pessoadigital.pt/pub/'}
                    }

header_data: {'name' : 'Digital Edition of Fernando Pessoa',
        'contact' : 'Ulrike Henny-Krahmer <email>',
        'message' : 'Mentions in the digital edition of Fernando Pessoa',
        }

authority_files: {'wikidata': 'https://www.wikidata.org/wiki/',
                'viaf': 'http://viaf.org/viaf/',
                'gnd': 'http://d-nb.info/gnd/'
                }

namespaces: {"tei":"http://www.tei-c.org/ns/1.0",
            "xml":"http://www.w3.org/XML/1998/namespace"
            }

```

**File locations:** Defines the path of the XML file containing the project index data.

**Register types:** Specifies element names and attributes where the index is stored in the tei file, for example `<list type="places">`. If there is no specified attribute, the value of `attribute_type` and `attribute_value` should be `None`, for example in the case of: `<listPlaces>`.

**Header data:** Contains the optional metadata for the generated BEACON file. If it should be empty, input an empty string: `''`.

**Authority files:** Defines the external sources for entity validation (e.g., Wikidata, VIAF, GND).

**Namespaces:** Defines XML namespaces for parsing TEI-compliant files. In most cases, should not be altered.

## Output
Generated files are stored in the `output/` directory:
- **BEACONgen.py**: `output/BEACON_{itemtype}_{authority}.txt`

## License
This project is licensed under the MIT License. See `LICENSE` for details.
