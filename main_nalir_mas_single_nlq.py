#
# Developed by Alexandre Novello (PUC-Rio)
#

from glamorise_nlidb import GlamoriseNlidb
import main_common as mc
from os import path

token_path = path.abspath('./config/environment/nalir_tokens.xml')

with open('./config/environment/nalir_mas_db.json') as json_file:
    config_db = json_file.read()
        
with open('./config/environment/glamorise_nalir_mas.json') as json_file:
    patterns_json_txt = json_file.read()

jupyter = mc.is_jupyter_notebook()
glamorise = GlamoriseNlidb(NLIDB = 'NaLIR', patterns = patterns_json_txt, config_db = config_db, tokens = token_path)

nlq ='return me the author in the "University of Michigan" who have more than 5000 total citations.'

mc.print_results(glamorise, nlq)

mc.print_total_timers()
del glamorise    

