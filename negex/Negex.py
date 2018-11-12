# -*- coding: utf-8 -*-
"""Negex."""
import re


def sort_rules(rule_list):
    r"""Return sorted list of rules.

    Rules should be in a tab-delimited format: 'rule\t\t[four letter negation tag]'
    Sorts list of rules descending based on length of the rule,
    splits each rule into components, converts pattern to regular expression,
    and appends it to the end of the rule.
    """
    rule_list.sort(key=len, reverse=True)
    sorted_list = []
    for rule in rule_list:
        s = rule.strip().split('\t')
        split_trig = s[0].split()
        trig = r'\s+'.join(split_trig)
        pattern = r'\b(' + trig + r')\b'
        s.append(re.compile(pattern, re.IGNORECASE))
        sorted_list.append(s)
    return sorted_list


class NegTagger(object):
    """Take a sentence and tag negation terms and negated phrases.

    Keyword arguments:
    sentence -- string to be tagged
    phrases  -- list of phrases to check for negation
    rules    -- list of negation trigger terms from the sort_rules function
    negP     -- tag 'possible' terms as well (default = True)
    """

    def __init__(self, sentence='', phrases=None, rules=None, negp=True):
        """Initialization."""
        self.__sentence = sentence
        self.__phrases = phrases
        self.__rules = rules
        self.__negTaggedSentence = ''
        self.__scopesToReturn = []
        self.__negationFlag = None

        filler = '_'

        for rule in self.__rules:
            reformat_rule = re.sub(r'\s+', filler, rule[0].strip())
            self.__sentence = rule[3].sub(
                ' ' + rule[2].strip() + reformat_rule +
                rule[2].strip() + ' ', self.__sentence
            )
        for phrase in self.__phrases:
            phrase = re.sub(r'([.^$*+?{\\|()[\]])', r'\\\1', phrase)
            split_phrase = phrase.split()
            joiner = r'\W+'
            joined_pattern = r'\b' + joiner.join(split_phrase) + r'\b'
            re_pattern = re.compile(joined_pattern, re.IGNORECASE)
            m = re_pattern.search(self.__sentence)
            if m:
                self.__sentence = self.__sentence.replace(
                    m.group(0), '[PHRASE]' + re.sub(r'\s+', filler,
                                                    m.group(0).strip()) + '[PHRASE]'
                )


