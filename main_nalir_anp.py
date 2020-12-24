#
# Developed by Alexandre Novello (PUC-Rio)
#

from glamorise_nlidb import GlamoriseNlidb
import main_common as mc
import csv
from codetiming import Timer

token_path = '../nalir-glamorise/zfiles/tokens.anp.xml'

with open('./config/nalir_anp_local_db.json') as json_file:
    config_db = json_file.read()
        
with open('./config/glamorise_nalir_anp.json') as json_file:
    patterns_json_txt = json_file.read()

   
# create GLAMORISE object (the child class is instantiated)
glamorise = GlamoriseNlidb(NLIDB = 'NaLIR', patterns = patterns_json_txt, config_db = config_db, token_path = token_path)
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

