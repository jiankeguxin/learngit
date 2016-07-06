#!/usr/bin/env python
# coding=utf-8
'''this is the sentences model ,it is used for putting the sentences into the
model which simplifies the vector counting way'''
import docmodel


class SentModel:
    def __init__(self):
        # sentences length
        self.length = 0
        # sentences contant
        self.contant = []
        # words in sentences
        self.sentwords = []
        # vector of the sentences
        self.vector = []
        # distance between sentences and documents
        self.distantTodoc = []
        # the ID of sentence in document
        self.sentId = 0
        # which document does the sentence belong to
        self.docId = ''
