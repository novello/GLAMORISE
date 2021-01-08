from simple_sqlite import SimpleSQLite
import json

# Simple class to act as a NLIDB
class MockNlidb:

    def __init__(self):
        # open the database
        self.__SimpleSQLite = SimpleSQLite('./datasets/mock_nlidb_anp.db')

    
    def field_synonym(self, synonym, replace_dot = True):
        # responsible for the translation of the field to the appropriated column
        try:
            sql = "SELECT field FROM NLIDB_FIELD_SYNONYMS WHERE synonym = '" + synonym.lower().replace(' ', '_').replace('.', '_') + "'"
            field, cursor_description = (self.__SimpleSQLite.execute_sql(sql, 'Field translated'))
            field = list(field)[0][0].replace(' ', '_')
            if replace_dot:
                field = field.replace('.', '_')
            return field
        except:
            return synonym

    def execute_query(self, nlq, timer_nlidb_execution_first_and_second_attempt,  timer_nlidb_json_result_set):
        timer_nlidb_execution_first_and_second_attempt.start()
        try:            
            # mock NLQ processing, return the SQL for the NLQ query
            sql = "SELECT sql FROM NLIDB_SQL_FROM_NLQ WHERE lower(nlq) = '" + nlq.lower() + "'"
            sql = self.__SimpleSQLite.execute_sql(sql, 'SQL generated')[0]
            sql_result = list(sql)[0][0]
            result_set, cursor_description = self.__SimpleSQLite.execute_sql(sql_result, 'Query executed')
            # prepare the result set as JSON
            result_set = json.dumps(result_set)
            column_names = (list(map(lambda x: x[0], cursor_description)))

            # internal data dictionary table of SQLite
            sql = "SELECT name, type FROM PRAGMA_TABLE_INFO('ANP')"
            timer_nlidb_execution_first_and_second_attempt.stop()
            timer_nlidb_json_result_set.start()
            column_types = self.__SimpleSQLite.execute_sql(sql, 'Metadata collected')[0]            
            # prepare the column names and types as JSON
            columns = json.dumps([(column_name, column_type[1])
                                  for column_name in column_names
                                    for column_type in column_types
                                        if column_type[0] == column_name])
            print(sql_result)                                                                       
            return columns, result_set, sql_result
        except:
            print("Query not found: ", nlq)