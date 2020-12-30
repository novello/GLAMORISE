#
# Developed by Alexandre Novello (PUC-Rio)
#

from glamorise_nlidb import GlamoriseNlidb
import main_common as mc
import csv
from codetiming import Timer

with open('./config/nalir_mas_local_db.json') as json_file:
    config_db = json_file.read()
        
with open('./config/glamorise_nalir_mas_test.json') as json_file:
    patterns_json_txt = json_file.read()

jupyter = mc.is_jupyter_notebook()
glamorise = GlamoriseNlidb(NLIDB = 'NaLIR', patterns = patterns_json_txt, config_db = config_db)

nlq ='return me the keyword, with the number of publications in VLDB conference.'

mc.print_results(glamorise, nlq)

mc.print_total_timers()
del glamorise    

