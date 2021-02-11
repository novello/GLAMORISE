#
# Developed by Alexandre Novello (PUC-Rio)
#

import os
import glob
from unittest import TestCase
import csv
from glamorise_nlidb import GlamoriseNlidb
from codetiming import Timer

with open('./config/environment/glamorise_mock.json') as json_file:
    patterns_json_txt = json_file.read()

class TestGlamorise(TestCase):
    def __delete_db_files(self):
        fileList = glob.glob('./datasets/glamorise_*.db')
        # Iterate over the list of filepaths & remove each file.
        for filePath in fileList:
            try:
                os.remove(filePath)
            except:
                print("Error while deleting file : ", filePath)

    def test_glamorise_methods(self):
        # set of questions to test
        with open('./nlqs/mock_nlidb_anp.nlqs.csv', encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';', quotechar="'")
            #jump the title line
            next(csv_reader)
            glamorise = GlamoriseNlidb(patterns = patterns_json_txt)
            for row in csv_reader:
                #the NLQ is the first column of the CSV
                nl_query = row[0]
                glamorise.execute(nl_query)
                try:
                    # assert the NLQ generated by GLAMORISE to the NLIDB is equal to the expected value
                    # (second column of the CSV)
                    assert glamorise.pre_prepared_query.lower() == row[1].lower()
                    print('passed!')
                finally:
                    # print anyway, just for convenience (pytest cuts the string)
                    print('\nPrepared NLQ to NLIDB\nExpected: ', row[1].lower())
                    print('Actual:   ', glamorise.pre_prepared_query.lower())
                try:
                    # assert the SQL generated by GLAMORISE is equal to the expected value
                    # (forth column of the CSV)
                    assert glamorise.pos_glamorise_sql.lower() == row[3].lower()
                    print('passed!')
                finally:
                    # print anyway, just for convenience (pytest cuts the string)
                    print('\nGLAMORISE SQL\nExpected: ', row[3].lower())
                    print('Actual:   ', glamorise.pos_glamorise_sql.lower())                    

                    glamorise.print_timers()
                    
                    
            for (key, value) in Timer.timers.items():
                print("total {} : {:.2f} sec".format(key, value))
            del glamorise                
            # for some reason the db files are not deleted in test mode
            # this method is to ensure they will be deleted
            self.__delete_db_files()
            csv_file.seek(1)
            print('{} NLQ questions tested'.format(sum(1 for line in csv_reader)))
