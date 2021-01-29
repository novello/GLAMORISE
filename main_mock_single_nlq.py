#
# Developed by Alexandre Novello (PUC-Rio)
#

from glamorise_nlidb import GlamoriseNlidb
import main_common as mc

with open('./config/environment/glamorise_mock.json') as json_file:
    config_glamorise = json_file.read()

with open('./config/environment/glamorise_interface_mock_anp.json') as json_file:
    config_glamorise_interface = json_file.read()    

glamorise = GlamoriseNlidb(config_glamorise_param = config_glamorise, config_glamorise_interface_param = config_glamorise_interface)
    
nlq = 'What was the average yearly production of oil in the state of Alagoas?'
mc.print_results(glamorise, nlq)

mc.print_total_timers()
del glamorise
