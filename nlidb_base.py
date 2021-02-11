import abc
import re
import spacy

class NlidbBase(metaclass=abc.ABCMeta):    

    def __init__(self):
        self._nlp = None

    def _alternative_compound_name(self, str, sep):
        words = re.split(' |_', str)
        if 'of' in words:
            ## reversing the words using reversed() function
            words = list(reversed(words))
            words.remove('of')
            ## joining the words and printing
            return sep.join(words)
        else:    
            ## reversing the words using reversed() function
            words = list(reversed(words))
            ## joining the words and printing
            return (sep + "of " + sep).join(words)
    
    # has to use the medium model (en_core_web_md)
    # the small has no word vectors for similarity
    def _find_by_similarity(self, str1, list, lang="en_core_web_md"): 
        if not self._nlp:
            self._nlp = spacy.load(lang)  # make sure to use larger model!        
        doc1 = self._nlp(str1)
        similarity = 0
        similar_field = ''
        for str2 in list:            
            doc2 = self._nlp(str2.lower().replace('_', ' ').replace('.', ' '))
            new_similarity = doc1.similarity(doc2)
            if new_similarity > similarity:
                similarity = new_similarity
                similar_field = str2
        return similar_field


    def field_synonym(self, synonym, replace_dot = True):
        # responsible for the translation of the field to the appropriated column
        try:            
            field = self._query_specific_synonym(synonym)

            #if field is not found, use the word vector similarity to find the closest one
            if not field:
                synonym_list = self._query_all_synonyms()                
                synonym = self._find_by_similarity(synonym, synonym_list)
                field = self._query_specific_synonym(synonym)

            if replace_dot:
                field = field.replace('.', '_')
            return field
        except Exception as e:
            print('Exception: ', e)
            return synonym

    @abc.abstractmethod
    def execute_query(self, nlq):
        pass    