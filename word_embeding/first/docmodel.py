#!/usr/bin/env python
# coding=utf-8
from os import listdir
from os.path import isfile, join
import pdb
import gensim
# from sentmodel import SentModel


class DocModel:
    """document model"""

    def __init__(self):
        self.sentences = []
        self.title = ''
        self.wordcount = 0
        self.docID = ''
        self.sentcount = 0
        self.sentvec = []
        self.docvec = []
        self.distance = {}
        self.sortid = []
        self.summ = []


class SummModel:

    def __init__(self):
        self.summ = []
        self.docID = ''
        self.sortid = []


def getsentences(mypath):
    """read the document into model"""
    alldir = [d for d in listdir(mypath)]
    files = []
    docList = []
    doc = DocModel()
    for adir in alldir:
        afile = [f for f in listdir(join(mypath, adir))
                 if isfile(join(mypath, adir, f))]
        files += afile
    for afile in files:
        filepath = afile[0:8]
        fp = open(join(mypath, filepath, afile), 'r')
        lines = [line.strip() for line in fp.readlines()]
        # read the model
        for line in lines:
            if len(line) > 0:
                if 'id:' in line:
                    doc.docID = line.strip().split(':')[1]
                else:
                    doc.sentences.append(line.strip())
                    doc.sentcount += 1
            if len(line) == 0:
                docList.append(doc)
                doc = DocModel()
    return docList


def computeSentVec(docList, modelpath):
    """calculate the document and sentences vector quanity"""
    sumWordVec = [0] * 200
    model = gensim.models.Word2Vec.load(modelpath)
    sumDocVec = [0] * 200
    wordsent = []
    for doc in docList:
        for sent in doc.sentences:
            wordList = sent.split()
            for word in wordList:
                if word in model.vocab:
                    wordsent.append(word)
                    sumWordVec = map((lambda x, y: x + y),
                                     sumWordVec, model[word.lower()])
            doc.sentvec.append(map((lambda x: x/len(wordList)), sumWordVec))
        # get the document vectors
        for sentvec in doc.sentvec:
            # pdb.set_trace()
            sumDocVec = map((lambda x, y: x + y), sumDocVec, sentvec)
        # calculate the doc`s average vectors
        if (len(doc.sentences) != 0):
            doc.docvec = map((lambda x: x/len(doc.sentences)), sumDocVec)
    return docList


def mse(a, b):
    return reduce(lambda x, y: x+y, map(lambda x, y: (x-y)**2, a, b), 0)


def find_closest(docList):
    '''find the closest sentences to the document'''
    for doc in docList:
        locate = 0
        for sentvec in doc.sentvec:
            distance = mse(sentvec, doc.docvec)
            doc.distance[locate] = distance
            # pdb.set_trace()
            locate += 1

        # do sort work
        t = sorted(doc.distance.keys(), key=lambda k: doc.distance[k], reverse=True)
        doc.sortid += t

    return docList


if __name__ == '__main__':
    # read the doc model
    docList = getsentences('/home/jiankeguxin/桌面/mydoc/')
    # calculate the sentences` and document`s word2vec vector quanity
    docList = computeSentVec(docList, './text8.model')
    docListNew = getsentences('/home/jiankeguxin/桌面/mydocnew/')

    # get the summarization'''
    # pdb.set_trace()
    docList = find_closest(docList)
    docSumm = SummModel()
    for doc in docList:
        for i in range(3):
            for docnew in docListNew:
                if docnew.docID.lower() == 'ltw_eng_20050623.0165':
                    pdb.set_trace()
                if doc.docID.lower().strip() == docnew.docID.lower():
                    if doc.docID == 'ltw_eng_20050623.0165':
                        pdb.set_trace()
                    if len(doc.sentences) > 3:
                        doc.summ.append(docnew.sentences[doc.sortid[i]])
                    else:
                        continue
                # summ.append(doc.sentences[i])
                # docSumm.summ += summ
                # pdb.set_trace()
            # doc.summ.append('\n')
            # pdb.set_trace()

    for doc in docList:
        for sent in doc.summ:
            print sent.strip()
        print doc.docID.strip()
        print '\n'

