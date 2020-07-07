from unittest import TestCase
import csv
from GLAMORISE import GLAMORISEMockNLIDB



class TestGLAMORISE(TestCase):
    def test_GLAMORISE_methods(self):
        with open('./datasets/pfp.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';', quotechar="'")
            next(csv_reader)
            for row in csv_reader:
                nl_query = row[0]
                glamorise = GLAMORISEMockNLIDB(nl_query)
                try:
                    assert glamorise.prepared_query.lower() == row[1].lower()
                finally:
                    print('\nPrepared NLQ to NLIDB\nExpected: ', row[1].lower())
                    print('Actual:   ', glamorise.prepared_query.lower())
                try:
                    assert glamorise.sql.lower() == row[3].lower()
                finally:
                    print('\nGLAMORISE SQL\nExpected: ', row[3].lower())
                    print('Actual:   ', glamorise.sql.lower())
