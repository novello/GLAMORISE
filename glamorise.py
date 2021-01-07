#
# Developed by Alexandre Novello (PUC-Rio)
#
#!pip install spacy==2.2.4
#!pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.2.5/en_core_web_sm-2.2.5.tar.gz
#!pip install codetiming

import spacy
from spacy import displacy
import abc
import re
import json
import pandas as pd
from spacy.matcher import Matcher
from spacy.tokens import Token
from collections import defaultdict
from word2number import w2n
import os
from copy import deepcopy
from simple_sqlite import SimpleSQLite
from codetiming import Timer



# We're using classes for pipeline  because the component needs to be initialised with
# the shared vocab via the nlp object

# common stuff of Merger classes
class Merger(metaclass=abc.ABCMeta):
      def __call__(self, doc):
        # This method is invoked when the component is called on a Doc
        matches = self.matcher(doc)
        spans = []  # Collect the matched spans here
        for match_id, start, end in matches:
            spans.append(doc[start:end])
        with doc.retokenize() as retokenizer:
            for span in spans:
                retokenizer.merge(span)
                for token in span:
                    if self._type == 'compound':
                      token._.compound_noun = True  # Mark token as compound noun               
                    elif self._type == 'units_of_measurement':
                      token._.compound_noun = True  # Mark token as compound noun                 
        return doc
 
class CompoundMerger(Merger):
    def __init__(self, nlp):     
        self._type = 'compound'
        # Register a new token extension to flag compound nouns
        Token.set_extension("compound_noun", default=False, force=True)
        compound_pattern_dep = []
        if patterns_json.get('compound_pattern_dep'):
            compound_pattern_dep = patterns_json['compound_pattern_dep']
        compound_pattern_of = []
        if patterns_json.get('compound_pattern_of'):
            compound_pattern_of = patterns_json['compound_pattern_of']            
        self.matcher = Matcher(nlp.vocab)
        if compound_pattern_dep and compound_pattern_of:
            self.matcher.add("CompoundMerger", None, compound_pattern_dep, compound_pattern_of)
        elif compound_pattern_dep:
            self.matcher.add("CompoundMerger", None, compound_pattern_dep)
        elif compound_pattern_of:
            self.matcher.add("CompoundMerger", None, compound_pattern_of)
 
 
 
class UnitsOfMeasurementMerger(Merger):    
    def __init__(self, nlp):    
        self._type = 'units_of_measurement'        
        # Register a new token extension to flag units of measurement
        Token.set_extension("units_of_measurement", default=False, force=True)
        self.matcher = Matcher(nlp.vocab)
        if patterns_json.get('units_of_measurement'):
            for unit_of_measurement in patterns_json['units_of_measurement']:         
                units_of_measurement_pattern = []
                splits = unit_of_measurement.split()      
                for split in splits:        
                    units_of_measurement_pattern = units_of_measurement_pattern + [{'LOWER' : split.lower()}]
                self.matcher.add(
                    "UnitsOfMeasurementMerger" + unit_of_measurement.replace(' ', ''),
                    None,
                    units_of_measurement_pattern
                )

