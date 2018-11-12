# coding: utf-8
"""Models used in the algorithm."""
import collections
from typing import Dict, List

from tokenizer import split_contractions, word_tokenizer

Transformation = collections.namedtuple('Transformation', ['text', 'stage'])


class Token:
    """This class represents one word in a tokenized sentence."""

    def __init__(self, text: str, index: int, hidden=False):
        self.text: str = text
        self.index: int = index
        self.hidden: bool = hidden
        self.transform_history: List[Transformation] = [
            Transformation(text, 'original')]
        self.sentence: Sentence = None

    def __str__(self) -> str:
        """String representation."""
        return 'Token: %d %s' % (self.index, self.text)

    def get_text_at_stage(self, stage: str):
        """Get text from transformation history."""
        for transformation in self.transform_history:
            if transformation.stage == stage:
                return transformation.text

    def transform(self, stage: str, transform_func):
        """Transform token."""
        self.text = transform_func(self.text)
        self.transform_history.append(Transformation(self.text, stage))
        return self

    def mark_deleted(self, hidden=True):
        """Mark the token as hidden."""
        self.hidden = hidden


class Sentence:
    """This class represents a sentence."""

    def __init__(self, text: str):
        self.tokens: List[Token] = []
        if text is not None:
            for idx, word in enumerate(split_contractions(word_tokenizer(text))):
                self.add_token(Token(word, idx))

    def __getitem__(self, token_id: int) -> Token:
        return self.get_token(token_id)

    def __iter__(self):
        return iter(self.tokens)

    def get_token(self, token_id: int) -> Token:
        """Get the token."""
        for token in self.tokens:
            if token.index == token_id:
                return token

    def add_token(self, token: Token):
        """Add a token."""
        self.tokens.append(token)

        # set token imdex if not set
        token.sentence = self
        if token.index is None:
            token.index = len(self.tokens)

    def to_plain_string(self) -> str:
        """Plain string."""
        return ' '.join([t.text for t in self.tokens if not t.hidden])

    def __repr__(self):
        return 'Sentence: "' + ' '.join([t.text for t in self.tokens]) + '" - %d Tokens' % len(self)

    def __str__(self) -> str:
        return 'Sentence: "' + ' '.join([t.text for t in self.tokens]) + '" - %d Tokens' % len(self)

    def __len__(self) -> int:
        return len(self.tokens)

    def text_at_stage(self, stage: str, include_hidden=True) -> str:
        """Get sentence from a historical stage."""
        return ' '.join(
            [t.get_text_at_stage(stage) for t in self.tokens if include_hidden or not t.hidden])


class Entity(Sentence):
    """Collection of words to represent an entity."""

    def __init__(self, tokens: List[Token], entity_type: str):
        """Constructor."""
        self.tokens: List[Token] = tokens
        self.entity_type = entity_type
        self.tags: Dict[str, str] = {}

    def add_tag(self, tag_type: str, tag_value):
        """Adds a tag."""
        self.tags[tag_type] = tag_value

    def get_tag(self, tag_type: str) -> str:
        """Get a particular tag."""
        if tag_type in self.tags:
            return self.tags[tag_type]
        return None
