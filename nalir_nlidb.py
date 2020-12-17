from simple_sqllite import SimpleSQLLite
import json
from os import path
import sys
sys.path.append(path.abspath('../nalir-glamorise'))
from mysql.connector import FieldType
import re
import nltk
#nltk.download('averaged_perceptron_tagger')
#nltk.download('wordnet')
#nltk.download('punkt')


from nalir import *


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

    def __change_select(self):
        sql_list = self.__sql.split('\n')        
        result = re.search('(SELECT )(DISTINCT )?(.*)$', sql_list[0], re.IGNORECASE|re.MULTILINE)        
        select = ''
        fields = result.group(3).split(',')
        transformed_fields = []
        for field in fields:
            field = field.strip()
            transformed_fields.append(field + ' as ' + field.replace('.', '_').replace('(', '_').replace(')', ''))
        self.__sql = result.group(1) + result.group(2) + ', '.join(transformed_fields) + '\n'
        for i in range(1, len(sql_list)):
            self.__sql += sql_list[i] + '\n'

    def __translate_mysql_datatype_to_sqlite(self, type):
        field_type = {
                    'DECIMAL' : 'REAL',
                    'TINY' : 'REAL',
                    'SHORT' : 'REAL',
                    'LONG' : 'REAL',
                    'FLOAT' : 'REAL',
                    'DOUBLE' : 'REAL',
                    'NULL' : 'NULL',
                    'TIMESTAMP' : 'TEXT',
                    'LONGLONG': 'INTEGER',
                    'INT24': 'INTEGER',
                    'DATE' : 'TEXT',
                    'TIME' : 'TEXT',
                    'DATETIME' : 'TEXT',
                    'YEAR': 'INTEGER',
                    'NEWDATE' : 'TEXT',
                    'VARCHAR' : 'TEXT',
                    'BIT': 'INTEGER',
                    'JSON' : 'TEXT',
                    'NEWDECIMAL': 'REAL',
                    'ENUM' : 'TEXT',
                    'SET' : 'TEXT',
                    'TINY_BLOB' : 'BLOB',
                    'MEDIUM_BLOB' : 'BLOB',
                    'LONG_BLOB' : 'BLOB',
                    'BLOB' : 'BLOB',
                    'VAR_STRING' : 'TEXT',
                    'STRING' : 'TEXT',
                    'GEOMETRY' : 'TEXT'}
        return field_type[type]

   
    def field_synonym(self, synonym):
        # responsible for the translation of the field to the appropriated column
        try:
            sql = "SELECT field FROM NLIDB_FIELD_SYNONYMS WHERE synonym = '" + synonym + "'"
            field, cursor_description = (self.__SimpleSQLLite.execute_sql(sql, 'Field translated'))
            return list(field)[0][0]
        except:
            return synonym

    def execute_query(self, nlq, timer_nlidb_execution, timer_nlidb_json_result_set):   
        timer_nlidb_execution.start()     
        columns = result_set = self.__sql = ''
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
            self.__sql = query.translated_sql

            self.__change_select()            

            
            #result_set, cursor_description = self.__SimpleSQLLite.execute_sql(sql_result, 'Query executed')
            timer_nlidb_execution.stop()
            timer_nlidb_json_result_set.start()
            result_set, cursor_description = rdbms.conduct_sql(self.__sql)
            
            columns = (list(map(lambda x: [x[0], self.__translate_mysql_datatype_to_sqlite(FieldType.get_info(x[1]))], cursor_description)))
            
            columns = json.dumps(columns)
            # prepare the result set as JSON
            result_set = json.dumps(result_set)

            return columns, result_set, self.__sql
        except:
            print("Error processing NLQ in NaLIR: ", nlq)
            raise
        finally:
            return columns, result_set, self.__sql