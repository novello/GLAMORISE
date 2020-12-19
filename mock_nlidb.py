from simple_sqlite import SimpleSQLite
import json

# Simple class to act as a NLIDB
class MockNlidb:

    def __init__(self):
        # open the database
        self.__SimpleSQLite = SimpleSQLite('./datasets/mock_nlidb_anp.db')

    def create_table(self):
        # used to create table, just in a task to import is needed
        sql = '''CREATE TABLE NLIDB_RESULT_SET (
                                FIELD TEXT,            
                                BASIN TEXT,
                                STATE TEXT,            
                                OPERATOR TEXT,
                                CONTRACT_NUMBER TEXT,
                                OIL_PRODUCTION REAL,
                                GAS_PRODUCTION REAL,
                                MONTH INTEGER,
                                YEAR INTEGER);'''
        self.__SimpleSQLite.execute_sql(sql, 'Table created')

    def drop_table(self):
        sql = '''DROP TABLE NLIDB_RESULT_SET;'''
        self.__SimpleSQLite.execute_sql(sql, 'Table dropped')

    def insert_data(self):
        # used to insert data, just in a task to import is needed
        with open('./datasets/anp_insert.txt', 'r', encoding='utf8') as file:
            sql = file.read()
            self.__SimpleSQLite.execute_sql(sql, '')

    def field_synonym(self, synonym):
        # responsible for the translation of the field to the appropriated column
        try:
            sql = "SELECT field FROM NLIDB_FIELD_SYNONYMS WHERE synonym = '" + synonym + "'"
            field, cursor_description = (self.__SimpleSQLite.execute_sql(sql, 'Field translated'))
            return list(field)[0][0]
        except:
            return synonym

    def execute_query(self, nlq, timer_nlidb_execution, timer_nlidb_json_result_set):
        timer_nlidb_execution.start()
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
            timer_nlidb_execution.stop()
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