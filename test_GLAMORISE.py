from unittest import TestCase
import csv
import GLAMORISE



class TestGLAMORISE(TestCase):
    def test_GLAMORISE_methods(self):
        with open('./datasets/pfp.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';', quotechar="'")
            next(csv_reader)
            for row in csv_reader:
                nl_query = row[0]
                glamorise = GLAMORISE.GLAMORISEMockNLIDB(nl_query)
                glamorise.prepare_query_to_NLIDB()
                assert glamorise.prepared_query.lower() == row[1].lower()
                glamorise.prepare_aggregate_SQL()
                print(glamorise.query)
                assert glamorise.sql.lower() == row[3].lower()
