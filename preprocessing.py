# coding: utf-8
"""Text Preprocessor."""
import os
import pickle
import re

from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer

import inflect
from segmenter import split_single

from .spell.SweetingSpellCheck import SweetingSpellCheck

this_dir = os.path.dirname(__file__)

sweetingSpellCheck = SweetingSpellCheck()
lemmas = WordNetLemmatizer()
stemmer = PorterStemmer()
inflectengine = inflect.engine()
final_stop_words = []

with open(os.path.join(this_dir, 'data/stopwords.txt'), 'r') as file:
    for word in file.readlines():
        final_stop_words.append(word.strip())
final_stop_words.remove('and')
final_stop_words.remove('or')
final_stop_words.remove('not')

with open(os.path.join(this_dir, 'data/apostrophe.pkl'), 'rb') as file:
    appos = pickle.load(file)
    del appos['cause']


def detect_sentence_boundary(text):
    """Sentence boundary detection pipeline."""
    return [sentence for sentence in split_single(
        text) if len(sentence.strip()) > 0]


def remove_punctuations(sentence, keep_apostrophe=True):
    """Sanitize string by removing punctuations."""
    if keep_apostrophe:
        pattern = r'[?|$|*|%|@|(|)|~|-]'
    else:
        pattern = r'[^a-zA-Z0-9,&]'
    return re.sub(pattern, r' ', sentence)


def spell_check(text: str) -> str:
    """Spell checker."""
    return sweetingSpellCheck.correct_spell(text)


def change_case(text: str, style='lower') -> str:
    """Match case."""
    if (style == 'lower'):
        case_word = remove_blanks(text.lower())
    else:
        case_word = remove_blanks(text.upper())
    return case_word


def remove_blanks(text: str) -> str:
    """Trim the token."""
    return text.strip()


def remove_inner_blanks(text: str) -> str:
    """Trim inner tokens."""
    return ' '.join([word.strip() for word in text.split(' ') if word.strip() != ''])


def lemma(text: str) -> str:
    """Lemmatizer."""
    return lemmas.lemmatize(text)


def stem(text):
    """Porter stemmer."""
    return stemmer.stem(text)


def normalize(text):
    """Normalize the text."""
    new_text = re.sub('\}', '', text)
    new_text = re.sub('\{', '', new_text)
    new_text = re.sub('\(.*\)', '', new_text)
    new_text = re.sub('\(', '', new_text)
    new_text = re.sub('\)', '', new_text)
    new_text = re.sub('\[', '', new_text)
    new_text = re.sub('\]', '', new_text)
    new_text = re.sub('\+', '', new_text)
    new_text = re.sub(' \& ', ' and ', new_text)
    return new_text


def remove_stop_words(text):
    """Remove character not related to alphabets."""
    return ' '.join(
        [word for word in text.split(' ') if word not in final_stop_words])


def is_stop_word(word):
    """Change status of the token."""
    return word in final_stop_words


def convert_to_singular(text):
    """Convert plural to singular."""
    if inflectengine.singular_noun(text):
        return inflectengine.singular_noun(text).lower()
    else:
        return text.lower()


def apostrophe_replacer(text):
    """Remove Apostrophe."""
    for apo in appos:
        if text.rfind(apo) != -1:
            text = text.replace(apo, appos[apo].lower())
    return text