#main class
class Glamorise(metaclass=abc.ABCMeta):    

    def __init__(self, lang="en_core_web_sm", patterns = ""):
        global patterns_json 
        patterns_json = json.loads(patterns)    
        self._patterns_json = patterns_json

        # internal properties
        self.__nlp = spacy.load(lang)            

        # add pipelines and Matcher
        self.__compound_merger = CompoundMerger(self.__nlp)
        self.__units_of_measurement_merger = UnitsOfMeasurementMerger(self.__nlp)
        self.__nlp.add_pipe(self.__units_of_measurement_merger, last=True)  # Add component to the pipeline
        self.__nlp.add_pipe(self.__compound_merger, last=True)  # Add component to the pipeline 
        self.__matcher = Matcher(self.__nlp.vocab, validate=False)
        
        # build patterns for Matcher
        self.__build_patterns()

        # GLAMORISE local database. Used to persist the NLIDB result set and to process the query with aggregation
        self.__SimpleSQLite = SimpleSQLite('./datasets/glamorise.db')

    def initialize_and_reset_attr(self):
        self._timer_total = Timer(name="timer_total", logger=None)
        self._timer_total.start()
        self._timer_pre = Timer(name="timer_pre", logger=None)
        self._timer_nlidb_execution_first_and_second_attempt = Timer(name="timer_nlidb_execution_first_and_second_attempt", logger=None)
        self._timer_nlidb_execution_third_attempt = Timer(name="_timer_nlidb_execution_third_attempt", logger=None)
        self._timer_nlidb_json_result_set = Timer(name="timer_nlidb_json_result_set", logger=None)
        self._timer_pos = Timer(name="timer_pos", logger=None)
        self._timer_exibition = Timer(name="timer_exibition", logger=None)

        self._pre_aggregation_functions = []
        self._pos_aggregation_functions = []
        self._pre_aggregation_fields = []
        self._pos_aggregation_fields = []
        self._pre_group_by_fields = []

        self._pre_time_scale_aggregation_functions = []
        self._pre_time_scale_aggregation_fields = []
        self._pre_time_scale_group_by_fields = []        
        
        self._pre_having_fields = []
        self._pre_having_conditions = []
        self._pre_having_values = []
        self._pre_having_units = []

        self.__pre_cut_text = []
        self.__pre_replaced_text = {}
        self.__pre_group_by = False

        self.__matched_sents = []  # Collect data of matched sentences to be visualized  
        
        self._pre_prepared_query = ''
        self._pre_prepared_query_before_field_translation = ''
        self.__pre_before_query = ''
        self.__original_query = ''

        self.__select_clause = ''
        self.__from_clause = ''
        self.__group_by_clause = ''
        self.__having_clause = ''
        self.__order_by_clause = ''
        self.__pos_glamorise_sql = ''

        # NLIDB fields
        self._nlidb_interface_fields = set()

        # fields revealed only in the NLIDB
        self.__pos_group_by_fields = []
        
        # create the pandas dataframe just if it called before being fed
        self.__pd = None       

    @property
    def pre_before_query(self):
        return self.__pre_before_query

    @property
    def original_query(self):
        return self.__original_query

    @property
    def pre_prepared_query(self):
        return self._pre_prepared_query

    @property
    def pre_prepared_query_before_field_translation(self):
        return self._pre_prepared_query_before_field_translation

    @property
    def pre_aggregation_functions(self):
        return deepcopy(self._pre_aggregation_functions)

    @property
    def pos_aggregation_functions(self):
        return deepcopy(self._pos_aggregation_functions)

    @property
    def pre_aggregation_fields(self):
        return deepcopy(self._pre_aggregation_fields)

    @property
    def pos_aggregation_fields(self):
        return deepcopy(self._pos_aggregation_fields)

    @property
    def pre_group_by_fields(self):
        return deepcopy(self._pre_group_by_fields)

    @property
    def pre_time_scale_aggregation_functions(self):
        return deepcopy(self._pre_time_scale_aggregation_functions)

    @property
    def pre_time_scale_aggregation_fields(self):
        return deepcopy(self._pre_time_scale_aggregation_fields)

    @property
    def pre_time_scale_group_by_fields(self):
        return deepcopy(self._pre_time_scale_group_by_fields)

    @property
    def pre_having_fields(self):
        return deepcopy(self._pre_having_fields)

    @property
    def pre_having_conditions(self):
        return deepcopy(self._pre_having_conditions)

    @property
    def pre_having_values(self):
        return deepcopy(self._pre_having_values)
 
    @property
    def pre_having_units(self):
        return deepcopy(self._pre_having_units)

    @property
    def pre_cut_text(self):
        return self.__pre_cut_text

    @property
    def pre_replaced_text(self):
        return self.__pre_replaced_text

    @property
    def pre_group_by(self):
        return self.__pre_group_by  

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
    def pos_glamorise_sql(self):
        return self.__pos_glamorise_sql

    @property
    def pd(self):                                 
        return deepcopy(self.__pd)
    
    @property
    def patterns_json(self):                                 
        return deepcopy(self._patterns_json)

    @property
    def pos_group_by_fields(self):
        return deepcopy(self.__pos_group_by_fields)

    @property
    def nlidb_interface_fields(self):
        return deepcopy(self._nlidb_interface_fields)    

    def __build_field(self, span, field, pos = '', unit_of_measurement = False, time_scale_group_by_field = '', replace_text = ''):                
        if time_scale_group_by_field != '':
            self._pre_time_scale_group_by_fields.append(time_scale_group_by_field)
            self.__pre_replaced_text[replace_text] = time_scale_group_by_field
            return
        
        # a greater chance of the important part is at the end
        for token in reversed(span):
            if token.pos_ == pos:
                if pos == 'NUM':
                    text = str(w2n.word_to_num(token.text))
                else:
                    text = token.lemma_        
                if (unit_of_measurement and token.text in patterns_json['units_of_measurement']) or \
                   (not unit_of_measurement and token.text not in patterns_json['units_of_measurement']):
                    getattr(self, "_" + field).append(text)           
                    break
                elif field  == 'pre_having_fields':
                    self._pre_having_fields = self._pre_aggregation_fields.copy()
                    break
 
 


    def __build_patterns(self):             
        for key, value in patterns_json['patterns'].items():  
            if isinstance(value['reserved_words'], list):
                for reserved_words in value['reserved_words']:           
                    reserved_words_pattern = []
                    splits = reserved_words.split()      
                    for split in splits:        
                        reserved_words_pattern = reserved_words_pattern + [{'LOWER' : split.lower()}]
                        
                    specific_pattern = value.get('specific_pattern')
                    if specific_pattern:
                        final_pattern = reserved_words_pattern + specific_pattern
                    else:
                        final_pattern = reserved_words_pattern + patterns_json['default_pattern']      
                    self.__matcher.add(key + ' | ' + reserved_words , self.collect_sents, final_pattern)


    #ajustar fine_gained no código antigo
    def customized_displacy(self):
        # set the displacy parameters
        displacy.render(self.__doc, style='dep', jupyter=True,
                        options={'compact' : False, 'distance': 90, 'fine_grained': False,
                                'add_lemma': True, 'collapse_phrases': False})

    #novo
    def customized_displacy_entities(self):
        displacy.render(self.__matched_sents, style="ent", manual=True, jupyter=True)

    def collect_sents(self, matcher, doc, i, matches):      
        match_id, start, end = matches[i]
        match = self.__nlp.vocab.strings[match_id]
        span = doc[start:end]  # Matched span
        sent = span.sent  # Sentence containing matched span
        # Append mock entity for match in displaCy style to matched_sents
        # get the match span by ofsetting the start and end of the span with the
        # start and end of the sentence in the doc
        pattern = match.partition('|')[0].strip()   
        
        reserved_word = match.partition('|')[2].strip()
        if patterns_json['patterns'][pattern].get('pre_cut_text') and patterns_json['patterns'][pattern]['pre_cut_text']:
            self.__pre_cut_text.append(reserved_word) 
        index = patterns_json['patterns'][pattern]['reserved_words'].index(reserved_word)

        options = [{'json_var' : 'pre_having_conditions', 'label' : 'HAVING | CONDITION'},
                {'json_var' : 'pre_aggregation_functions', 'label' : 'AGGREGATION FUNCTION'},
                {'json_var' : 'pre_group_by', 'label' : 'GROUP BY'},
                {'json_var' : 'pre_time_scale_aggregation_functions', 'label' : 'TIMESCALE'}]
        for option in options:
            if patterns_json['patterns'][pattern].get(option['json_var']):            
                if isinstance(patterns_json['patterns'][pattern][option['json_var']], list):                
                    label = option['label'] + " " +  patterns_json['patterns'][pattern][option['json_var']][index]               
                    getattr(self, "_" + option['json_var']).append(patterns_json['patterns'][pattern][option['json_var']][index])         
                elif isinstance(patterns_json['patterns'][pattern][option['json_var']], str):
                    label = option['label'] + " " +  patterns_json['patterns'][pattern][option['json_var']]           
                    getattr(self, "_" + option['json_var']).append(patterns_json['patterns'][pattern][option['json_var']])          
                elif isinstance(patterns_json['patterns'][pattern][option['json_var']], bool):
                    label = "GROUP BY"
                    self.__pre_group_by = patterns_json['patterns'][pattern]['pre_group_by']
        
        match_ents = [{
            "start": span.start_char - sent.start_char,
            "end": span.end_char - sent.start_char,
            "label": label,
        }]    
        
        self.__matched_sents.append({"text": sent.text, "ents": match_ents})
        if patterns_json['patterns'][pattern].get('pre_aggregation_functions'):
            self.__build_field(span, 'pre_aggregation_fields', 'NOUN')
        elif patterns_json['patterns'][pattern].get('pre_group_by'):
            self.__build_field(span, 'pre_group_by_fields', 'NOUN')      
        elif patterns_json['patterns'][pattern].get('pre_having_conditions'):
            self.__build_field(span, 'pre_having_fields', 'NOUN')
            self.__build_field(span, 'pre_having_units', 'NOUN', True)    
            self.__build_field(span, 'pre_having_values', 'NUM')        
        elif patterns_json['patterns'][pattern].get('pre_time_scale_replace_text'):
            self.__build_field(span, 'pre_time_scale_aggregation_fields', 'NOUN')
            self.__build_field(span, 'pre_having_units', 'NOUN', True)    
            replace_text_token = (patterns_json['patterns'][pattern]['reserved_words'][index])
            self.__build_field(span, 'pre_time_scale_group_by_fields', 
                        time_scale_group_by_field = patterns_json['patterns'][pattern]['pre_time_scale_replace_text'][replace_text_token],
                        replace_text = replace_text_token)     

    def __prepare_query_to_NLIDB(self):
        # set the query that is going to be passed to the NLIDB initially as the received query
        self._pre_prepared_query = self.__pre_before_query
        # then cut the texts to be cut
        self._pre_prepared_query = self.__cut_text(self.__pre_cut_text, self._pre_prepared_query)        
        # then replace the texts that must be replaced
        self._pre_prepared_query = self.__replace_text(self.__pre_replaced_text, self._pre_prepared_query)  
        if patterns_json.get('pre_after_cut_text'): 
            self._pre_prepared_query = self.__cut_text(patterns_json['pre_after_cut_text'], self._pre_prepared_query)
        if patterns_json.get('pre_after_replace_text'): 
            self._pre_prepared_query = self.__replace_text(patterns_json['pre_after_replace_text'], self._pre_prepared_query)                    
        
    def __replace_text(self, replaced_text_list, query):
        result = query
        # then replace the texts that must be replaced
        for replaced_text in replaced_text_list:
            regex = r"(^|(.*?[\s.,;!?]+))(" + replaced_text.lower() + r")(([\s., ;!?]*.*)|$)"
            str = r"\1" + replaced_text_list[replaced_text] + r"\5"
            result = re.sub(regex, str, result, flags=re.I)
        return result

    def __cut_text(self,cut_text_list, query):
        result = query
        # then cut the texts to be cut
        for cut_text in cut_text_list:
            regex = r"(^|(.*?[\s.,;!?]+))(" + cut_text.lower() + r"([\s.,;!?]|$))(([\s., ;!?]*.*)|$)"
            result = re.sub(regex, r"\1\5", result, flags=re.I)
        return result

    def __preprocessor(self, query):
        self._timer_pre.start()
        self.__original_query = query
        if patterns_json.get('pre_before_cut_text'): 
            query = self.__cut_text(patterns_json['pre_before_cut_text'], query)
        if patterns_json.get('pre_before_replace_text'): 
            query = self.__replace_text(patterns_json['pre_before_replace_text'], query)            
        self.__pre_before_query = query
        
        self.__doc = self.__nlp(query)        
        self.__matches = self.__matcher(self.__doc)                   
        temp = defaultdict(list)          
        # Using extend 
        for elem in self.__matched_sents:
            temp[elem['text']].extend(elem['ents'])    
        self.__matched_sents = [{"ents":y, "text":x} for x, y in temp.items()]  

        self.__prepare_query_to_NLIDB()
        self._timer_pre.stop()

    def __create_table_and_insert_data(self, columns, result_set):
        # create the table to store the NLIDB result set
        sql = '''DROP TABLE IF EXISTS NLIDB_RESULT_SET; 
                 CREATE TABLE NLIDB_RESULT_SET (''' + \
                 ', '.join([column[0] + ' ' + column[1] for column in columns]) + ');'
        self.__SimpleSQLite.execute_sql(sql)
        #insert the result set passed from the NLIDB in the table
        sql = 'INSERT INTO NLIDB_RESULT_SET VALUES(' + ''.join(['?, ' for field in result_set[0]])[:-2] + ')'
        self.__SimpleSQLite.executemany_sql(sql, result_set)

    def _processor(self, columns, result_set):
        self._timer_pos.start()
        # processor steps
        #         
        # look for fields that GLAMORISE did not identify
        # because it is the work of the NLIDB (query part without aggregation)
        self.__pos_group_by_fields = [column[0].lower() for column in columns \
                                                  if column[0].lower() not in self._pre_group_by_fields +
                                                  self._pre_aggregation_fields + self._pre_time_scale_aggregation_fields +
                                                  self._pre_time_scale_group_by_fields]
        self.__prepare_aggregate_SQL(columns)
        if columns and result_set:
            self.__create_table_and_insert_data(columns, result_set)
        # prepare a pandas dataframe with the result
        self._timer_pos.stop()
        self._timer_exibition.start()
        if columns and result_set:
            self.__pd = self.__SimpleSQLite.pandas_dataframe(self.__pos_glamorise_sql)
        self._timer_exibition.stop()
        self._timer_total.stop()

    def execute(self, query):
        self.initialize_and_reset_attr()        
        self.__preprocessor(query)
        columns, result_set = self._nlidb_interface()
        # JSON columns names and types received by the NLIDB converted to list        
        if columns:
            columns = json.loads(columns)
        # JSON result set  received by the NLIDB converted to list        
        if result_set:
            result_set = json.loads(result_set)
        if self._timer_nlidb_json_result_set._start_time:    
            self._timer_nlidb_json_result_set.stop()
        #if result_set != []:
        self._processor(columns, result_set)

    @abc.abstractmethod
    def _nlidb_interface(self):
       pass

    @abc.abstractmethod
    def _translate_fields(self):
        pass

    def __prepare_aggregate_SQL(self, columns):
        #initialize clauses
        if self._pre_aggregation_fields:
            self.__select_clause = 'SELECT '
        #GLAMORISE has nothing to do, not an aggregation query    
        else:
            self.__pos_glamorise_sql = 'SELECT * FROM NLIDB_result_set'
            return    
        # is exists a group by field
        if self._pre_group_by_fields:
            self.__group_by_clause = 'GROUP BY '
            self.__order_by_clause = 'ORDER BY '
        if self._pre_having_fields:
            self.__having_clause = 'HAVING '

        # the group by fields impact the clauses SELECT, GROUP BY and ORDER BY and nested queries
        nested_group_by_field = ''
        for group_by_field in self._pre_group_by_fields:
            self.__select_clause += group_by_field + ', '
            nested_group_by_field += group_by_field + ', '
            self.__group_by_clause += group_by_field + ', '
            self.__order_by_clause += group_by_field + ', '

        #if it is an aggregation query:
        if self._pre_aggregation_fields:
            # the same for the post processing group by fields (field identified just by the NLIDB)
            for post_processing_group_by_field in self.__pos_group_by_fields:
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
        column_dict = {x[0] : x[1] for x in columns}    
        self._pos_aggregation_functions = deepcopy(self._pre_aggregation_functions)
        self._pos_aggregation_fields = deepcopy(self._pre_aggregation_fields)
        for i in range(len(self._pos_aggregation_functions)):            
            # changing from count to sum in numeroc fields
            if self._pos_aggregation_fields[i] in column_dict:
                if column_dict[self._pos_aggregation_fields[i]] in ['REAL', 'INTEGER'] and self._pos_aggregation_functions[i] == 'count':                    
                    self._pos_aggregation_functions[i] = 'sum'
            # building sql part for aggregate field and function        
            self.__select_clause += self._pos_aggregation_functions[i] + \
                                    '(' + self._pos_aggregation_fields[i] + ') as ' + \
                                    self._pos_aggregation_functions[i] + '_' + \
                                    self._pos_aggregation_fields[i] + ', '

            # building sql part for candidate aggregate field and function
            # it is done as a subquery, but if one day SQLite is substituted it could be done with nested functions
            # e.g. SELECT avg(sum(oil_production) as avg_sum_oil_production FROM NLIDB_result_set GROUP BY year
            if self._pos_aggregation_fields[i] in self._pre_time_scale_aggregation_fields:
                j = self._pre_time_scale_aggregation_fields.index(self._pos_aggregation_fields[i])
                self.__from_clause = ' FROM (SELECT ' + nested_group_by_field + self._pre_time_scale_aggregation_functions[j] + '(' + \
                                     self._pos_aggregation_fields[i] + ') as ' + \
                                     self._pos_aggregation_fields[i] + ' FROM NLIDB_result_set'
                self.__from_clause += ' GROUP BY ' + nested_group_by_field + \
                                      ', '.join(self._pre_time_scale_group_by_fields) + ') '

            # if there is no candidate fields and function, it is a common FROM without subquery
            else:
                self.__from_clause = ' FROM NLIDB_result_set '


        # building the HAVING clause having field, followed by operator, followed by value
        for i in range(len(self._pre_having_fields)):
            # we have to change the use of aggregate function in the future
            self.__having_clause += self._pos_aggregation_functions[i] + \
                                    '(' + self._pre_having_fields[i] + ') ' + self._pre_having_conditions[i] + ' ' \
                                    + self._pre_having_values[i] + ' and '

        # cut the ", " or " and " at the end of each string
        self.__select_clause = self.__select_clause[0:-2]
        self.__group_by_clause = self.__group_by_clause[0:-2]
        self.__having_clause = self.__having_clause[0:-5]
        self.__order_by_clause = self.__order_by_clause[0:-2]

        #GLAMORISE has nothing to do, not an aggregation query
        #if self.__select_clause == '':
        #    self.__select_clause = 'SELECT * FROM NLIDB_result_set'

        # build the final query
        self.__pos_glamorise_sql = (self.__select_clause + self.__from_clause + self.__group_by_clause + ' ' + \
                     self.__having_clause + ' ' + self.__order_by_clause).replace("  ", " ").strip()

    def dump(self, sub_str):
        for attr in dir(self):            
            if attr.startswith(sub_str) and getattr(self, attr):
                if attr.endswith('_sql'):
                    print("\n%s = %r\n" % (attr, getattr(self, attr)))
                else:
                    print("%s = %r" % (attr, getattr(self, attr)))
    
    def print_timers(self):
        print("timer_pre: {:.2f} sec".format(self._timer_pre.last))
        print("timer_nlidb_execution_first_and_second_attempt: {:.2f} sec".format(self._timer_nlidb_execution_first_and_second_attempt.last))    
        print("timer_nlidb_execution_third_attempt: {:.2f} sec".format(self._timer_nlidb_execution_third_attempt.last))           
        print("timer_nlidb_json_result_set: {:.2f} sec".format(self._timer_nlidb_json_result_set.last))
        print("timer_pos: {:.2f} sec".format(self._timer_pos.last))
        print("timer_exibition: {:.2f} sec".format(self._timer_exibition.last))

    def __del__(self):
        # when the object is destroyed drop the table that was used to generate the GLAMORISE result
        sql = 'DROP TABLE IF EXISTS NLIDB_RESULT_SET;'
        self.__SimpleSQLite.execute_sql(sql)
        os.remove('./datasets/glamorise.db')
