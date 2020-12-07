#
# Developed by Alexandre Novello (PUC-Rio)
#
#!pip install spacy==2.2.4
#!pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.2.5/en_core_web_sm-2.2.5.tar.gz

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
from simple_sqllite import SimpleSQLLite

patterns_json_txt = """{
  "units_of_measurement" : ["cubic meters"],
    "default_pattern" : [{"POS": "ADV", "OP": "*"}, {"POS": "ADJ", "OP": "*"}, {"POS": "NOUN", "LOWER":{"NOT_IN": ["number"]}}],
    "patterns" : {
        "than options" : {
            "reserved_words" : ["more than", "greater than", "less than", "equal to", "greater than or equal to", "less than or equal to"],
            "having_conditions" : [">", ">", "<", "=", ">=", "<="],
            "specific_pattern" : [{"LIKE_NUM": true}, {"POS": "ADV", "OP": "*"}, {"POS": "ADJ", "OP": "*"}, {"POS": "NOUN", "OP": "*"}, {"POS": "NOUN"}],
            "cut_text" : false
        },
        "group by" : {
            "reserved_words" : ["by", "per", "for each", "of each"],
            "group_by" : true,            
            "cut_text" : false
        },
        "group by and" : {
            "reserved_words" : ["by", "per", "for each", "of each"],
            "group_by" : true,
            "specific_pattern" : [{"POS": "ADV", "OP": "*"}, {"POS": "ADJ", "OP": "*"}, {"POS": "NOUN", "LOWER":{"NOT_IN": ["number"]}}, {"LOWER" : "and"}, {"POS": "NOUN", "LOWER":{"NOT_IN": ["number"]}}],
            "cut_text" : false            
        },
        "how options" : {
            "reserved_words" : ["how many", "how much"],
            "aggregation_functions" : ["count", "sum"],
            "cut_text" : true
        },
        "other count" : {
            "reserved_words" : ["number of", "number of the"],
            "aggregation_functions" : "count",
            "cut_text" : true
        },
        "other sum" : {
            "reserved_words" : ["total"],
            "aggregation_functions" : "sum",
            "cut_text" : true
        },      
        "average options" : {
            "reserved_words" : ["average", "avg", "mean"],
            "aggregation_functions" : "avg",
            "cut_text" : true
        },
        "superlative min" : {
            "reserved_words" : ["least", "smallest", "tiniest", "shortest", "cheapest", "nearest", "lowest", "worst", "newest", "min", "minimum"],
            "aggregation_functions" : "min",
            "cut_text" : true
        },
        "superlative max" : {
            "reserved_words" : ["most", "most number of", "biggest", "longest", "furthest", "highest", "tallest", "greatest", "best", "oldest", "max", "maximum"],
            "aggregation_functions" : "max",
            "cut_text" : true
        },
        "time scale options" : {
            "reserved_words" : ["daily", "monthly", "yearly"],
            "time_scale_replace_text" : {"daily" : "day", "monthly" : "month", "yearly" : "year"},
            "time_scale_aggregation_functions" : "sum",
            "cut_text" : false
        }
    }
}"""

patterns_json = json.loads(patterns_json_txt)


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
        self.matcher = Matcher(nlp.vocab)
        self.matcher.add(
            "CompoundMerger",
            None,
            [{'POS': 'NOUN', 'DEP': 'compound'},
           {'POS': 'NOUN'}],[{'POS': 'NOUN', 'LOWER':{'NOT_IN': ['number']}},
           {'LOWER': 'of', 'POS': 'ADP'},
           {'POS': 'NOUN'}]     
        )
 
 
 
