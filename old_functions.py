import nltk
# nltk.download('wordnet')
from nltk.corpus import wordnet as wn


def matcher(self, patterns):
    for pattern in patterns:
        self.__matcher.add(str(patterns), None, pattern)
        matches = self.__matcher(self.__doc)
        if matches != []:
            return True
    return False

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