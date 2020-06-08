from spacy import displacy
import spacy
from spacy.matcher import Matcher


class Glamorise:

    # instance attribute
    def __init__(self, txt, lang="en"):
        self.__nlp = spacy.load(lang)
        self.__doc = self.__nlp(txt)
        self.__customize_stop_words
        self.__aggregate_function = ''
        self.__aggregate_field = ''
        self.__group_by_field = ''
        self.__having_field = ''
        self.__cut_text = []
        self.__group_by = False
        self.__having = ''
        self.__matcher = Matcher(self.__nlp.vocab)

    @property
    def aggregate_function(self):
        return self.__aggregate_function

    @property
    def aggregate_field(self):
        return self.__aggregate_field

    @property
    def group_by_field(self):
        return self.__group_by_field

    @property
    def having_field(self):
        return self.__having_field

    @property
    def cut_text(self):
        return self.__cut_text

    @property
    def group_by(self):
        return self.__group_by

    @property
    def having(self):
        return self.__having

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

    def build_field(self, token, type):
        print("token.ancestors", str(token.ancestors))
        for ancestor in token.ancestors:
            # set the field
            field = ancestor.lemma_
            accum = ''
            # look for compund terms
            for ancestor_children in ancestor.subtree:
                # get compound terms that are not proper noun
                if ancestor_children.dep_ == 'compound' and ancestor_children.tag_ != 'NNP':
                    accum = accum + ancestor_children.lemma_ + ' '
            field = accum + field
            if type == 'aggregate':
                self.__aggregate_field = field
            if type == 'group by':
                self.__group_by_field = field
            if type == 'having':
                self.__having_field = field
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

    def pattern_match(self, token, reserved_words, children_reserved_words=None,
                      group_by=False, having=''):
        if token.lemma_ in reserved_words:
            if reserved_words[token.lemma_] is not None:
                self.__aggregate_function = reserved_words[token.lemma_]
            self.__group_by = group_by
            self.__having = having
            if not group_by and having == '':
                self.build_field(token, type='aggregate')
            elif group_by:
                self.build_field(token, type='group by')
            elif having != '':
                self.build_field(token, type='having')
            if children_reserved_words is None:
                self.__cut_text.append(token.lemma_)
            else:
                children = list(token.children)
                for child in children:
                    if child.lemma_ in children_reserved_words:
                        self.__cut_text.append(child.lemma_ + ' ' + token.lemma_)

    def pattern_scan(self):
        for token in self.__doc:
            '''
            # get the how many, how much pattern
            if token.lemma_ in ['many', 'much']:      
              children = list(token.children)      
              for child in children:                
                if child.lemma_ == 'how':       
                  #set aggregate_function
                  if token.lemma_ == 'many':
                    self.__aggregate_function = 'count'  
                  elif  token.lemma_ == 'much':
                    self.__aggregate_function = 'sum'           
                  #set the text that will be removed from the query before passing to the NLIDB
                  self.__cut_text = child.lemma_ + ' ' + token.lemma_          
                  self.build_aggregate_field(token)
            '''
            # get the how many, how much pattern
            self.pattern_match(token,
                               {'many': 'count', 'number': 'count', 'much': 'sum'},
                               ['how', 'of'])

            # get the most, maximum, max pattern
            self.pattern_match(token,
                               {'most': 'max', 'maximum': 'max', 'max': 'max'})

            # get the least, minimum, min pattern
            self.pattern_match(token,
                               {'least': 'min', 'minimum': 'min', 'min': 'min'})

            # get the average, mean pattern
            self.pattern_match(token,
                               {'average': 'avg', 'mean': 'avg', 'avg': 'avg'})

            # get the by, per pattern
            self.pattern_match(token, {'by': None, 'per': None}, group_by=True)

            # get the greater than, more than pattern
            self.pattern_match(token, {'great': None, 'more': None}, having='+')

            # get the less than pattern
            self.pattern_match(token, {'less': None}, having='-')

            # get the equal to pattern
            self.pattern_match(token, {'equal': None}, having='=')

    def customized_displacy(self):
        displacy.render(self.__doc, style='dep', jupyter=True,
                        options={'distance': 90, 'fine_grained': True,
                                 'add_lemma': True, 'collapse_phrases': False})