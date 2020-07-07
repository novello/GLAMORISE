import spacy
from spacy import displacy
from spacy.matcher import Matcher
import abc
import sqlite3
import re
import json
import pandas as pd


class GLAMORISE(metaclass=abc.ABCMeta):

    # instance attribute
    def __init__(self, query, lang="en_core_web_sm"):
        self.__nlp = spacy.load(lang)
        self.__query = query
        self.__doc = self.__nlp(query)
        self.__customize_stop_words

        self.__aggregate_functions = []
        self._aggregate_fields = []
        self._group_by_fields = []

        self.__candidate_aggregate_functions = []
        self._candidate_aggregate_fields = []
        self._candidate_group_by_fields = []

        self._having_fields = []
        self.__having_conditions = []
        self.__having_values = []
        self.__having_units = []

        self.__cut_text = []
        self.__substitute_text = {}
        self.__group_by = False
        self.__prepared_query = ''

        self.__select_clause = ''
        self.__from_clause = ''
        self.__group_by_clause = ''
        self.__having_clause = ''
        self.__order_by_clause = ''
        self.__sql= ''

        self.__post_processing_group_by_fields = []


        self.__matcher = Matcher(self.__nlp.vocab)

        # Just to make it a bit more readable
        self.__WN_NOUN = 'n'
        self.__WN_VERB = 'v'
        self.__WN_ADJECTIVE = 'a'
        self.__WN_ADJECTIVE_SATELLITE = 's'
        self.__WN_ADVERB = 'r'

        self.__SimpleSQLLite = SimpleSQLLite('./datasets/GLAMORISE.db')

        self.__pd = None

    @property
    def query(self):
        return self.__query

    # remove later
    @property
    def prepared_query(self):
        return self.__prepared_query

    @property
    def aggregate_functions(self):
        return self.__aggregate_functions.copy()

    @property
    def aggregate_fields(self):
        return self._aggregate_fields.copy()

    @property
    def group_by_fields(self):
        return self._group_by_fields.copy()

    @property
    def candidate_aggregate_functions(self):
        return self.__candidate_aggregate_functions.copy()

    @property
    def candidate_aggregate_fields(self):
        return self._candidate_aggregate_fields.copy()

    @property
    def candidate_group_by_fields(self):
        return self._candidate_group_by_fields.copy()

    @property
    def having_fields(self):
        return self._having_fields.copy()

    @property
    def having_conditions(self):
        return self.__having_conditions.copy()

    @property
    def having_values(self):
        return self.__having_values.copy()

    @property
    def having_units(self):
        return self.__having_units.copy()

    @property
    def having_units(self):
        return self.__having_units.copy()

    @property
    def cut_text(self):
        return self.__cut_text

    @property
    def substitute_text(self):
        return self.__substitute_text

    @property
    def group_by(self):
        return self.__group_by

    @property
    def select_clause(self):
        return self.__select_clause

    @property
    def from_clause(self):
        return self.__from_clause

    @property
    def group_by_clause(self):
        return self.__group_by_clause

    @property
    def having_clause(self):
        return self.__having_clause

    @property
    def order_by_clause(self):
        return self.__order_by_clause

    @property
    def sql(self):
        return self.__sql

    @property
    def pd(self):
        return self.__pd.copy()

    @property
    def post_processing_group_by_fields(self):
        return self.__post_processing_group_by_fields

    def __customize_stop_words(self):
        token_exception_list = ['by', 'per', 'how', 'many', 'much', 'and', 'more',
                                'greater', 'than', 'hundred', 'of']
        for token in token_exception_list:
            if self.__nlp.vocab[token].is_stop:
                self.__nlp.vocab[token].is_stop = False

    def iterator_has_next(self, iterator):
        try:
            next(iterator)
            return True
        except:
            return False

    def new_build_field(self, token, field_property):
        accum_pre = accum_pos = ''
        field = token.lemma_
        for child in token.children:
            # get compound terms that are not proper noun
            if child.dep_ == 'compound' and child.pos_ == 'NOUN' \
                    and child.head == token:  # direct child
                accum_pre = accum_pre + child.lemma_ + ' '
            # get compound names with "of"
            if child.dep_ == 'prep' and child.pos_ == 'ADP' \
                    and child.text == 'of' and child.head == token:  # direct child
                accum_pos = accum_pos + child.lemma_ + ' '
                for grandchild in child.children:
                    if grandchild.dep_ == 'pobj' and grandchild.pos_ == 'NOUN':
                        accum_pos = accum_pos + grandchild.lemma_ + ' '
        field = str(accum_pre + field if accum_pre != '' else field + ' ' + accum_pos).strip()
        field_property.append(field)

    def build_field(self, token, type):
        if (type == 'group_by' and token.text != 'and') or not self.iterator_has_next(token.ancestors):
            next_token_tree = token.children
        else:
            next_token_tree = token.ancestors
        for next_token in next_token_tree:
            # dealing with "and" acting as "per" - exception
            if type == 'group_by' and token.text == 'and':
                next_token = token.nbor()
            if next_token.tag_ in ['NN', 'NNS']:
                # set the field
                field = next_token.lemma_
                accum_pre = accum_pos = ''
                # look for compound terms
                for next_token_children in next_token.children:
                    # preparing "and" acting as "per" - exception
                    if next_token_children.dep_ == 'cc' and next_token_children.lemma_ == 'and':
                        next_token_children.lemma_ = 'per'
                    # get compound terms that are not proper noun
                    if next_token_children.dep_ == 'compound' and next_token_children.tag_ != 'NNP' \
                            and next_token_children.head == next_token:
                        accum_pre = accum_pre + next_token_children.lemma_ + ' '
                    if next_token_children.dep_ == 'prep' and next_token_children.tag_ == 'IN' \
                            and next_token_children.lemma_ == 'of' and next_token_children.head == next_token:
                        accum_pos = accum_pos + next_token_children.lemma_ + ' '
                        for next_token_grandchildren in next_token_children.children:
                            if next_token_grandchildren.dep_ == 'pobj' and next_token_grandchildren.tag_ == 'NN':
                                accum_pos = accum_pos + next_token_grandchildren.lemma_ + ' '
                field = str(accum_pre + field if accum_pre != '' else field + ' ' + accum_pos).strip()
                if type == 'aggregate':
                    self._aggregate_fields.append(field)
                if type == 'group_by':
                    self._group_by_fields.append(field)
                if type == 'candidate_group_by':
                    self._candidate_group_by_fields.append(field)
                #if type == 'having':
                #    self._having_fields.append(field)
                break

    def check_nnp_in_children(self, token):
        for child in token.children:
            if child.tag_ == 'NNP':
                return True
        return False

    def syntetic_tree_pattern_match(self, token, reserved_words, children_reserved_words=None,
                                    group_by=False, having=''):
        if token.lemma_ in reserved_words:
            if reserved_words[token.lemma_] is not None:
                self.__aggregate_functions.append(reserved_words[token.lemma_])
            self.__group_by = group_by
            #if having != '':
            #    self.__having_conditions.append(having)
            if not group_by:# and self.__having_conditions == []:
                self.build_field(token, type='aggregate')
                #self.new_build_field(token, self._aggregate_fields)
            elif group_by:
                self.build_field(token, type='group_by')
                #self.new_build_field(token, self._group_by_fields)
            #elif self.__having_conditions != []:
            #    self.build_field(token, type='having')
            if children_reserved_words is None:
                self.__cut_text.append(token.text)
            else:
                children = list(token.children)
                for child in children:
                    if child.lemma_ in children_reserved_words:
                        self.__cut_text.append(child.text + ' ' + token.text)


    def adjective_to_noun_pattern_match(self, token, reserved_words, aggregate_function):
        adj_noun = {'daily': 'day', 'monthly': 'month', 'yearly': 'year'}
        if token.lemma_ in reserved_words:
            noun = adj_noun[token.lemma_]
            self.__substitute_text[token.lemma_] = noun
            # the aggregation processor is going to verify after if it is necessary, just if it is not the
            # "default_time_scale" a keyword in the metadata table NLIDB_FIELD_UNITS returned by the NLIDB with the
            # result set
            self._candidate_group_by_fields.append(noun)
            # if the above field is used in the group by, the aggregation function is sum
            self.__candidate_aggregate_functions.append(aggregate_function)
            self.new_build_field(token.head, self._candidate_aggregate_fields)

    def superlative_pattern_match(self, token):
        min = ['least', 'smallest', 'tiniest', 'shortest', 'cheapest', 'nearest', 'lowest', 'worst', 'newest', 'min',
               'minimum']
        max = ['most', 'biggest', 'longest', 'furthest', 'highest', 'tallest', 'greatest', 'best', 'oldest', 'max',
               'maximum']

        if token.text in max + min:
            self.new_build_field(token.head, self._aggregate_fields)  # set the aggregate field
            self.__cut_text.append(token.text)  # set the text that should be cut
            if token.text in max:  # set the aggregation function
                self.__aggregate_functions.append('max')
            else:
                self.__aggregate_functions.append('min')
            '''    
            # look for the group by field
            for verb_token in self.__doc:
                # the group by field is child of a verb, first find the auxiliary verb
                if verb_token.pos_ == 'AUX':  #  ['AUX', 'VERB'] if main verbs occur
                    # after this look for the child that is a noun and is nominal subject
                    for child in verb_token.children:
                        if child.pos_ == 'NOUN' and child.dep_ == 'nsubj':
                            # set the group by field
                            self.new_build_field(child, self._group_by_fields)
            '''

    def token_scan(self):
        for token in self.__doc:
            if self.check_nnp_in_children(token):
                continue
            '''
            # get the how many, how much pattern
            if token.lemma_ in ['many', 'much']:      
              children = list(token.children)      
              for child in children:                
                if child.lemma_ == 'how':       
                  #set aggregate_function
                  if token.lemma_ == 'many':
                    self.__aggregate_functions = 'count'  
                  elif  token.lemma_ == 'much':
                    self.__aggregate_functions = 'sum'           
                  #set the text that will be removed from the query before passing to the NLIDB
                  self.__cut_text = child.lemma_ + ' ' + token.lemma_          
                  self.build_aggregate_field(token)
            '''
            # get the how many, how much pattern
            self.syntetic_tree_pattern_match(token,
                                             {'many': 'count', 'number': 'count', 'much': 'sum'},
                                             ['how', 'of'])

            # get the average, mean pattern
            self.syntetic_tree_pattern_match(token,
                                             {'average': 'avg', 'mean': 'avg', 'avg': 'avg'})

            # get the by, per pattern
            self.syntetic_tree_pattern_match(token, {'by': None, 'per': None}, group_by=True)

            # get daily, monthly, yearly pattern
            self.adjective_to_noun_pattern_match(token, ['daily', 'monthly', 'yearly'], 'sum')

            # superlative min:  least, smallest, tiniest, shortest, cheapest, nearest, lowest, worst, newest
            # superlative max: most, biggest, longest, furthest, highest, tallest, greatest, best, oldest
            self.superlative_pattern_match(token)


    def entity_scan(self):
        # get each recognized entity
        for entity in self.__doc.ents:
            # check if it is number like
            if entity.label_ in ['MONEY', 'QUANTITY', 'CARDINAL']:
                # check the pattern "greater|more than" and set having condition to ">"
                if entity[0].text in ['more', 'greater'] and entity[1].text == 'than':
                    self.__having_conditions.append('>')
                    prefix = entity[0].text + ' ' + entity[1].text
                    find_value = True
                # check the pattern "less than" and set having condition to "<"
                if entity[0].text == 'less' and entity[1].text == 'than':
                    self.__having_conditions.append('<')
                    prefix = entity[0].text + ' ' + entity[1].text
                    find_value = True

                # check the pattern "equal to" and set having condition to "="
                # not working because of spaCy faulty entity recognition
                if entity[0].text == 'equal' and entity[1].text == 'to':
                    self.__having_conditions.append('=')
                    prefix = entity[0].text + ' ' + entity[1].text
                    find_value = True

                # find and set the having condition
                if find_value:
                    having_value = ''
                    # examine each token inside the entity
                    for token in entity:
                        one_token_doc = self.__nlp(token.text)
                        # if the token alone is cardinal use it to build the having value
                        if one_token_doc[0].ent_type_ == 'CARDINAL':
                            having_value += ' ' + one_token_doc[0].text
                    # clear thousand and decimal separator and spaces and set the having value
                    self.__having_values.append(having_value.replace(',','').replace('.','').strip())
                    # replace text to leave just the measure unit and clear spaces
                    self.__having_units.append(entity.text.replace(having_value, '').replace(prefix, '').strip())
                    # assume that we are dealing ith the same fields,
                    # change this in the future to a more accurate answer
                    self._having_fields = self.aggregate_fields.copy()





    def customized_displacy(self):
        displacy.render(self.__doc, style='dep', jupyter=True,
                        options={'distance': 90, 'fine_grained': True,
                                 'add_lemma': True, 'collapse_phrases': False})


    def prepare_query_to_NLIDB(self):
        self.__prepared_query = self.__query
        for cut_text in self.__cut_text:
            regex = r"(^|(.*?[\s.,;!?]+))(" + cut_text + r"([\s.,;!?]|$))(([\s., ;!?]*.*)|$)"
            self.__prepared_query = re.sub(regex, r"\1\5", self.__prepared_query)
        for substitute_text in self.__substitute_text:
            regex = r"(^|(.*?[\s.,;!?]+))(" + substitute_text + r")(([\s., ;!?]*.*)|$)"
            str = r"\1" + self.__substitute_text[substitute_text] + r"\5"
            self.__prepared_query = re.sub(regex, str, self.__prepared_query)
        return self.__prepared_query

    def preprocessor(self):
        self.token_scan()
        self.entity_scan()
        self.prepare_query_to_NLIDB()

    def create_table_and_insert_data(self, columns, result_set):
        sql = 'DROP TABLE IF EXISTS NLIDB_RESULT_SET; CREATE TABLE NLIDB_RESULT_SET (' + ', '.join([column[
                                                                                                        0] + ' ' +
                                                                                                    column[1] for column
                                                                                                    in
                                                                                                    columns]) + \
              ');'
        self.__SimpleSQLLite.execute_sql(sql)
        sql = 'INSERT INTO NLIDB_RESULT_SET VALUES(' + ''.join(['?, ' for field in result_set[0]])[:-2] + ')'
        self.__SimpleSQLLite.executemany_sql(sql, result_set)

    def processor(self, columns, result_set):
        self.translate_all_fields()
        self.__post_processing_group_by_fields = [column[0].lower() for column in columns \
                                                  if column[0].lower() not in self._group_by_fields +
                                                  self._aggregate_fields + self._candidate_aggregate_fields +
                                                  self._candidate_group_by_fields]
        self.prepare_aggregate_SQL()
        self.create_table_and_insert_data(columns, result_set)
        self.__pd = self.__SimpleSQLLite.pandas_dataframe(self.__sql)



    def execute(self):
        self.preprocessor()
        columns, result_set = self.send_question_receive_answer()
        columns = json.loads(columns)
        result_set = json.loads(result_set)
        self.processor(columns, result_set)


    @abc.abstractmethod
    def send_question_receive_answer(self):
       pass

    @abc.abstractmethod
    def translate_fields(self):
        pass

    def prepare_aggregate_SQL(self):
        #initialize clauses
        if self._aggregate_fields:
            self.__select_clause = 'SELECT '
        # is exists a group by field
        if self._group_by_fields:
            self.__group_by_clause = 'GROUP BY '
            self.__order_by_clause = 'ORDER BY '
        if self._having_fields:
            self.__having_clause = 'HAVING '

        # the group by fields impact the clauses SELECT, GROUP BY and ORDER BY and nested queries
        nested_group_by_field = ''
        for group_by_field in self._group_by_fields:
            self.__select_clause += group_by_field + ', '
            nested_group_by_field += group_by_field + ', '
            self.__group_by_clause += group_by_field + ', '
            self.__order_by_clause += group_by_field + ', '

        #if it is an aggregation query:
        if self._aggregate_fields:
            # the same for the post processing group by fields (field identified just by the NLIDB)
            for post_processing_group_by_field in self.__post_processing_group_by_fields:
                # just if the field was not recognized by GLAMORISE
                    if not self.__group_by_clause:
                        self.__group_by_clause = 'GROUP BY '
                    if not self.__order_by_clause:
                        self.__order_by_clause = 'ORDER BY '
                    self.__select_clause += post_processing_group_by_field + ', '
                    nested_group_by_field += post_processing_group_by_field + ', '
                    self.__group_by_clause += post_processing_group_by_field + ', '
                    self.__order_by_clause += post_processing_group_by_field + ', '

        # building the syntax of the aggregate functions, aggregate fields e.g. min(production),
        # and candidate aggregate field and function if they exist
        for i in range(len(self.__aggregate_functions)):
            # building sql part for aggregate field and function
            self.__select_clause += self.__aggregate_functions[i] + \
                                    '(' + self._aggregate_fields[i] + ') as ' + \
                                    self.__aggregate_functions[i] + '_' + \
                                    self._aggregate_fields[i] + ', '

            # building sql part for candidate aggregate field and function
            # it is done as a subquery, but if one day SQLite is substituted it could be done with nested functions
            # e.g. SELECT avg(sum(oil_production) as avg_sum_oil_production FROM NLIDB_result_set GROUP BY year
            if self._aggregate_fields[i] in self._candidate_aggregate_fields:
                j = self._candidate_aggregate_fields.index(self._aggregate_fields[i])
                self.__from_clause = ' FROM (SELECT ' + nested_group_by_field + self.__candidate_aggregate_functions[j] + '(' + \
                                     self._aggregate_fields[i] + ') as ' + \
                                     self._aggregate_fields[i] + ' FROM NLIDB_result_set'
                self.__from_clause += ' GROUP BY ' + nested_group_by_field + \
                                      ', '.join(self._candidate_group_by_fields) + ') '

            # if there is no candidate fields and function, it is a common FROM without subquery
            else:
                self.__from_clause = ' FROM NLIDB_result_set '


        # building the HAVING clause having field, followed by operator, followed by value
        for i in range(len(self._having_fields)):
            # we have to change the use of aggregate function in the future
            self.__having_clause += self.__aggregate_functions[i] + \
                                    '(' + self._having_fields[i] + ') ' + self.__having_conditions[i] + ' ' \
                                    + self.__having_values[i] + ' and '

        # cut the ", " or " and " at the end of each string
        self.__select_clause = self.__select_clause[0:-2]
        self.__group_by_clause = self.__group_by_clause[0:-2]
        self.__having_clause = self.__having_clause[0:-5]
        self.__order_by_clause = self.__order_by_clause[0:-2]

        #GLAMORISE has nothing to do, not an aggregation query
        if self.__select_clause == '':
            self.__select_clause = 'SELECT * FROM NLIDB_result_set'

        self.__sql = (self.__select_clause + self.__from_clause + self.__group_by_clause + ' ' + \
                     self.__having_clause + ' ' + self.__order_by_clause).replace("  ", " ").strip()

    def __del__(self):
        sql = 'DROP TABLE IF EXISTS NLIDB_RESULT_SET;'
        self.__SimpleSQLLite.execute_sql(sql)

