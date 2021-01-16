#
# Developed by Alexandre Novello (PUC-Rio)
#

from glamorise_nlidb import GlamoriseNlidb
import main_common as mc
from codetiming import Timer
from os import path

token_path = path.abspath('./config/nalir_tokens.xml')

with open('./config/nalir_mas_local_db.json') as json_file:
    config_db = json_file.read()
        
with open('./config/glamorise_nalir_mas.json') as json_file:
    patterns_json_txt = json_file.read()

jupyter = mc.is_jupyter_notebook()
glamorise = GlamoriseNlidb(NLIDB = 'NaLIR', patterns = patterns_json_txt, config_db = config_db, tokens = token_path)
with open('./nlqs/nalir_mas_subset_modified.nlqs.txt', encoding="utf-8") as file:            
    # read the file with the NLQ questions
    lines = file.readlines()     
    line_count = 0
    # create GLAMORISE object (the child class is instantiated)#     
    for nlq in lines:    
        line_count += 1
        #if line_count < 13:
        #    continue        
        mc.print_results(glamorise, nlq)

    mc.print_total_timers()
    del glamorise    

