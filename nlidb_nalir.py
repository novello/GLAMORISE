from simple_sqlite import SimpleSQLite
import json
from os import path
import sys
with open('./config/environment/path.json') as json_file:
    json_path = json_file.read()
json_path = json.loads(json_path)
sys.path.append(path.abspath(json_path['nalir_relative_path']))
from mysql.connector import FieldType
import re
import nltk
import glamorise
#nltk.download('averaged_perceptron_tagger')
#nltk.download('wordnet')
#nltk.download('punkt')

from nlidb_base import NlidbBase
from nalir import *


# Simple class to act as a NLIDB
class NlidbNalir(NlidbBase):

    

    def __init__(self, config_db, token_path):
        super(NlidbNalir, self).__init__()
        # open the database        
        self.__config_db = config_db
        self.__tokens = token_path
        self.__config = ConfigHandler(reset=True,config_json_text=self.__config_db)
        self.__rdbms = RDBMS(self.__config)

    
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
        

    def translate_all_field_synonyms_in_nlq(self, nlidb_nlq, nlidb_interface_fields):    
        try:           
            if glamorise.config_glamorise_interface.get('nlidb_field_synonym'):
                    results = glamorise.config_glamorise_interface['nlidb_field_synonym']
            for key,value in results.items():
                if key in nlidb_nlq:
                    nlidb_nlq = nlidb_nlq.replace(key, value.replace(' ', '_').replace('.', '_'))
                    nlidb_interface_fields.append(value)            
            nlidb_interface_fields = list(dict.fromkeys(nlidb_interface_fields))
            return nlidb_nlq, nlidb_interface_fields  
        except Exception as e:
            print('Exception: ', e)
            return nlidb_nlq, nlidb_interface_fields  
            

    def __include_fields(self, additional_fields):
        # get all fields in the query created by the NLIDB
        fields, result, sql_list = self._get_fields_in_sql(self.__sql, '(SELECT )(DISTINCT )?(.*)$', 0, 3, ',') 
        # verify if these fields should be translated to more than one field. Eg: month -> year, month
        for i in range(len(fields)):
            field_sym = self._query_specific_synonym(fields[i])
            fields[i] = field_sym if field_sym else fields[i]
        # include the fields identified by GLAMORISE    
        fields = fields + additional_fields
        # remove duplicates
        fields = list(dict.fromkeys(fields))
        #rebuild sql
        self.__sql = result.group(1) + result.group(2) + ', '.join(fields) + '\n'
        for i in range(1, len(sql_list)):
            self.__sql += sql_list[i] + '\n'
        self.__sql =  self.__sql[0:-1]  

    def execute_query(self, nlq, timer_nlidb_execution_first_and_second_attempt, timer_nlidb_execution_third_attempt, timer_nlidb_json_result_set, nlidb_attempt_level, fields):           
        timer_nlidb_execution_first_and_second_attempt.start()     
        columns = result_set = self.__sql = ''
        self.__first_attempt_sql = self.__second_attempt_sql = self.__third_attempt_sql = ''
        try:            
            self.__sql = self.__run_query(nlq)
            self.__first_attempt_sql = self.__sql


            if self.__sql and nlidb_attempt_level > 1:                
                self.__include_fields(fields)
                self.__second_attempt_sql = self.__sql
                result_set, cursor_description = self.__rdbms.conduct_sql(self.__sql + ' LIMIT 5')
                columns = (list(map(lambda x: [x[0], self.__translate_mysql_datatype_to_sqlite(FieldType.get_info(x[1]))], cursor_description)))                            
                self.__sql = self._change_select(self.__sql, columns)
            
            timer_nlidb_execution_first_and_second_attempt.stop()
            

            if not result_set and nlidb_attempt_level == 3:            
                timer_nlidb_execution_third_attempt.start()
                previous_sql = self.__sql                
                self.__nlq_rebuild(fields)
                self.__third_attempt_sql = self.__sql
                result_set, cursor_description = self.__rdbms.conduct_sql(self.__sql + ' LIMIT 5')
                columns = (list(map(lambda x: [x[0], self.__translate_mysql_datatype_to_sqlite(FieldType.get_info(x[1]))], cursor_description)))                            
                self.__sql = self._change_select(self.__sql, columns)
                timer_nlidb_execution_third_attempt.stop()

            
            timer_nlidb_json_result_set.start()
            result_set, cursor_description = self.__rdbms.conduct_sql(self.__sql)
            columns = (list(map(lambda x: [x[0], self.__translate_mysql_datatype_to_sqlite(FieldType.get_info(x[1]))], cursor_description)))            
            columns = json.dumps(columns)
            # prepare the result set as JSON
            result_set = json.dumps(result_set)            
            timer_nlidb_json_result_set.stop()
        except Exception as e:
            print("Error processing NLQ in NaLIR: ", nlq)
            print("Exception: ", e)
        finally:             
            self.__sql = self.__sql.replace('\n', ' ')
            return columns, result_set, self.__sql, self.__first_attempt_sql, self.__second_attempt_sql, self.__third_attempt_sql

    def __run_query(self, nlq):        
        try:
            query = Query(nlq, self.__rdbms.schema_graph)
            # Stanford Dependency Parser
            StanfordParser(query,self.__config)            
            # Node Mapper
            NodeMapper.phrase_process(query,self.__rdbms,self.__config, tokens = self.__tokens)
            # Entity Resolution
            # The entity pairs denote that two nodes represente the same entity.
            entity_resolute(query)
            # Tree Structure Adjustor
            TreeStructureAdjustor.tree_structure_adjust(query,self.__rdbms)
            # Explainer
            explain(query)
            # SQL Translator
            # **Important Node**: The error message is resultant of line 191 of file data_structure/block.py
            translate(query, self.__rdbms)
            return query.translated_sql
        except Exception as e:
            print("Error processing NLQ in NaLIR: ", nlq)
            print("Exception: ", e)        

    def __nlq_rebuild(self, fields):
        try:
            nlq = "give me all " + " for each ".join(fields).replace(".", "_")
            new_sql = self.__run_query(nlq)             
            self.__sql = self.__join_sql(new_sql)            
        except Exception as e:
            print("Error processing second attempt of NLQ in NaLIR: ", nlq)
            print("Exception: ", e)      

    def __join_sql(self, new_sql):
        select_new_sql_fields, select_new_sql_result, new_sql_sql_list = self._get_fields_in_sql(new_sql, '(SELECT )(DISTINCT )?(.*)$', 0, 3, ',')
        from_new_sql_fields, from_new_sql_result, new_sql_sql_list = self._get_fields_in_sql(new_sql, '(FROM )(.*)$', 1, 2, ',')        

        select_fields, select_result, sql_list = self._get_fields_in_sql(self.__second_attempt_sql, '(SELECT )(DISTINCT )?(.*)$', 0, 3, ',')
        from_fields, from_result, sql_list = self._get_fields_in_sql(self.__second_attempt_sql, '(FROM )(.*)$', 1, 2, ',')
        where_fields, where_result, sql_list = self._get_fields_in_sql(self.__second_attempt_sql, '(WHERE )(.*)$', 2, 2, ' AND ')
        
        select_final_fields = list(dict.fromkeys(select_new_sql_fields + select_fields))
        from_final_fields = list(dict.fromkeys(from_new_sql_fields + from_fields))
        where_final_fields = list(dict.fromkeys(where_fields))

        select_str = "SELECT DISTINCT " + ', '.join(select_final_fields)
        from_str = "\nFROM " + ', '.join(from_final_fields)
        if where_final_fields:
            where_str = "\nWHERE " + ' AND '.join(where_final_fields)
            sql = select_str + from_str + where_str
        else:
            sql = select_str + from_str
        return sql


            
    
    
