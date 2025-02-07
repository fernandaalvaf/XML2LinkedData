# BEACON & RDF Generator

This repository contains two Python scripts, `BEACONgen.py` and `RDFgen.py`, designed to process XML index data and generate BEACON and RDF output files for structured data representation.

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

### RDF Generator
To generate RDF data, run:
```sh
python RDFgen.py
```
This script:
- Parses the XML index data.
- Converts it into RDF format.
- Outputs the data in both Turtle (`.ttl`) and RDF/XML (`.rdf`) formats.

## Configuration
Modify `config.yaml` to specify:
- XML file location (`file_location`)
- Item types (`item_types`)
- Header information (`header`)

Example `config.yaml`:
```yaml
file_location: "indices.xml"
item_types: {'all' : 'index/names#',
          'periodical' : 'index/periodicals#',
          'publications' : 'pub/'}
header: {'name' : 'Digital Edition of Fernando Pessoa',
        'target' : 'http://www.pessoadigital.pt/',
        'contact' : 'Ulrike Henny-Krahmer <email>',
        'message' : 'Mentions in the digital edition of Fernando Pessoa',
        }
```

## Output
Generated files are stored in the `output/` directory:
- **BEACONgen.py**: `output/BEACON_{itemtype}_{authority}.txt`
- **RDFgen.py**: `output/output.ttl`, `output/output.rdf`

## License
This project is licensed under the MIT License. See `LICENSE` for details.