class GLAMORISEMockNLIDB(GLAMORISE):

    def __init__(self, query, lang="en_core_web_sm"):
        super(GLAMORISEMockNLIDB, self).__init__(query, lang)
        self.__nlidb = MockNLIDB()
        self.execute()

    def send_question_receive_answer(self):
        columns, result_set = self.__nlidb.execute_query(self.prepared_query)
        return columns, result_set

    def translate_fields(self, fields):
        for i in range(len(fields)):
            fields[i] = self.__nlidb.field_synonym(fields[i].replace(' ', '_'))
        if fields:
            fields_str = ','.join(fields)
            fields = fields_str.split(',')
            fields = [field.strip() for field in fields]
        return fields


    def translate_all_fields(self):
        self._aggregate_fields = self.translate_fields(self._aggregate_fields)
        self._group_by_fields = self.translate_fields(self._group_by_fields)
        self._candidate_aggregate_fields = self.translate_fields(self._candidate_aggregate_fields)
        self._candidate_group_by_fields = self.translate_fields(self._candidate_group_by_fields)
        self._having_fields = self.translate_fields(self._having_fields)

class SimpleSQLLite:

    def __init__(self, database):
        self.__database = database

    def executemany_sql(self, sql, params):
        try:
            conn = sqlite3.connect(self.__database)
            conn.executemany(sql, params)
            conn.commit()
        except sqlite3.Error as error:
            print("Error while executing execute many", error)
        finally:
            if (conn):
                conn.close()

    def execute_sql(self, sql, msg=''):
        try:
            conn = sqlite3.connect(self.__database)
            if ';' in sql:
                conn.executescript(sql)
            else:
                cursor = conn.execute(sql)
                columns = cursor.description
                rows = cursor.fetchall()
                return rows, columns
            print(msg)
        except sqlite3.Error as error:
            print("Error while executing sql", error)
        finally:
            if (conn):
                conn.close()

    def pandas_dataframe(self, sql):
        try:
            conn = sqlite3.connect(self.__database)
            return pd.read_sql_query(sql, conn)
        finally:
            if (conn):
                conn.close()


