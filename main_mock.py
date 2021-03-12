#
# Developed by Alexandre Novello (PUC-Rio)
#

from glamorise_nlidb import GlamoriseNlidb
import main_common as mc
import csv

with open('./config/environment/glamorise_mock.json') as json_file:
    config_glamorise = json_file.read()

with open('./config/environment/glamorise_interface_mock_danke_anp.json') as json_file:
    config_glamorise_interface = json_file.read()    

with open('./nlqs/mock_nlidb_anp.nlqs.csv', encoding="utf-8") as csv_file:
    # read the file with the NLQ questions
    csv_reader = csv.reader(csv_file, delimiter=';', quotechar="'")
    # jump title line
    next(csv_reader)
    line_count = 0
    # create GLAMORISE object (the child class is instantiated)
    glamorise = GlamoriseNlidb(config_glamorise_param = config_glamorise, config_glamorise_interface_param = config_glamorise_interface)
    for row in csv_reader:
        # the NLQ is the first column of the CSV
        nlq = row[0]        
        mc.print_results(glamorise, nlq)

    mc.print_total_timers()
    del glamorise

