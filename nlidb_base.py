import abc
import re
import spacy

class NlidbBase(metaclass=abc.ABCMeta):    

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
        nlp = spacy.load(lang)  # make sure to use larger model!        
        doc1 = nlp(str1)
        similarity = 0
        similar_field = ''
        for str2 in list:
            doc2 = nlp(str2)
            new_similarity = doc1.similarity(doc2)
            if new_similarity > similarity:
                similarity = new_similarity
                similar_field = str2
        return similar_field


    @abc.abstractmethod
    def field_synonym(self):
        pass

    @abc.abstractmethod
    def execute_query(self, nlq):
        pass    