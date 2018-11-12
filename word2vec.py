#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 10 14:55:12 2018.

@author: euler
"""
import logging
import os
from multiprocessing import cpu_count

import gensim
import numpy as np
from gensim.models import word2vec
from gensim.models.keyedvectors import KeyedVectors

vector_dim = 150
root_path = os.path.join(os.path.dirname(__file__), 'data/')


class MySentences(object):
    """Sentence class."""

    def __init__(self, filename):
        self.filename = filename

    def __iter__(self):
        for line in open(self.filename):
            yield line.split()


class WordEmbeddingModel():
    """Word embedding model."""

    def __init__(self, model):
        self.model = model
        self.embedding_matrix = None
        self.create_embedding_matrix()

    def create_embedding_matrix(self):
        """Convert the wv word vectors into a numpy matrix that is suitable for insertion into our TensorFlow and Keras models."""
        embedding_matrix = np.zeros((len(self.model.wv.vocab), vector_dim))
        for i in range(len(self.model.wv.vocab)):
            embedding_vector = self.model.wv[self.model.wv.index2word[i]]
            if embedding_vector is not None:
                embedding_matrix[i] = embedding_vector[:vector_dim]
        self.embedding_matrix = embedding_matrix


def create_embedding_matrix(model):
    """
    Convert the wv word vectors into a numpy matrix.

    That is suitable for insertion into our TensorFlow and Keras models.
    """
    embedding_matrix = np.zeros((len(model.wv.vocab), vector_dim))
    for i in range(len(model.wv.vocab)):
        embedding_vector = model.wv[model.wv.index2word[i]]
        if embedding_vector is not None:
            embedding_matrix[i] = embedding_vector
    return embedding_matrix


def load_gensim_embedding(model_name):
    """Load the embedding model."""
    try:
        model = gensim.models.Word2Vec.load(root_path + model_name)
    except FileNotFoundError:
        model = build_embedding(model_name)

    embedding_matrix = create_embedding_matrix(model)
    return model, embedding_matrix


def load_embedding(model_name, is_binary=True):
    """Load the embedding model."""
    try:
        model = KeyedVectors.load_word2vec_format(
            root_path + model_name + '.bin', binary=is_binary)
    except FileNotFoundError:
        model = build_embedding(model_name)

    # embedding_matrix = create_embedding_matrix(model)
    return WordEmbeddingModel(model)


def build_embedding(model_name: str, is_binary=True):
    """Build the word embedding."""
    sentences = MySentences(root_path + model_name + '.txt')
    logging.basicConfig(
        format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    model = word2vec.Word2Vec(
        sentences, iter=100, min_count=1, size=vector_dim, workers=2 * cpu_count())
    model.save(root_path + model_name, binary=is_binary)
    return model
