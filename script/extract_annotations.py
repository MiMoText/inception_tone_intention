'''
Script for extracting annotations on secondary literature texts
from INCEpTION with the purpose of transferring them into statements
and feeding into MimoTextBase.
'''

# =======================
# Imports
# =======================
from cassis import *
import pandas as pd
import glob
import os
from os.path import join
import re

# =======================
# Files and folders
# =======================

datadir = ""
input_folder = join("input", "*.xmi")
output_folder = join("output", "")
typesystem_file = join("TypeSystem.xml")
concept_file = join("concepts_mimotextbase.tsv")


# =======================
# Functions
# =======================

def get_concept_mapping(concept_file):
    '''
    Takes file with concept labels and MiMoTextBase IDs.
    Returns it as a dictionary.
    '''
    with open(concept_file, "r", encoding="utf8") as infile:
        mapping = pd.read_csv(infile, sep="\t")
        mapping_dict = {}
        for index, row in mapping.iterrows():
            mapping_dict[row['concept']] = row['conceptLabel']
        return mapping_dict


def load_cas(typesystem_file, xmi_file):
    '''
    Loads Typesystem file and xmi_file.
    Returns it as a cas object.
    '''
    with open(typesystem_file, 'rb') as f:
        typesystem = load_typesystem(f)
    with open(xmi_file, 'rb') as f:
       cas = load_cas_from_xmi(f, typesystem=typesystem)
    return cas

def get_sentences(cas):
    '''
    Saves sentence information including begin, end and text into a dataframe.
    '''
    rows = []
    counter = 0
    for sentence in cas.select('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence'):
        #print(sentence.get_covered_text(), sentence.begin, sentence.end)
        rows.append({'id' : counter, 'begin' : sentence.begin, 'end' : sentence.end, 'text' : sentence.get_covered_text()})
        counter += 1 
    sentence_df = pd.DataFrame(rows)
    return sentence_df

def get_snippet(sentence_df, prop):
    '''
    Extracts the associated sentences to an annotated statement.
    '''
    annot_begin = min(prop.Governor.begin, prop.Dependent.begin)
    annot_end = max(prop.Governor.end, prop.Dependent.end)
    snippet = ""
    first_sentence = 0
    # get first sentence of annotation
    for ind in sentence_df.index:
        if annot_begin >= sentence_df['begin'][ind] and annot_begin <= sentence_df['end'][ind]:
            snippet = snippet + sentence_df['text'][ind]
            first_sentence = ind
            break
    
    # check for more sentences
    ind_sent = first_sentence + 1
    if not annot_end <= sentence_df['end'][first_sentence]:   # annotation covers only one sentence
        if annot_end <= sentence_df['end'][ind_sent]: # annotation covers two sentences
            snippet = snippet + " " + sentence_df['text'][ind_sent]
        else: # more than two sentences
            while annot_end > sentence_df['end'][ind_sent]:
                snippet = snippet + " " + sentence_df['text'][ind_sent]
                ind_sent += 1
            snippet = snippet + " " + sentence_df['text'][ind_sent + 1]
    
    snippet = re.sub('\r', '', snippet)
    snippet = re.sub('\n', ' ', snippet)
    return snippet
                
        
        
def extract_infos(cas, mapping_dict, sentence_df):
    '''
    Extracts statement informations from the cas object.
    Returns statements as dataframe.
    '''
    rows = []
    for prop in cas.select('webanno.custom.Property'):    # runs over all statements (property elements in xmi)
        # extract governor information = subject
        subject_id =  prop.Governor.identifier
        subject_snippet = prop.Governor.get_covered_text()
        # get property ID
        property = prop.propertyID
        # extract dependent information = object
        object_id =  prop.Dependent.identifier
        try:
            object_label = mapping_dict[object_id]  
        except:
            object_label = None
        object_snippet = prop.Dependent.get_covered_text()
        text_snippet = get_snippet(sentence_df, prop)
        rows.append({'subject_id' : subject_id, 'subject_snippet' : subject_snippet, 'property' : property, 'object_id' : object_id, 'object_label' : object_label, 'object_snippet' : object_snippet, 'snippet': text_snippet})
        
    
    df = pd.DataFrame(rows)
    return df


def df2tsv(df, basename, output_folder):
    '''
    Saves dataframe to tsv.
    '''
    filename = join(output_folder, basename + ".tsv") 
    with open(filename, "w", encoding="utf8", newline='\n') as outfile: 
        df.to_csv(outfile, sep="\t", index=False, header=True)
        
        
def main(concept_file, typesystem_file, input_folder, output_folder):
    mapping_dict = get_concept_mapping(concept_file)
    
    for file in glob.glob(input_folder):
        basename,ext = os.path.basename(file).split(".")
        print(basename)
        cas = load_cas(typesystem_file, file)
        sentence_df = get_sentences(cas)
        df = extract_infos(cas, mapping_dict, sentence_df)
        df2tsv(df, basename, output_folder)
    

main(concept_file, typesystem_file, input_folder, output_folder)