#
# Developed by Alexandre Novello (PUC-Rio)
#

from unittest import TestCase
import csv
from glamorise_mock_nlidb import GLAMORISEMockNLIDB


class TestGLAMORISE(TestCase):
    def test_GLAMORISE_methods(self):
        # set of questions to test
        with open('./datasets/pfp.csv', encoding="utf-8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';', quotechar="'")
            #jump the title line
            next(csv_reader)
            glamorise = GLAMORISEMockNLIDB()
            for row in csv_reader:
                #the NLQ is the first column of the CSV
                nl_query = row[0]
                glamorise.execute(nl_query)
                try:
                    # assert the NLQ generated by GLAMORISE to the NLIDB is equal to the expected value
                    # (second column of the CSV)
                    assert glamorise.prepared_query.lower() == row[1].lower()
                finally:
                    # print anyway, just for convenience (pytest cuts the string)
                    print('\nPrepared NLQ to NLIDB\nExpected: ', row[1].lower())
                    print('Actual:   ', glamorise.prepared_query.lower())
                try:
                    # assert the SQL generated by GLAMORISE is equal to the expected value
                    # (forth column of the CSV)
                    assert glamorise.sql.lower() == row[3].lower()
                finally:
                    # print anyway, just for convenience (pytest cuts the string)
                    print('\nGLAMORISE SQL\nExpected: ', row[3].lower())
                    print('Actual:   ', glamorise.sql.lower())
            csv_file.seek(1)
            print('{} NLQ questions tested'.format(sum(1 for line in csv_reader)))
