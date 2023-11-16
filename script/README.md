# statement_extraction

## About

Script for extracting annotations on secondary literature texts from INCEpTION with the purpose of feeding them into MimoTextBase (https://data.mimotext.uni-trier.de/wiki/Main_Page).


## Usage

### Prerequisites

The following packages need to be installed:
* dkpro-cassis
* pandas
* glob
* os
* re

Make sure that the input files are stored in a folder called "input" and create an empty folder "output".


### Input

* The annotated texts are exported from INCEpTION in **UIMA CAS XMI (XML 1.0)** format and passed as input to the script.
* The script requires a **XML typesystem file** which is contained in the INCEpTION exports.
* The script uses a matching file (**concepts_mimotextbase.tsv**) to get the french concept labels

### Output

After running the script the extracted information is stored in the output folder. For each input file a TSV statement file is created. Each row represents a statement and contains the following information:
* the statement subject (author or work): the annotated text snippet and the assigned ID
* the statement object: the annotated text snippet and MiMoTextBase ID and French label of the assigned concept
* the property
* the text snippet (one or more sentences containing the annotated strings)
