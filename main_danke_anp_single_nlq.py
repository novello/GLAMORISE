#
# Developed by Alexandre Novello (PUC-Rio)
#

from glamorise_nlidb import GlamoriseNlidb
import main_common as mc

with open('./config/environment/glamorise_danke.json') as json_file:
    config_glamorise = json_file.read()

with open('./config/environment/glamorise_interface_mock_danke_anp.json') as json_file:
    config_glamorise_interface = json_file.read()


# create GLAMORISE object (the child class is instantiated)
glamorise = GlamoriseNlidb(NLIDB='Danke', config_glamorise_param=config_glamorise,
                           config_glamorise_interface_param=config_glamorise_interface)

nlq = 'What was the mean gas production per month per field?'

mc.print_results(glamorise, nlq)

mc.print_total_timers()
del glamorise
