#
# Developed by Alexandre Novello (PUC-Rio)
#

from glamorise_nlidb import GlamoriseNlidb
import main_common as mc
from xml.etree.ElementTree import fromstring

with open('./config/environment/nalir_tokens.xml') as xml_file:
    nalir_tokens = xml_file.read()
    nalir_tokens = fromstring(nalir_tokens)

with open('./config/environment/nalir_mas_db.json') as json_file:
    config_db = json_file.read()

with open('./config/environment/glamorise_nalir.json') as json_file:
    config_glamorise = json_file.read()

with open('./config/environment/glamorise_interface_nalir_mas.json') as json_file:
    config_glamorise_interface = json_file.read()

jupyter = mc.is_jupyter_notebook()
glamorise = GlamoriseNlidb(NLIDB='NaLIR', config_glamorise_param=config_glamorise,
                           config_glamorise_interface_param=config_glamorise_interface, config_db=config_db, tokens=nalir_tokens)

nlq = 'return me the total citations of papers in PVLDB before 2005.'

mc.print_results(glamorise, nlq)

mc.print_total_timers()
del glamorise
