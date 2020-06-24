import spacy
from spacy import displacy
from spacy.matcher import Matcher
import abc
import sqlite3
import nltk
#nltk.download('wordnet')
from nltk.corpus import wordnet as wn
import re

class GLAMORISE(metaclass=abc.ABCMeta):



    # instance attribute
    def __init__(self, query, lang="en_core_web_sm"):
        self.__nlp = spacy.load(lang)
        self.__query = query
        self.__doc = self.__nlp(query)
        self.__customize_stop_words

        self.__aggregate_functions = []
        self.__aggregate_fields = []
        self.__group_by_fields = []

        self.__candidate_aggregate_functions = []
        self.__candidate_aggregate_fields = []
        self.__candidate_group_by_fields = []

        self.__having_fields = []
        self.__having_conditions = []
        self.__having_values = []
        self.__having_units = []


        self.__cut_text = []
        self.__substitute_text = {}
        self.__group_by = False
        self.__prepared_query = ''
        self.__matcher = Matcher(self.__nlp.vocab)

        # Just to make it a bit more readable
        self.__WN_NOUN = 'n'
        self.__WN_VERB = 'v'
        self.__WN_ADJECTIVE = 'a'
        self.__WN_ADJECTIVE_SATELLITE = 's'
        self.__WN_ADVERB = 'r'

    @property
    def query(self):
        return self.__query

    #remove later
    @property
    def prepared_query(self):
        return self.__prepared_query

    @property
    def aggregate_functions(self):
        return self.__aggregate_functions

    @property
    def aggregate_fields(self):
        return self.__aggregate_fields

    @property
    def group_by_fields(self):
        return self.__group_by_fields

    @property
    def candidate_aggregate_functions(self):
        return self.__candidate_aggregate_functions

    @property
    def candidate_aggregate_fields(self):
        return self.__candidate_aggregate_fields

    @property
    def candidate_group_by_fields(self):
        return self.__candidate_group_by_fields


    @property
    def having_fields(self):
        return self.__having_fields

    @property
    def having_conditions(self):
        return self.__having_conditions

    @property
    def having_values(self):
        return self.__having_values

    @property
    def having_units(self):
        return self.__having_units


    @property
    def cut_text(self):
        return self.__cut_text

    @property
    def substitute_text(self):
        return self.__substitute_text

    @property
    def group_by(self):
        return self.__group_by

    def __customize_stop_words(self):
        token_exception_list = ['by', 'per', 'how', 'many', 'much', 'and', 'more',
                                'greater', 'than', 'hundred', 'of']
        for token in token_exception_list:
            if self.__nlp.vocab[token].is_stop:
                self.__nlp.vocab[token].is_stop = False

    def matcher(self, patterns):
        for pattern in patterns:
            self.__matcher.add(str(patterns), None, pattern)
            matches = self.__matcher(self.__doc)
            if matches != []:
                return True
        return False
    def iterator_has_next(self, iterator):
        try:
            next(iterator)
            return True
        except:
            return False

    def build_field(self, token, type):
        if (type == 'group by' and token.text != 'and') or not self.iterator_has_next(token.ancestors):
            next_token_tree = token.children
        else:
            next_token_tree = token.ancestors
        for next_token in next_token_tree:
            # dealing with "and" acting as "per" - exception
            if type == 'group by' and token.text == 'and':
                next_token = token.nbor()
            if next_token.tag_ in ['NN', 'NNS']:
                # set the field
                field = next_token.lemma_
                accum_pre = accum_pos = ''
                # look for compund terms
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
                    self.__aggregate_fields.append(field)
                if type == 'group by':
                    self.__group_by_fields.append(field)
                if type == 'having':
                    self.__having_fields.append(field)
                break


    '''
    def pattern_match(self, token, reserved_words, children_reserved_words = None, ancestors_reserved_words = None): 
      if token.lemma_ in reserved_words:              
          if children_reserved_words is None and ancestors_reserved_words is None:
            print("reserved_words")
            return True
          children = list(token.children)
          print("children")
          for child in children:                
            if child.lemma_ in children_reserved_words:       
              if ancestors_reserved_words is None:
                return True
              else:
                break  
          ancestors = list(token.ancestors)
          print("parent")
          for ancestor in ancestors:                
            if ancestor.lemma_ in ancestor_reserved_words:                   
              return True
      return False
    '''

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
            if having != '':
                self.__having_conditions.append(having)
            if not group_by and  self.__having_conditions == []:
                self.build_field(token, type='aggregate')
            elif group_by:
                self.build_field(token, type='group by')
            elif  self.__having_conditions != []:
                self.build_field(token, type='having')
            if children_reserved_words is None:
                self.__cut_text.append(token.text)
            else:
                children = list(token.children)
                for child in children:
                    if child.lemma_ in children_reserved_words:
                        self.__cut_text.append(child.text + ' ' + token.text)

    def adjective_to_noun_pattern_match(self, token, reserved_words, aggregate_function):
        if token.lemma_ in reserved_words:
            noun = self.convert_word(token.lemma_, self.__WN_ADJECTIVE, self.__WN_NOUN)
            self.__substitute_text[token.lemma_] = noun
            # the aggregation processor is going to verify after if it is necessary, just if it is not the
            # "default_time_scale" a keyword in the metadata table NLIDB_FIELD_UNITS returned by the NLIDB with the
            # result set
            self.__group_by_fields.append(noun)
            #if the above field is used in the group by, the aggregation function is sum
            self.aggregate_functions.append(aggregate_function)

    def pattern_scan(self):
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

            # get the most, maximum, max pattern
            self.syntetic_tree_pattern_match(token,
                                             {'most': 'max', 'maximum': 'max', 'max': 'max'})

            # get the least, minimum, min pattern
            self.syntetic_tree_pattern_match(token,
                                             {'least': 'min', 'minimum': 'min', 'min': 'min'})

            # get the average, mean pattern
            self.syntetic_tree_pattern_match(token,
                                             {'average': 'avg', 'mean': 'avg', 'avg': 'avg'})

            # get the by, per pattern
            self.syntetic_tree_pattern_match(token, {'by': None, 'per': None}, group_by=True)

            # get the greater than, more than pattern
            self.syntetic_tree_pattern_match(token, {'great': None, 'more': None}, having='+')

            # get the less than pattern
            self.syntetic_tree_pattern_match(token, {'less': None}, having='-')

            # get the equal to pattern
            self.syntetic_tree_pattern_match(token, {'equal': None}, having='=')

            # get daily, monthly, yearly pattern
            self.adjective_to_noun_pattern_match(token, ['daily', 'monthly', 'yearly'], 'sum')

            # superlative min:  least, smallest, tiniest, shortest, cheapest, nearest, lowest, worst, newest
            self.adjective_to_noun_pattern_match(token, ['least', 'smallest', 'tiniest', 'shortest', 'cheapest',
                                                          'nearest', 'lowest', 'worst', 'newest'], 'min')

            # superlative max: most, biggest, longest, furthest, highest, tallest, greatest, best, oldest
            self.adjective_to_noun_pattern_match(token, ['most', 'biggest', 'longest', 'furthest', 'highest',
                                                  'tallest', 'greatest', 'best', 'oldest'], 'max')

            # get greater than, more than pattern

            # get less than pattern

            # get less than pattern


    def customized_displacy(self):
        displacy.render(self.__doc, style='dep', jupyter=True,
                        options={'distance': 90, 'fine_grained': True,
                                 'add_lemma': True, 'collapse_phrases': False})



    def convert_word(self, word, from_pos, to_pos):
        """ Transform words given from/to POS tags """

        synsets = wn.synsets(word, pos=from_pos)
        # Word not found
        if not synsets:
            return []

        # Get all lemmas of the word (consider 'a'and 's' equivalent)
        lemmas = [l for s in synsets
                  for l in s.lemmas()
                  if s.name().split('.')[1] == from_pos
                  or from_pos in (self.__WN_ADJECTIVE, self.__WN_ADJECTIVE_SATELLITE)
                  and s.name().split('.')[1] in (self.__WN_ADJECTIVE, self.__WN_ADJECTIVE_SATELLITE)]
        # Get related forms
        derivationally_related_forms = [(l, l.derivationally_related_forms()) for l in lemmas]
        # return derivationally_related_forms
        # filter only the desired pos (consider 'a' and 's' equivalent)
        related_noun_lemmas = [l for drf in derivationally_related_forms
                               for l in drf[1]
                               if l.synset().name().split('.')[1] == to_pos
                               or to_pos in (self.__WN_ADJECTIVE, self.__WN_ADJECTIVE_SATELLITE)
                               and l.synset().name().split('.')[1] in (self.__WN_ADJECTIVE, WN_ADJECTIVE_SATELLITE)]

        # Extract the words from the lemmas
        words = [l.name() for l in related_noun_lemmas]
        len_words = len(words)

        # Build the result in the form of a list containing tuples (word, probability)
        result = [(w, float(words.count(w)) / len_words) for w in set(words)]
        result.sort(key=lambda w: -w[1])

        # return the best possibility [0][0]
        return result[0][0] if result else ''

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


    @abc.abstractmethod
    def send_question_receive_answer(self):
        return



class GLAMORISEMockNLIDB(GLAMORISE):

    def send_question_receive_answer(self):
        return

class SimpleSQLLite:

    def __init__(self, database):
        self.__database = database

    def execute_sql(self, sql, msg=''):
        try:
            conn = sqlite3.connect(database)
            # conn = sqlite3.connect('content/datasets/NLIDB.db')
            conn.executescript(sql)
            print(msg)
        except sqlite3.Error as error:
            print("Error while executing sql", error)
        finally:
            if (conn):
                conn.close()
                print("sqlite connection is closed")

class MockNLIDB:

    def __init__(self):
        self.__SimpleSQLLite('./datasets/NLIDB.db')



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
            self.__SimpleSQLLite.execute_sql(sql, 'Rows inserted')

    def query_question(self):
        pass

    def process_query(self):
        pass

    def receive_question_send_asnwer(self):
        pass



