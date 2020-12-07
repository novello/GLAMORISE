from simple_sqllite import SimpleSQLLite
import json
from os import path
import sys
sys.path.append(path.abspath('../nalir-glamorise'))

from nalir import *

import nltk
#nltk.download('averaged_perceptron_tagger')
#nltk.download('wordnet')
#nltk.download('punkt')

# Simple class to act as a NLIDB
class NalirNlidb:

    config_json_text = '''{
    "connection":{
            "host": "localhost",
            "password":"desenvolvimento123",
            "user":"nalir",
            "database":"mas"
        },
        "loggingMode": "ERROR",
        "zfiles_path":"/home/novello/nalir-glamorise/zfiles",
        "jars_path":"/home/novello/nalir-glamorise/jars/new_jars"
    }
    '''

    def __init__(self):
        # open the database
        self.__SimpleSQLLite = SimpleSQLLite('./datasets/NaLIR.db')
   
    def field_synonym(self, synonym):
        # responsible for the translation of the field to the appropriated column
        try:
            sql = "SELECT field FROM NLIDB_FIELD_SYNONYMS WHERE synonym = '" + synonym + "'"
            field, cursor_description = (self.__SimpleSQLLite.execute_sql(sql, 'Field translated'))
            return list(field)[0][0]
        except:
            return synonym

    def execute_query(self, nlq):
        try:
            config = ConfigHandler(reset=True,config_json_text=NalirNlidb.config_json_text)
            rdbms = RDBMS(config)
            query = Query(nlq, rdbms.schema_graph)
            # Stanford Dependency Parser
            StanfordParser(query,config)

            # Node Mapper
            NodeMapper.phrase_process(query,rdbms,config)

            # Entity Resolution
            # The entity pairs denote that two nodes represente the same entity.
            entity_resolute(query)


            # Tree Structure Adjustor
            TreeStructureAdjustor.tree_structure_adjust(query,rdbms)

            # Explainer
            explain(query)

            # SQL Translator
            # **Important Node**: The error message is resultant of line 191 of file data_structure/block.py
            translate(query, rdbms)
            sql_result = query.translated_sql

            print('SQL Result NaLIR: ', sql_result)

            
            #result_set, cursor_description = self.__SimpleSQLLite.execute_sql(sql_result, 'Query executed')
            result_set = rdbms.conduct_sql(sql_result)
            # prepare the result set as JSON
            result_set = json.dumps(result_set)
            
            #column_names = (list(map(lambda x: x[0], cursor_description)))

            # internal data dictionary table of SQLite
            # sql = "SELECT name, type FROM PRAGMA_TABLE_INFO('ANP')"
            # column_types = self.__SimpleSQLLite.execute_sql(sql, 'Metadata collected')[0]
            # # prepare the column names and types as JSON
            # columns = json.dumps([(column_name, column_type[1])
            #                       for column_name in column_names
            #                         for column_type in column_types
            #                             if column_type[0] == column_name])
            # return columns, result_set
            return '[["AUTHOR", "TEXT"], ["CONFERENCE", "TEXT"]]', result_set
        except:
            print("Error processing NLQ: ", nlq)