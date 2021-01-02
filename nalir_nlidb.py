from simple_sqlite import SimpleSQLite
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

    

    def __init__(self, config_db, token_path):
        # open the database
        self.__SimpleSQLite = SimpleSQLite('./datasets/nalir_mas.db')
        self.__config_db = config_db
        self.__token_path = token_path
        self.__config = ConfigHandler(reset=True,config_json_text=self.__config_db)
        self.__rdbms = RDBMS(self.__config)

    def __change_select(self):
        fields, result, sql_list = self.__get_fields_in_sql(self.__sql, '(SELECT )(DISTINCT )?(.*)$', 0, 3, ',')
        all_fields = []
        transformed_fields = []        
        for field in fields:            
            if field not in all_fields:            
                all_fields.append(field)
                transformed_fields.append(field + ' as ' + field.replace('.', '_').replace('(', '_').replace(')', ''))
        self.__sql = result.group(1) + result.group(2) + ', '.join(transformed_fields) + '\n'
        for i in range(1, len(sql_list)):
            self.__sql += sql_list[i] + '\n'

    def __get_fields_in_sql(self, sql, regex, sql_list_position, group_num, separator):
        sql_list = sql.split('\n')
        result = re.search(regex, sql_list[sql_list_position], re.IGNORECASE|re.MULTILINE)        
        fields_str = result.group(group_num)
        fields = [x.strip() for x in fields_str.split(separator)]
        return fields, result, sql_list

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
            sql = "SELECT field FROM NLIDB_FIELD_SYNONYMS WHERE lower(synonym) = '" + synonym.lower().replace(' ', '_').replace('.', '_') + "'"
            field, cursor_description = self.__rdbms.conduct_sql(sql)
            return list(field)[0][0].replace(' ', '_').replace('.', '_')
        except Exception as e:
            return synonym
            #print('Exception: ', e)

    def translate_all_field_synonyms_in_sql(self, nlidb_nql, nlidb_interface_fields):    
        try:            
            sql = "SELECT synonym, field FROM NLIDB_FIELD_SYNONYMS"
            results, cursor_description = self.__rdbms.conduct_sql(sql)            
            for line in results:
                if line[0] in nlidb_nql:
                    nlidb_nql = nlidb_nql.replace(line[0], line[1].replace(' ', '_').replace('.', '_'))
                    nlidb_interface_fields.add(line[1])            
            return nlidb_nql  
        except Exception as e:
            return nlidb_nql
            #print('Exception: ', e        

    def __include_fields(self, nlidb_interface_fields):
        fields, result, sql_list = self.__get_fields_in_sql(self.__sql, '(SELECT )(DISTINCT )?(.*)$', 0, 3, ',')        
        for nlidb_interface_field in nlidb_interface_fields:            
            if nlidb_interface_field not in fields:            
                fields.append(nlidb_interface_field)                
        self.__sql = result.group(1) + result.group(2) + ', '.join(fields) + '\n'
        for i in range(1, len(sql_list)):
            self.__sql += sql_list[i] + '\n'

    def execute_query(self, nlq, timer_nlidb_execution_first_and_second_attempt, timer_nlidb_execution_third_attempt, timer_nlidb_json_result_set, nlidb_attempt_level, nlidb_interface_fields):   
        timer_nlidb_execution_first_and_second_attempt.start()     
        columns = result_set = self.__sql = ''
        self.__sql_first_attempt = self.__sql_second_attempt = self.__sql_third_attempt = ''
        try:            
            self.__sql = self.__run_query(nlq)
            self.__sql_first_attempt = self.__sql


            if self.__sql:
                if nlidb_attempt_level > 1:
                    self.__include_fields(nlidb_interface_fields)
                    self.__sql_second_attempt = self.__sql

                self.__change_select()            
            
            #result_set, cursor_description = self.__SimpleSQLite.execute_sql(sql_result, 'Query executed')
            timer_nlidb_execution_first_and_second_attempt.stop()
            timer_nlidb_json_result_set.start()
            result_set, cursor_description = self.__rdbms.conduct_sql(self.__sql)

            if not result_set and nlidb_attempt_level == 3:            
                timer_nlidb_json_result_set.stop()
                timer_nlidb_execution_third_attempt.start()
                prior_sql = self.__sql
                self.__nlq_rebuild(nlidb_interface_fields)
                self.__sql_third_attempt = self.__sql
                self.__change_select()
                if self.__sql != prior_sql:
                    result_set, cursor_description = self.__rdbms.conduct_sql(self.__sql)                 
                timer_nlidb_execution_third_attempt.stop()
                timer_nlidb_json_result_set.start()
            
            columns = (list(map(lambda x: [x[0], self.__translate_mysql_datatype_to_sqlite(FieldType.get_info(x[1]))], cursor_description)))
            
            columns = json.dumps(columns)
            # prepare the result set as JSON
            result_set = json.dumps(result_set)            
        except Exception as e:
            print("Error processing NLQ in NaLIR: ", nlq)
            print("Exception: ", e)
        finally:                                             
            return columns, result_set, self.__sql, self.__sql_first_attempt, self.__sql_second_attempt, self.__sql_third_attempt

    def __run_query(self, nlq):
        try:
            query = Query(nlq, self.__rdbms.schema_graph)
            # Stanford Dependency Parser
            StanfordParser(query,self.__config)            
            # Node Mapper
            NodeMapper.phrase_process(query,self.__rdbms,self.__config, token_path = self.__token_path)
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

    def __nlq_rebuild(self, nlidb_interface_fields):
        try:
            nlq = "give me all " + " for each ".join(nlidb_interface_fields).replace(".", "_")
            new_sql = self.__run_query(nlq)             
            self.__sql = self.__join_sql(new_sql)            
        except Exception as e:
            print("Error processing second attempt of NLQ in NaLIR: ", nlq)
            print("Exception: ", e)      

    def __join_sql(self, new_sql):
        select_new_sql_fields, select_new_sql_result, new_sql_sql_list = self.__get_fields_in_sql(new_sql, '(SELECT )(DISTINCT )?(.*)$', 0, 3, ',')
        from_new_sql_fields, from_new_sql_result, new_sql_sql_list = self.__get_fields_in_sql(new_sql, '(FROM )(.*)$', 1, 2, ',')
        where_new_sql_fields, where_new_sql_result, new_sql_sql_list = self.__get_fields_in_sql(new_sql, '(WHERE )(.*)$', 2, 2, ' AND ')

        select_fields, select_result, sql_list = self.__get_fields_in_sql(self.__sql_second_attempt, '(SELECT )(DISTINCT )?(.*)$', 0, 3, ',')
        from_fields, from_result, sql_list = self.__get_fields_in_sql(self.__sql_second_attempt, '(FROM )(.*)$', 1, 2, ',')
        where_fields, where_result, sql_list = self.__get_fields_in_sql(self.__sql_second_attempt, '(WHERE )(.*)$', 2, 2, ' AND ')

        select_final_fields = set()
        from_final_fields = set()
        where_final_fields = set()

        for select_new_sql_field in select_new_sql_fields:
            if select_new_sql_field not in select_fields:
                select_final_fields.add(select_new_sql_field)

        for from_new_sql_field in from_new_sql_fields:
            if from_new_sql_field not in from_fields:
                from_final_fields.add(from_new_sql_field)

        for where_new_sql_field in where_new_sql_fields:
            if where_new_sql_field not in where_fields:
                where_final_fields.add(where_new_sql_field)        

        select_final_fields.update(select_fields)
        from_final_fields.update(from_fields)
        where_final_fields.update(where_fields)

        select_str = "SELECT DISTINCT " + ', '.join(select_final_fields)
        from_str = "\nFROM " + ', '.join(from_final_fields)
        where_str = "\nWHERE " + ' AND '.join(where_final_fields)
        
        sql = select_str + from_str + where_str
        return sql


            
    
    