class MockNLIDB:

    def __init__(self):
        self.__SimpleSQLLite = SimpleSQLLite('./datasets/NLIDB.db')

    def create_table(self):
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
        self.__SimpleSQLLite.execute_sql(sql, 'Table created')

    def drop_table(self):
        sql = '''DROP TABLE NLIDB_RESULT_SET;'''
        self.__SimpleSQLLite.execute_sql(sql, 'Table dropped')

    def insert_data(self):
        with open('./datasets/anp_insert.txt', 'r', encoding='utf8') as file:
            sql = file.read()
            self.__SimpleSQLLite.execute_sql(sql, '')

    def query_question(self):
        pass

    def process_query(self):
        pass

    def receive_question_send_answer(self):
        pass

    def field_synonym(self, synonym):
        try:
            sql = "SELECT field FROM NLIDB_FIELD_SYNONYMS WHERE synonym = '" + synonym + "'"
            field, cursor_description = (self.__SimpleSQLLite.execute_sql(sql, 'Field translated'))
            return list(field)[0][0]
        except:
            return synonym

    def execute_query(self, nlq):

        sql = "SELECT sql FROM NLIDB_SQL_FROM_NLQ WHERE lower(nlq) = '" + nlq.lower() + "'"
        sql = self.__SimpleSQLLite.execute_sql(sql, 'SQL generated')[0]
        sql_result = list(sql)[0][0]
        result_set, cursor_description = self.__SimpleSQLLite.execute_sql(sql_result, 'Query executed')
        result_set = json.dumps(result_set)
        #column_names = json.dumps(list(map(lambda x: x[0], cursor_description)))
        column_names = (list(map(lambda x: x[0], cursor_description)))

        sql = "SELECT name, type FROM PRAGMA_TABLE_INFO('ANP')"
        column_types = self.__SimpleSQLLite.execute_sql(sql, 'Metadata collected')[0]
        #column_types = json.dumps(column_types)

        columns = json.dumps([(column_name, column_type[1])
                              for column_name in column_names
                                for column_type in column_types
                                    if column_type[0] == column_name])
        return columns, result_set

