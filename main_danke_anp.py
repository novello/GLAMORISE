#
# Developed by Alexandre Novello (PUC-Rio)
#

from glamorise_nlidb import GlamoriseNlidb
import main_common as mc
from codetiming import Timer

with open('./config/environment/glamorise_danke.json') as json_file:
    config_glamorise = json_file.read()

with open('./config/environment/glamorise_interface_mock_danke_anp.json') as json_file:
    config_glamorise_interface = json_file.read()


# create GLAMORISE object (the child class is instantiated)
glamorise = GlamoriseNlidb(NLIDB='Danke', config_glamorise_param=config_glamorise,
                           config_glamorise_interface_param=config_glamorise_interface)
with open('./nlqs/anp.nlqs.txt', encoding="utf-8") as file:
    # read the file with the NLQ questions
    lines = file.readlines()
    line_count = 0
    # create GLAMORISE object (the child class is instantiated)#
    for nlq in lines:
        line_count += 1
        mc.print_results(glamorise, nlq)

    mc.print_total_timers()
    del glamorise