#        Exchanges the [PHRASE] ... [PHRASE] tags for [NEGATED] ... [NEGATED]
#        based on PREN, POST rules and if negPoss is set to True then based on
#        PREP and POSP, as well.
#        Because PRENEGATION [PREN} is checked first it takes precedent over
#        POSTNEGATION [POST]. Similarly POSTNEGATION [POST] takes precedent over
#        POSSIBLE PRENEGATION [PREP] and [PREP] takes precedent over POSSIBLE
#        POSTNEGATION [POSP].

        overlap_flag = 0
        pren_flag = 0
        post_flag = 0
        pre_possible_flag = 0
        post_possible_flag = 0

        sentence_tokens = self.__sentence.split()
        sentence_portion = ''
        ascopes = []
        sb = []
        # check for [PREN]
        for i in range(len(sentence_tokens)):
            if sentence_tokens[i][:6] == '[PREN]':
                pren_flag = 1
                overlap_flag = 0

            if sentence_tokens[i][:6] in ['[CONJ]', '[PSEU]', '[POST]', '[PREP]', '[POSP]']:
                overlap_flag = 1

            if i + 1 < len(sentence_tokens):
                if sentence_tokens[i + 1][:6] == '[PREN]':
                    overlap_flag = 1
                    if sentence_portion.strip():
                        ascopes.append(sentence_portion.strip())
                    sentence_portion = ''

            if pren_flag == 1 and overlap_flag == 0:
                sentence_tokens[i] = sentence_tokens[i].replace(
                    '[PHRASE]', '[NEGATED]')
                sentence_portion = sentence_portion + ' ' + sentence_tokens[i]

            sb.append(sentence_tokens[i])

        if sentence_portion.strip():
            ascopes.append(sentence_portion.strip())

        sentence_portion = ''
        sb.reverse()
        sentence_tokens = sb
        sb2 = []
        # Check for [POST]
        for i in range(len(sentence_tokens)):
            if sentence_tokens[i][:6] == '[POST]':
                post_flag = 1
                overlap_flag = 0

            if sentence_tokens[i][:6] in ['[CONJ]', '[PSEU]', '[PREN]', '[PREP]', '[POSP]']:
                overlap_flag = 1

            if i + 1 < len(sentence_tokens):
                if sentence_tokens[i + 1][:6] == '[POST]':
                    overlap_flag = 1
                    if sentence_portion.strip():
                        ascopes.append(sentence_portion.strip())
                    sentence_portion = ''

            if post_flag == 1 and overlap_flag == 0:
                sentence_tokens[i] = sentence_tokens[i].replace(
                    '[PHRASE]', '[NEGATED]')
                sentence_portion = sentence_tokens[i] + ' ' + sentence_portion

            sb2.insert(0, sentence_tokens[i])

        if sentence_portion.strip():
            ascopes.append(sentence_portion.strip())

        sentence_portion = ''
        self.__negTaggedSentence = ' '.join(sb2)

        if negp:
            sentence_tokens = sb2
            sb3 = []
            # Check for [PREP]
            for i in range(len(sentence_tokens)):
                if sentence_tokens[i][:6] == '[PREP]':
                    pre_possible_flag = 1
                    overlap_flag = 0

                if sentence_tokens[i][:6] in ['[CONJ]', '[PSEU]', '[POST]', '[PREN]', '[POSP]']:
                    overlap_flag = 1

                if i + 1 < len(sentence_tokens):
                    if sentence_tokens[i + 1][:6] == '[PREP]':
                        overlap_flag = 1
                        if sentence_portion.strip():
                            ascopes.append(sentence_portion.strip())
                        sentence_portion = ''

                if pre_possible_flag == 1 and overlap_flag == 0:
                    sentence_tokens[i] = sentence_tokens[i].replace(
                        '[PHRASE]', '[POSSIBLE]')
                    sentence_portion = sentence_portion + \
                        ' ' + sentence_tokens[i]

                sb3 = sb3 + ' ' + sentence_tokens[i]

            if sentence_portion.strip():
                ascopes.append(sentence_portion.strip())

            sentence_portion = ''
            sb3.reverse()
            sentence_tokens = sb3
            sb4 = []
            # Check for [POSP]
            for i in range(len(sentence_tokens)):
                if sentence_tokens[i][:6] == '[POSP]':
                    post_possible_flag = 1
                    overlap_flag = 0

                if sentence_tokens[i][:6] in ['[CONJ]', '[PSEU]', '[PREN]', '[PREP]', '[POST]']:
                    overlap_flag = 1

                if i + 1 < len(sentence_tokens):
                    if sentence_tokens[i + 1][:6] == '[POSP]':
                        overlap_flag = 1
                        if sentence_portion.strip():
                            ascopes.append(sentence_portion.strip())
                        sentence_portion = ''

                if post_possible_flag == 1 and overlap_flag == 0:
                    sentence_tokens[i] = sentence_tokens[i].replace(
                        '[PHRASE]', '[POSSIBLE]')
                    sentence_portion = sentence_tokens[i] + \
                        ' ' + sentence_portion

                sb4.insert(0, sentence_tokens[i])

            if sentence_portion.strip():
                ascopes.append(sentence_portion.strip())

            self.__negTaggedSentence = ' '.join(sb4)

        if '[NEGATED]' in self.__negTaggedSentence:
            self.__negationFlag = 'negated'
        elif '[POSSIBLE]' in self.__negTaggedSentence:
            self.__negationFlag = 'possible'
        else:
            self.__negationFlag = 'affirmed'

        self.__negTaggedSentence = self.__negTaggedSentence.replace(
            filler, ' ')

        for line in ascopes:
            tokens_to_return = []
            this_line_tokens = line.split()
            for token in this_line_tokens:
                if token[:6] not in ['[PREN]', '[PREP]', '[POST]', '[POSP]']:
                    tokens_to_return.append(token)
            self.__scopesToReturn.append(' '.join(tokens_to_return))

    def get_neg_tagged_sentence(self):
        """Negation tagged sentence."""
        return self.__negTaggedSentence

    def get_negation_flag(self):
        """Negation flag."""
        return self.__negationFlag

    def get_scopes(self):
        """Return scopes."""
        return self.__scopesToReturn

    def __str__(self):
        """String formatter."""
        text = self.__negTaggedSentence
        text += '\t' + self.__negationFlag
        text += '\t' + '\t'.join(self.__scopesToReturn)
