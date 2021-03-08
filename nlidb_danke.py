from simple_sqlite import SimpleSQLite
import json
from nlidb_base import NlidbBase
# importing the requests library 
import requests
import spacy
from nltk.tokenize import word_tokenize

# Simple class to act as a NLIDB
class NlidDanke(NlidbBase):

    def __init__(self):
        # open the database
        # self.__SimpleSQLite = SimpleSQLite('./datasets/mock_nlidb_anp.db')
        self._url = "https://danke.tecgraf.puc-rio.br/danke-api-anp/"
        self._synonyms_data = {}
        sp = spacy.load('en_core_web_sm')
        self._all_stopwords = sp.Defaults.stop_words
 

    def _query_specific_synonym(self, synonym):
        if(self._synonyms_data):
            synonym_items = word_tokenize(synonym)
            synonym_items= [word for word in synonym_items if not word in self._all_stopwords]  
            return next(c_name for c_name,keywords in self._synonyms_data.items() if all(elem in keywords for elem in synonym_items))
        return

    def _query_all_synonyms(self):
        return self._synonyms_data.keys()  

    def execute_query(self, nlq, timer_nlidb_execution_first_and_second_attempt,  timer_nlidb_json_result_set):
        timer_nlidb_execution_first_and_second_attempt.start()
        columns = result_set = sql_result =''
        try:
            # get the conceptual query
            URL_GET_CQ = self._url+"search/queries"
            PARAMS = {'q':nlq}
            r_cq = requests.get(url = URL_GET_CQ, params = PARAMS)
            cq = r_cq.json()[0]
            #get the result of the cq
            URL_GET_RESULT = self._url+"search/results"
            r_result = requests.post(url = URL_GET_RESULT, json = cq, params = {'offset':-1,'limit':-1})
            result_json = r_result.json()
            result_set = []
            columns = []
            self._synonyms_data = {}
            columns_to_ignore = []


            # /properties ids list<string>
            #populate the columns and the synonyms data
            for idx,row_desc_danke in enumerate(result_json['description']):                
                entityId = row_desc_danke['entityId']                
                entityBucket = next(e for e in cq['coreNucleus'] if e['entityBucket']['entityIdentifier']==entityId)
                keywords =entityBucket['entityBucket']['coveredKeywords']
                if len(keywords) != 0:
                    colum_name = 'e'+entityId+"_"+self.__get_name(row_desc_danke['entityLabel'])
                    self._synonyms_data[colum_name] = entityBucket['entityBucket']['coveredKeywords']
                    columns.append([colum_name,'TEXT'])
                else:
                    columns_to_ignore.append(idx)
                for row_desc_group in row_desc_danke['propertyGroups']:
                    for row_desc_property in row_desc_group['properties']:
                        propertyID = row_desc_property['id']
                        colum_name  = 'p'+propertyID +"_"+ self.__get_name(row_desc_property['label'])
                        columns.append([colum_name,self.__get_property_datatype(propertyID)])
                        propertyBucket = next(p for p in entityBucket['properties'] if p['propertyIdentifier']==propertyID)
                        self._synonyms_data[colum_name] = propertyBucket['coveredKeywords']

            #self.__translate_XSD_datatype_to_sqlite('datatype')
            for row_danke in result_json['rows']:
                row = []
                for idx,row_entity_danke in enumerate(row_danke):
                    if idx not in columns_to_ignore:
                        row.append(row_entity_danke['value'])
                    for row_group in row_entity_danke['propertyGroups']:
                        for row_property in row_group:
                            row.append(row_property['value'])
                result_set.append(row)  

            timer_nlidb_json_result_set.start()
            
                                                                                  
            return columns, result_set, sql_result
        except Exception as e:
            print("Query not found: ", nlq)
            print("Query not found: ", e)
        finally:
            return columns, result_set, sql_result

    def __get_property_datatype(self, propID):
        URL_GET_CQ = self._url+"explorer/properties"
        PARAMS = {'ids':[propID]}
        r_property = requests.get(url = URL_GET_CQ, params = PARAMS)
        property = r_property.json()[0]['value'][0]
        return self.__translate_XSD_datatype_to_sqlite(property['ranges'][0])

    def __translate_XSD_datatype_to_sqlite(self, type):
        field_type = {
                    'XSD_DECIMAL' : 'REAL',
                    'XSD_DATE' : 'TEXT',
                    'XSD_STRING' : 'TEXT',
                    'XSD_BOOLEAN': 'INTEGER' }
        return field_type[type] 

    def __get_name(self, label):
       return "_".join(k.lower() for k in label.split())