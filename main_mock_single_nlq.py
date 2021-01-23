#
# Developed by Alexandre Novello (PUC-Rio)
#

from glamorise_nlidb import GlamoriseNlidb
import main_common as mc

with open('./config/environment/glamorise_mock.json') as json_file:
    patterns_json_txt = json_file.read()

glamorise = GlamoriseNlidb(patterns = patterns_json_txt)
    
nlq = 'What was the average yearly production of oil in the state of Alagoas?'
mc.print_results(glamorise, nlq)

mc.print_total_timers()
del glamorise
