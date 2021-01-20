#
# Developed by Alexandre Novello (PUC-Rio)
#

from glamorise_nlidb import GlamoriseNlidb
import main_common as mc
from os import path
from xml.etree.ElementTree import fromstring

with open('./config/nalir_tokens.xml') as xml_file:
    nalir_tokens = xml_file.read()
    nalir_tokens = fromstring(nalir_tokens)

with open('./config/nalir_anp_local_db.json') as json_file:
    config_db = json_file.read()
        
with open('./config/glamorise_nalir_anp.json') as json_file:
    patterns_json_txt = json_file.read()

  
# create GLAMORISE object (the child class is instantiated)
glamorise = GlamoriseNlidb(NLIDB = 'NaLIR', patterns = patterns_json_txt, config_db = config_db, tokens = nalir_tokens)

nlq = 'return me the average oil production per field in the state of Rio de Janeiro'    

mc.print_results(glamorise, nlq)

mc.print_total_timers()
del glamorise    

