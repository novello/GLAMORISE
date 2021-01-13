#
# Developed by Alexandre Novello (PUC-Rio)
#

from glamorise_nlidb import GlamoriseNlidb
import main_common as mc


with open('./config/nalir_anp_local_db.json') as json_file:
    config_db = json_file.read()
        
with open('./config/glamorise_nalir_anp.json') as json_file:
    patterns_json_txt = json_file.read()

  
# create GLAMORISE object (the child class is instantiated)
glamorise = GlamoriseNlidb(NLIDB = 'NaLIR', patterns = patterns_json_txt, config_db = config_db)

nlq = 'return me the average oil production per field in the state of Rio de Janeiro'    

mc.print_results(glamorise, nlq)

mc.print_total_timers()
del glamorise    

