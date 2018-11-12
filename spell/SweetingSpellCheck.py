"""Spell Checker."""

import collections
import os
import re
from functools import cmp_to_key
from itertools import product
from flask import current_app


VERBOSE = True
vowels = set('aeiouy')
alphabet = set('abcdefghijklmnopqrstuvwxyz')
this_dir = os.path.dirname(__file__)
# IO


def log(*args):
    """Loggins."""
    if VERBOSE:
        print(''.join([str(x) for x in args]))


def words(text):
    """Filter body of text for words."""
    return re.findall('[a-z]+', text.lower())


def train(text, model=None):
    """Generate or update a word model (dictionary of word:frequency)."""
    model = collections.defaultdict(lambda: 0) if model is None else model
    for word in words(text):
        model[word] += 1
    return model


def train_from_files(file_list, model=None):
    """Training from files."""
    for f in file_list:
        model = train(open(f).read(), model)
    return model


# UTILITY FUNCTIONS


def numberofdupes(string, idx):
    """Return the number of times in a row the letter at index idx is duplicated."""
    # "abccdefgh", 2  returns 1
    initial_idx = idx
    last = string[idx]
    while idx + 1 < len(string) and string[idx + 1] == last:
        idx += 1
    return idx - initial_idx


def hamming_distance(word1, word2):
    """Hamming distance."""
    if word1 == word2:
        return 0
    dist = sum(map(str.__ne__, word1[:len(word2)], word2[:len(word1)]))
    dist = max([len(word2), len(word1)]) if not dist else dist + \
        abs(len(word2) - len(word1))
    return dist


def frequency(word, word_model):
    """Frequence."""
    return word_model.get(word, 0)


# POSSIBILITIES ANALYSIS


def variants(word):
    """Get all possible variants for a word."""
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [a + b[1:] for a, b in splits if b]
    transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b) > 1]
    replaces = [a + c + b[1:] for a, b in splits for c in alphabet if b]
    inserts = [a + c + b for a, b in splits for c in alphabet]
    return set(deletes + transposes + replaces + inserts)


def double_variants(word):
    """Get variants for the variants for a word."""
    return set(s for w in variants(word) for s in variants(w))


def reductions(word):
    """Return flat option list of all possible variations of the word by removing duplicate letters."""
    word = list(word)
    # ['h','i', 'i', 'i'] becomes ['h', ['i', 'ii', 'iii']]
    for idx, l in enumerate(word):
        n = numberofdupes(word, idx)
        # if letter appears more than once in a row
        if n:
            # generate a flat list of options ('hhh' becomes ['h','hh','hhh'])
            # only take up to 3, there are no 4 letter repetitions in english
            flat_dupes = [l * (r + 1) for r in range(n + 1)][:3]
            # remove duplicate letters in original word
            for _ in range(n):
                word.pop(idx + 1)
            # replace original letter with flat list
            word[idx] = flat_dupes

    # ['h',['i','ii','iii']] becomes 'hi','hii','hiii'
    for p in product(*word):
        yield ''.join(p)


def vowelswaps(word):
    """Return flat option list of all possible variations of the word by swapping vowels."""
    word = list(word)
    # ['h','i'] becomes ['h', ['a', 'e', 'i', 'o', 'u', 'y']]
    for idx, l in enumerate(word):
        if type(l) == list:
            pass  # dont mess with the reductions
        elif l in vowels:
            # if l is a vowel, replace with all possible vowels
            word[idx] = list(vowels)

    # ['h',['i','ii','iii']] becomes 'hi','hii','hiii'
    for p in product(*word):
        yield ''.join(p)


def both(word):
    """Permute all combinations of reductions and vowelswaps."""
    for reduction in reductions(word):
        for variant in vowelswaps(reduction):
            yield variant


# POSSIBILITY CHOOSING


def suggestions(word, real_words, short_circuit=True):
    """Get best spelling suggestion for word return on first match if short_circuit is true,
    otherwise collect all possible suggestions."""
    word = word.lower()
    if short_circuit:  # setting short_circuit makes the spellchecker much faster, but less accurate in some cases
        return (
            {word} & real_words or  # caps     "inSIDE" => "inside"
            # repeats  "jjoobbb" => "job"
            set(reductions(word)) & real_words or
            # vowels   "weke" => "wake"
            set(vowelswaps(word)) & real_words or
            # other    "nonster" => "monster"
            set(variants(word)) & real_words or
            # both     "CUNsperrICY" => "conspiracy"
            set(both(word)) & real_words or
            # other    "nmnster" => "manster"
            set(double_variants(word)) & real_words or {'NO SUGGESTION'}
        )
    else:
        return (
            {word} & real_words or (
                set(reductions(word)) | set(vowelswaps(word)) | set(
                    variants(word)) | set(both(word)) | set(double_variants(word))
            ) & real_words or {'NO SUGGESTION'}
        )


def best(inputted_word, suggestions, word_model=None):
    """Choose the best suggestion in a list based on lowest hamming distance from original word, or based on frequency if word_model is provided."""

    suggestions = list(suggestions)

    def comparehamm(one, two):
        score1 = hamming_distance(inputted_word, one)
        score2 = hamming_distance(inputted_word, two)
        return (score1 - score2)
        # return cmp_to_key(score1, score2)  # lower is better

    def comparefreq(one, two):
        score1 = frequency(one, word_model)
        score2 = frequency(two, word_model)
        return (score2 - score1)
        # return cmp_to_key(score2, score1)  # higher is better

    freq_sorted = sorted(suggestions, key=cmp_to_key(comparefreq))[
        0:]  # take the top 10
    hamming_sorted = sorted(suggestions, key=cmp_to_key(comparehamm))[
        0:]  # take the top 10
    # current_app.logger.info('FREQ', freq_sorted)
    # current_app.logger.info('HAM', hamming_sorted)
    # current_app.logger.info('freqsorted: ' + str(hamming_sorted))
    return hamming_sorted[0]


class SweetingSpellCheck:
    """Init the word frequency model with a simple list of all possible words."""

    word_model = train(
        open(os.path.join(this_dir, '../data/dictionary.txt')).read())
    # real_words = set(word_model)

    # add other texts here, they are used to train the word frequency model
    texts = [
        os.path.join(this_dir, '../data/sherlockholmes.txt'),
        os.path.join(this_dir, '../data/lemmas.txt'),
        os.path.join(this_dir, '../data/drugs.txt'),
    ]
    # enhance the model with real bodies of english so we know which words are more common than others
    word_model = train_from_files(texts, word_model)
    real_words = set(word_model)

    log('Total Word Set: ', len(word_model))
    log('Model Precision: %s' %
        (float(sum(word_model.values())) / len(word_model)))

    def correct_spell(self, word):
        """Spell correction."""
        # possibilities = suggestions(word, self.real_words, short_circuit=False)
        short_circuit_result = suggestions(
            word, self.real_words, short_circuit=True)
        # current_app.logger.info('short circuit : ' + str(short_circuit_result))
        return best(word, short_circuit_result, self.word_model)