class UnitsOfMeasurementMerger(Merger):    
    def __init__(self, nlp):    
        self._type = 'units_of_measurement'
        # Register a new token extension to flag units of measurement
        Token.set_extension("units_of_measurement", default=False, force=True)
        self.matcher = Matcher(nlp.vocab)
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

    def __init__(self, lang="en_core_web_sm"):
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
        self.__SimpleSQLLite = SimpleSQLLite('./datasets/GLAMORISE.db')

    def initialize_and_reset_attr(self):
        self._aggregation_functions = []
        self._aggregation_fields = []
        self._group_by_fields = []

        self._time_scale_aggregation_functions = []
        self._time_scale_aggregation_fields = []
        self._time_scale_group_by_fields = []        
        
        self._having_fields = []
        self._having_conditions = []
        self._having_values = []
        self._having_units = []

        self.__cut_text = []
        self.__replaced_text = {}
        self.__group_by = False

        self.matched_sents = []  # Collect data of matched sentences to be visualized  
        
        self.__prepared_query = ''

        self.__select_clause = ''
        self.__from_clause = ''
        self.__group_by_clause = ''
        self.__having_clause = ''
        self.__order_by_clause = ''
        self.__sql = ''

        # fields revealed only in the NLIDB
        self.__post_processing_group_by_fields = []
        
        # create the pandas dataframe just if it called before being fed
        self.__pd = None

    @property
    def query(self):
        return self.__query

    @property
    def prepared_query(self):
        return self.__prepared_query

    @property
    def aggregation_functions(self):
        return self._aggregation_functions.copy()

    @property
    def aggregation_fields(self):
        return self._aggregation_fields.copy()

    @property
    def group_by_fields(self):
        return self._group_by_fields.copy()

    @property
    def time_scale_aggregation_functions(self):
        return self._time_scale_aggregation_functions.copy()

    @property
    def time_scale_aggregation_fields(self):
        return self._time_scale_aggregation_fields.copy()

    @property
    def time_scale_group_by_fields(self):
        return self._time_scale_group_by_fields.copy()

    @property
    def having_fields(self):
        return self._having_fields.copy()

    @property
    def having_conditions(self):
        return self._having_conditions.copy()

    @property
    def having_values(self):
        return self._having_values.copy()

    @property
    def having_units(self):
        return self.__having_units.copy()

    @property
    def having_units(self):
        return self._having_units.copy()

    @property
    def cut_text(self):
        return self.__cut_text

    @property
    def replaced_text(self):
        return self.__replaced_text

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
        return self.__post_processing_group_by_fields.copy()

    def __build_field(self, span, field, pos = '', unit_of_measurement = False, time_scale_group_by_field = '', replace_text = ''):                
        if time_scale_group_by_field != '':
            self._time_scale_group_by_fields.append(time_scale_group_by_field)
            self.__replaced_text[replace_text] = time_scale_group_by_field
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
                elif field  == 'having_fields':
                    self._having_fields = self._aggregation_fields.copy()
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
        displacy.render(self.matched_sents, style="ent", manual=True, jupyter=True)

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
        if patterns_json['patterns'][pattern].get('cut_text') and patterns_json['patterns'][pattern]['cut_text']:
            self.cut_text.append(reserved_word) 
        index = patterns_json['patterns'][pattern]['reserved_words'].index(reserved_word)

        options = [{'json_var' : 'having_conditions', 'label' : 'HAVING | CONDITION'},
                {'json_var' : 'aggregation_functions', 'label' : 'AGGREGATION FUNCTION'},
                {'json_var' : 'group_by', 'label' : 'GROUP BY'},
                {'json_var' : 'time_scale_aggregation_functions', 'label' : 'TIMESCALE'}]
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
                    self.__group_by = patterns_json['patterns'][pattern]['group_by']
        
        match_ents = [{
            "start": span.start_char - sent.start_char,
            "end": span.end_char - sent.start_char,
            "label": label,
        }]    
        
        self.matched_sents.append({"text": sent.text, "ents": match_ents})
        if patterns_json['patterns'][pattern].get('aggregation_functions'):
            self.__build_field(span, 'aggregation_fields', 'NOUN')
        elif patterns_json['patterns'][pattern].get('group_by'):
            self.__build_field(span, 'group_by_fields', 'NOUN')      
        elif patterns_json['patterns'][pattern].get('having_conditions'):
            self.__build_field(span, 'having_fields', 'NOUN')
            self.__build_field(span, 'having_units', 'NOUN', True)    
            self.__build_field(span, 'having_values', 'NUM')        
        elif patterns_json['patterns'][pattern].get('time_scale_replace_text'):
            self.__build_field(span, 'time_scale_aggregation_fields', 'NOUN')
            self.__build_field(span, 'having_units', 'NOUN', True)    
            replace_text_token = (patterns_json['patterns'][pattern]['reserved_words'][index])
            self.__build_field(span, 'time_scale_group_by_fields', 
                        time_scale_group_by_field = patterns_json['patterns'][pattern]['time_scale_replace_text'][replace_text_token],
                        replace_text = replace_text_token)     

    # def __build_field(self, token, field_property):
    #     accum_pre = accum_pos = ''
    #     field = token.lemma_
    #     # check how to remove this for
    #     for child in token.children:
    #         # preparing reserved word "and" acting as reserved word "per" - exception            
    #         if child.dep_ == 'cc' and child.lemma_ == 'and':
    #             child.lemma_ = 'per'
            
    #     # append field in the appropriate list
    #     field_property.append(field)

    # def __iterator_has_next(self, iterator):
    #     try:
    #         next(iterator)
    #         return True
    #     except:
    #         return False

    # def __synthetic_tree_build_field(self, token, field_property):
    #     # check if it a group by field and is not an "and" reserved word
    #     if (field_property is self._group_by_fields and token.text != 'and') or not self.__iterator_has_next(
    #             token.ancestors):
    #         next_token_tree = token.children
    #     else:
    #         next_token_tree = token.ancestors
    #     for next_token in next_token_tree:
    #         # dealing with reserved word "and" acting as "per" - exception
    #         if field_property is self._group_by_fields and token.text == 'and':
    #             next_token = token.nbor()
    #         # look for a field just if the token is a noun
    #         if next_token.pos_ == 'NOUN':
    #             # add the field to the correct list
    #             self.__build_field(next_token, field_property)
    #             break

    # def __synthetic_tree_pattern_match(self, token, reserved_words, children_reserved_words=None,
    #                                    group_by=False):
    #     # check if token is in reserved word list
    #     if token.lemma_ in reserved_words:
    #         # if it is and exists an associated aggregate function
    #         if reserved_words[token.lemma_] is not None:
    #             # add it to the aggregation function list
    #             self.__aggregation_functions.append(reserved_words[token.lemma_])
    #         # set the group by flag
    #         self.__group_by = group_by
    #         # call the synthetic_tree_build_field passing the correct list do add the field
    #         if not group_by:
    #             self.__synthetic_tree_build_field(token, self._aggregation_fields)
    #         elif group_by:
    #             self.__synthetic_tree_build_field(token, self._group_by_fields)
    #         if children_reserved_words is None:
    #             self.__cut_text.append(token.text)
    #         else:
    #             children = list(token.children)
    #             for child in children:
    #                 if child.lemma_ in children_reserved_words:
    #                     self.__cut_text.append(child.text + ' ' + token.text)

    # def __adjective_to_noun_pattern_match(self, token):
    #     # temporal adjectives and associated noun dict
    #     adj_noun = {'daily': 'day', 'monthly': 'month', 'yearly': 'year'}
    #     # check if token is in reserved word list
    #     if token.lemma_ in adj_noun:
    #         noun = adj_noun[token.lemma_]
    #         # substitute the adjective by the correspondent noun
    #         self.__replaced_text[token.lemma_] = noun
    #         # add to the time scale group by field (subquery)
    #         self._time_scale_group_by_fields.append(noun)
    #         # if the above field is used in the group by, the aggregation function is sum
    #         self.__time_scale_aggregation_functions.append('sum')
    #         # add the field to the correct list
    #         self.__build_field(token.head, self._time_scale_aggregation_fields)

    # def __superlative_pattern_match(self, token):
    #     # min list
    #     min = ['least', 'smallest', 'tiniest', 'shortest', 'cheapest', 'nearest', 'lowest', 'worst', 'newest', 'min',
    #            'minimum']
    #     # mas list
    #     max = ['most', 'biggest', 'longest', 'furthest', 'highest', 'tallest', 'greatest', 'best', 'oldest', 'max',
    #            'maximum']
    #     # if token in min or max
    #     if token.text in max + min:
    #         self.__build_field(token.head, self._aggregation_fields)  # set the aggregate field
    #         self.__cut_text.append(token.text)  # set the text that should be cut
    #         if token.text in max:  # set the aggregation function
    #             self.__aggregation_functions.append('max')
    #         else:
    #             self.__aggregation_functions.append('min')

    # def __check_nnp_in_children(self, token):
    #     # check if any children is a proper noun
    #     for child in token.children:
    #         if child.tag_ == 'NNP':
    #             return True
    #     return False


    # def __token_scan(self):
    #     for token in self.__doc:
    #         # if it is a proper noun, go to next token
    #         if self.__check_nnp_in_children(token):
    #             continue

    #         # get the how many, how much pattern
    #         self.__synthetic_tree_pattern_match(token,
    #                                             {'many': 'count', 'number': 'count', 'much': 'sum'},
    #                                             ['how', 'of'])
    #         # get the average, mean pattern
    #         self.__synthetic_tree_pattern_match(token,
    #                                             {'average': 'avg', 'mean': 'avg', 'avg': 'avg'})
    #         # get the by, per pattern
    #         self.__synthetic_tree_pattern_match(token, {'by': None, 'per': None}, group_by=True)

    #         # get daily, monthly, yearly pattern
    #         self.__adjective_to_noun_pattern_match(token)

    #         # superlative min:  least, smallest, tiniest, shortest, cheapest, nearest, lowest, worst, newest
    #         # superlative max: most, biggest, longest, furthest, highest, tallest, greatest, best, oldest
    #         self.__superlative_pattern_match(token)


    # def __entity_scan(self):
    #     # get each recognized entity
    #     for entity in self.__doc.ents:
    #         # check if it is number like
    #         if entity.label_ in ['MONEY', 'QUANTITY', 'CARDINAL']:
    #             # check the pattern "greater|more than" and set having condition to ">"
    #             if entity[0].text in ['more', 'greater'] and entity[1].text == 'than':
    #                 self.__having_conditions.append('>')
    #                 prefix = entity[0].text + ' ' + entity[1].text
    #                 find_value = True
    #             # check the pattern "less than" and set having condition to "<"
    #             if entity[0].text == 'less' and entity[1].text == 'than':
    #                 self.__having_conditions.append('<')
    #                 prefix = entity[0].text + ' ' + entity[1].text
    #                 find_value = True
    #             # check the pattern "equal to" and set having condition to "="
    #             # not working because of spaCy faulty entity recognition
    #             if entity[0].text == 'equal' and entity[1].text == 'to':
    #                 self.__having_conditions.append('=')
    #                 prefix = entity[0].text + ' ' + entity[1].text
    #                 find_value = True

    #             # find and set the having condition
    #             if find_value:
    #                 having_value = ''
    #                 # examine each token inside the entity
    #                 for token in entity:
    #                     one_token_doc = self.__nlp(token.text)
    #                     # if the token alone is cardinal use it to build the having value
    #                     if one_token_doc[0].ent_type_ == 'CARDINAL':
    #                         having_value += ' ' + one_token_doc[0].text
    #                 # clear thousand and decimal separator and spaces and set the having value
    #                 self.__having_values.append(having_value.replace(',', '').replace('.', '').strip())
    #                 # replace text to leave just the measure unit and clear spaces
    #                 self.__having_units.append(entity.text.replace(having_value, '').replace(prefix, '').strip())
    #                 # assume that we are dealing ith the same fields,
    #                 # change this in the future to a more accurate answer
    #                 self._having_fields = self.aggregation_fields.copy()

    # def customized_displacy(self):
    #     # set the displacy parameters
    #     displacy.render(self.__doc, style='dep', jupyter=True,
    #                     options={'compact' : False, 'distance': 90, 'fine_grained': True,
    #                              'add_lemma': True, 'collapse_phrases': False})

    def __prepare_query_to_NLIDB(self):
        # set the query that is going to be passed to the NLIDB initially as the received query
        self.__prepared_query = self.__query
        # then cut the texts to be cut
        for cut_text in self.__cut_text:
            regex = r"(^|(.*?[\s.,;!?]+))(" + cut_text.lower() + r"([\s.,;!?]|$))(([\s., ;!?]*.*)|$)"
            self.__prepared_query = re.sub(regex, r"\1\5", self.__prepared_query, flags=re.I)
        # then replace the texts that must be replaced
        for replaced_text in self.__replaced_text:
            regex = r"(^|(.*?[\s.,;!?]+))(" + replaced_text.lower() + r")(([\s., ;!?]*.*)|$)"
            str = r"\1" + self.__replaced_text[replaced_text] + r"\5"
            self.__prepared_query = re.sub(regex, str, self.__prepared_query, flags=re.I)
        return self.__prepared_query

    def __preprocessor(self, query):
        self.__query = query
        self.__doc = self.__nlp(query)        
        self.__matches = self.__matcher(self.__doc)                   
        temp = defaultdict(list)          
        # Using extend 
        for elem in self.matched_sents:
            temp[elem['text']].extend(elem['ents'])    
        self.matched_sents = [{"ents":y, "text":x} for x, y in temp.items()]  

        self.__prepare_query_to_NLIDB()

    def __create_table_and_insert_data(self, columns, result_set):
        # create the table to store the NLIDB result set
        sql = '''DROP TABLE IF EXISTS NLIDB_RESULT_SET; 
                 CREATE TABLE NLIDB_RESULT_SET (''' + \
                 ', '.join([column[0] + ' ' + column[1] for column in columns]) + ');'
        self.__SimpleSQLLite.execute_sql(sql)
        #insert the result set passed from the NLIDB in the table
        sql = 'INSERT INTO NLIDB_RESULT_SET VALUES(' + ''.join(['?, ' for field in result_set[0]])[:-2] + ')'
        self.__SimpleSQLLite.executemany_sql(sql, result_set)

    def _processor(self, columns, result_set):
        # processor steps

        # the field translation is done by the child class that is aware of the NLIDB column names
        self._translate_all_fields()
        # look for fields that GLAMORISE did not identify
        # because it is the work of the NLIDB (query part without aggregation)
        self.__post_processing_group_by_fields = [column[0].lower() for column in columns \
                                                  if column[0].lower() not in self._group_by_fields +
                                                  self._aggregation_fields + self._time_scale_aggregation_fields +
                                                  self._time_scale_group_by_fields]
        self.__prepare_aggregate_SQL()
        self.__create_table_and_insert_data(columns, result_set)
        # prepare a pandas dataframe with the result
        self.__pd = self.__SimpleSQLLite.pandas_dataframe(self.__sql)

    def execute(self, query):
        self.initialize_and_reset_attr()        
        self.__preprocessor(query)
        columns, result_set = self._send_question_receive_answer()
        # JSON columns names and types received by the NLIDB converted to list        
        columns = json.loads(columns)
        # JSON result set  received by the NLIDB converted to list        
        result_set = json.loads(result_set)
        self._processor(columns, result_set)

    @abc.abstractmethod
    def _send_question_receive_answer(self):
       pass

    @abc.abstractmethod
    def _translate_fields(self):
        pass

    def __prepare_aggregate_SQL(self):
        #initialize clauses
        if self._aggregation_fields:
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
        if self._aggregation_fields:
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
        for i in range(len(self._aggregation_functions)):
            # building sql part for aggregate field and function
            self.__select_clause += self._aggregation_functions[i] + \
                                    '(' + self._aggregation_fields[i] + ') as ' + \
                                    self._aggregation_functions[i] + '_' + \
                                    self._aggregation_fields[i] + ', '

            # building sql part for candidate aggregate field and function
            # it is done as a subquery, but if one day SQLite is substituted it could be done with nested functions
            # e.g. SELECT avg(sum(oil_production) as avg_sum_oil_production FROM NLIDB_result_set GROUP BY year
            if self._aggregation_fields[i] in self._time_scale_aggregation_fields:
                j = self._time_scale_aggregation_fields.index(self._aggregation_fields[i])
                self.__from_clause = ' FROM (SELECT ' + nested_group_by_field + self._time_scale_aggregation_functions[j] + '(' + \
                                     self._aggregation_fields[i] + ') as ' + \
                                     self._aggregation_fields[i] + ' FROM NLIDB_result_set'
                self.__from_clause += ' GROUP BY ' + nested_group_by_field + \
                                      ', '.join(self._time_scale_group_by_fields) + ') '

            # if there is no candidate fields and function, it is a common FROM without subquery
            else:
                self.__from_clause = ' FROM NLIDB_result_set '


        # building the HAVING clause having field, followed by operator, followed by value
        for i in range(len(self._having_fields)):
            # we have to change the use of aggregate function in the future
            self.__having_clause += self._aggregation_functions[i] + \
                                    '(' + self._having_fields[i] + ') ' + self._having_conditions[i] + ' ' \
                                    + self._having_values[i] + ' and '

        # cut the ", " or " and " at the end of each string
        self.__select_clause = self.__select_clause[0:-2]
        self.__group_by_clause = self.__group_by_clause[0:-2]
        self.__having_clause = self.__having_clause[0:-5]
        self.__order_by_clause = self.__order_by_clause[0:-2]

        #GLAMORISE has nothing to do, not an aggregation query
        if self.__select_clause == '':
            self.__select_clause = 'SELECT * FROM NLIDB_result_set'

        # build the final query
        self.__sql = (self.__select_clause + self.__from_clause + self.__group_by_clause + ' ' + \
                     self.__having_clause + ' ' + self.__order_by_clause).replace("  ", " ").strip()

    def __del__(self):
        # when the object is destroyed drop the table that was used to generate the GLAMORISE result
        sql = 'DROP TABLE IF EXISTS NLIDB_RESULT_SET;'
        self.__SimpleSQLLite.execute_sql(sql)
