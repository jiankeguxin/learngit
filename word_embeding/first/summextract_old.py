#!/usr/bin/env python
# coding=utf-8
import gensim
# import os
from os import listdir
from os.path import join, isfile
import math
import os
import shutil
import pdb

# getsentences() used for put every sentence into the dictionary
# calculate the sentence vector
# output a list of (word2vec_dict, text)
# compute the doc vector
# compute the distance between sentences and document

# it is used to mark the punctuation
non_char = '~!@#$%^&*()_+{}|:"<>?`1234567890-=[]\\;\',./\n'


class DocModel():
    """document model"""

    def __init__(self):
        self.sentences = []                     # sentence set
        self.originalsent = []                  # original sentences
        self.title = ''                         # doc title
        self.docID = ''                         # doc id
        self.wordcount = 0                      # word number of sentence
        self.sentcount = 0                      # sent number in a doc
        self.sentvec = []                       # sent vector
        self.docvec = []                        # doc vector
        self.distance = {}                      # distance between doc and sent
        self.sortid = []                        # the sort sentence id
        self.catalog = ''                       # which catalog is in


class DocsetModel():
    """doc set model"""

    def __init__(self):
        self.docList = []                       # doc list
        self.docsetTopicID                      # doc set topic id


class SummModel():
    """the summarization model"""

    def __init__(self):
        self.summ = []                          # summarization
        self.docID = ''                         # doc id
        self.sortid = []                        # the sort sentence id
        self.catalog = ''                       # where is in


def getsentences(mypath):
    """read the docs into DocModel and get rid of the punctuation mark
    and remove the stop word"""

    alldir = [d for d in listdir(mypath)]
    files = []
    docList = []
    for adir in alldir:
        subdir = [d for d in listdir(join(mypath, adir))]
        for fdir in subdir:
            filedir = join(mypath, adir, fdir)
            files = [f for f in listdir(filedir) if isfile(join(filedir, f))]
            specificFiles = [f for f in files if f.endswith('_stem.txt')]
            # pdb.set_trace()
            # collect sentences
            for fp in specificFiles:
                doc = DocModel()
                f = open(join(filedir, fp), 'r')
                lines = [line.strip() for line in f.readlines()]
                f.close()
                i = 0
                # mark the catalogue which the summarization is in
                doc.catalog += filedir.split('/')[-1]
                while(i < len(lines)):
                    if '<DOC' in lines[i]:
                        docid = 'id:' + lines[i].split('\"')[1].strip()
                        doc.docID += docid

                    if '<HEADLINE>' in lines[i]:
                        doc.title += lines[i+1]

                    if '<TEXT>' in lines[i]:
                        i += 1
                        while('</TEXT>' not in lines[i]):
                            if '<P>' in lines[i] or '</P>' in lines[i]:
                                i += 1
                                continue
                            # process punctuation and
                            # remove the stoped word here
                            sent = lines[i]
                            sent = preprocess(sent)
                            doc.sentences.append(sent)

                            # get the original sentences
                            doc.originalsent.append(lines[i])
                            # pdb.set_trace()
                            i += 1
                    i += 1
                docList.append(doc)
    return docList


def preprocess(sent):
    """get rid of the punctuation mark and remove the stoped word"""

    wordlist = sent.split()
    sentnew = ''
    f = open('./stop-word-list.txt', 'r')
    stop_word_list = [w.strip() for w in f.readlines()]
    f.close()
    # process the punctuation
    for word in wordlist:
        if any([(x in non_char) for x in word]):
            continue
        elif(word.lower() not in stop_word_list):
            sentnew += word.lower()
            sentnew += ' '
    return sentnew


def computeSentVec(docList, modelpath):
    """This method is used to compute the average vector of a sentence """

    sumWordVec = [0]*50
    sumDocVec = [0]*50
    model = gensim.models.Word2Vec.load(modelpath)
    # it is used to count the number of words which is not in the vocab
    n = 0
    global countin, countout
    countin = 0
    countout = 0
    for doc in docList:
        for sent in doc.sentences:
            wordList = sent.strip().split()
            for word in wordList:
                if word in model.vocab:
                    if n == 0:
                        sumWordVec = model[word]
                    else:
                        sumWordVec = map((lambda x, y: x+y), sumWordVec, model[word])
                    n += 1
            if n > 1:
                doc.sentvec.append(map(lambda x: x/n, sumWordVec))
        # get the document vector
        for sentvec in doc.sentvec:
            sumDocVec = map((lambda x, y: x+y), sumDocVec, sentvec)
        # calculate the doc`s average vector
        if (len(doc.sentences) != 0):
            doc.docvec = map((lambda x: x/len(doc.sentences)), sumDocVec)
    return docList


def mse(a, b):
    """compute euclidean distance"""
    return reduce(lambda x, y: x+y, map(lambda x, y: (x-y)**2, a, b), 0)


def find_closest(docList):
    """find the closest sentence to the document"""

    for doc in docList:
        locate = 0
        for sentvec in doc.sentvec:
            distance = math.sqrt(mse(sentvec, doc.docvec))
            doc.distance[locate] = distance
            locate += 1

        # do sort work; reverse=False is from small to big
        t = sorted(doc.distance.keys(),
                   key=lambda k: doc.distance[k], reverse=False)
        doc.sortid += t
    return docList


def outputSumm(docList):
    """This is used to output the summarization into different catalogue"""

    summList = []
    for doc in docList:
        docSumm = SummModel()
        if len(doc.sentences) >= 3:
            # get the summarization
            docSumm.summ += [doc.originalsent[doc.sortid[i]] for i in range(3)]
            # get the doc id
            docSumm.docID = doc.docID
            # catalogue
            docSumm.catalog += doc.catalog
            # put the summ into list
            summList.append(docSumm)
        elif len(doc.sentences) == 2 or len(doc.sentences) == 1:
            docSumm.summ += [doc.originalsent[doc.sortid[i]]
                             for i in range(len(doc.sentences))]
            docSumm.docID = doc.docID
            docSumm.catalog = doc.catalog
            summList.append(docSumm)

    # for doc in summList:
    #    if len(doc.summ) == 0:
    #        pdb.set_trace()
    #        for sent in doc.summ:
    #            print sent
    #        print doc.docID
    #        print '\n'
    os.mkdir('./summarization')
    os.chdir('./summarization')
    for docSumm in summList:
        suffix = '.txt'
        filename = docSumm.catalog + '-' + docSumm.docID.split(':')[1] + suffix
        fp = open(filename, 'w')
        for i in range(len(docSumm.summ)):
            fp.write(docSumm.summ[i].strip())
            fp.write('\n')
            i += 1


def main(filepath):
    # read the doc model
    docList = getsentences(filepath)
    # calculate the sentences` and documents` word2vec quantity
    docList = computeSentVec(docList, './text8-2.model')
    # print countin, countout
    docList = find_closest(docList)
    pdb.set_trace()
    # print out the summarization
    outputSumm(docList)


if __name__ == '__main__':
    filepath = './workspace/ldaSummarization/UpdateSumm08_test_docs_files'
    # docList = getsentences(filepath)
    main(filepath)
    # pdb.set_trace()
