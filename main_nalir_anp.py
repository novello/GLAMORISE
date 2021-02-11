#
# Developed by Alexandre Novello (PUC-Rio)
#

from glamorise_nlidb import GlamoriseNlidb
import main_common as mc
import csv
from codetiming import Timer
from xml.etree.ElementTree import fromstring

with open('./config/environment/nalir_tokens.xml') as xml_file:
    nalir_tokens = xml_file.read()
    nalir_tokens = fromstring(nalir_tokens)

with open('./config/environment/nalir_anp_db.json') as json_file:
    config_db = json_file.read()
        
with open('./config/environment/glamorise_nalir.json') as json_file:
    patterns_json_txt = json_file.read()

   
# create GLAMORISE object (the child class is instantiated)
glamorise = GlamoriseNlidb(NLIDB = 'NaLIR', patterns = patterns_json_txt, config_db = config_db, tokens = nalir_tokens)
with open('./nlqs/nalir_anp.nlqs.txt', encoding="utf-8") as file:            
    # read the file with the NLQ questions
    lines = file.readlines()     
    line_count = 0
    # create GLAMORISE object (the child class is instantiated)#     
    for nlq in lines:    
        line_count += 1                                             
        mc.print_results(glamorise, nlq)

    mc.print_total_timers()
    del glamorise  

