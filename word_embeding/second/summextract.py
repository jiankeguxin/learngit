#!/usr/bin/env python
# coding=utf-8
import gensim
# import os
from os import listdir
from os.path import join, isfile, isdir
import os
import pdb

# getsentences() used for put every sentence into the dictionary
# calculate the sentence vector
# output a list of (word2vec_dict, text)
# compute the doc vector
# compute the distance between sentences and document

# it is used to mark the punctuation
non_char = '~!@#$%^&*()_+{}|:"<>?`1234567890-=[]\\;\',./\n'


class DocsetModel():
    """doc set model"""

    def __init__(self):
        self.docsetTopicID = 0               # docset topic id
        self.docList = []                    # docs in docset
        self.catalog = ''                    # docset catalogue
        self.docsetvec = []                  # docset vector
        self.sortid = []                     # sent sorted


class DocModel():
    """document model"""

    def __init__(self):
        self.sentsModel = []                # sentence model
        self.title = ''                     # doc title
        self.docID = ''                     # doc id
        self.wordcount = 0                  # word number of sentence
        self.sentcount = 0                  # sent number in a doc
        self.docvec = []                    # doc vector
        self.distance = {}                  # distance between doc and sent
        self.sortid = []                    # the sort sentence id
        self.catalog = ''


class SentModel():
    """sentences in docs"""

    def __init__(self):
        self.sentId = ''                    # sentence number in doc
        self.sentNum = ''                   # sentence number in docset
        self.paraId = 0                     # para number in doc
        self.paraSentId = 0                 # sentence number in para
        self.wordsNum = 0                   # words in sentence
        self.original = []                  # original sent
        self.sentProcessed = []             # sentence which has been processed
        self.sentvec = []                   # sent vector
        self.sentlen = 0                    # sent length
        self.distance = {}                  # distance between sent and docset


class SummModel():
    """the summarization model"""

    def __init__(self):
        self.summ = []                          # summarization
        self.docID = ''                         # doc id
        self.sortid = []                        # the sort sentence id
        self.catalog = ''                       # docset id


def getsentences(mypath):
    """read the docs into DocModel and get rid of the punctuation mark
    and remove the stop word"""

    alldir = [d for d in listdir(mypath)]
    files = []
    docsetList = []
    for adir in alldir:
        subdir = [d for d in listdir(join(mypath, adir))]
        for fdir in subdir:
            # add docset here
            docset = DocsetModel()
            docset.catalog += fdir
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
                    j = 0
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
                            sent = SentModel()
                            # get the original sentences
                            sent.original.append(lines[i])
                            sent.sentProcessed.append(preprocess(lines[i]))
                            # set the sent number in docs and docsets
                            sent.sentId = doc.docID.split(':')[1] + '-' + str(j)
                            j += 1
                            sent.sentNum = docset.catalog
                            doc.sentsModel.append(sent)

                            # pdb.set_trace()
                            i += 1
                    # can't move
                    i += 1
                docset.docList.append(doc)
            docsetList.append(docset)
    return docsetList


def preprocess(sent):
    """get rid of the punctuation mark and remove the stoped word"""

    wordlist = sent.split()
    sentnew = ''
    f = open('/home/jiankeguxin/word_embeding/stop-word-list.txt', 'r')
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


def computeSentVec(docList, model):
    """This method is used to compute the average vector of a sentence """

    sumWordVec = [0]*50
    sumDocVec = [0]*50
    n = 0
    # it is used to count the number of words which is not in the vocab
    global countin, countout
    countin = 0
    countout = 0
    for doc in docList:
        for sent in doc.sentsModel:
            wordList = sent.sentProcessed[0].split()
            for word in wordList:
                if word in model.vocab:
                    if n == 0:
                        sumWordVec = model[word]
                    else:
                        sumWordVec = map((lambda x, y: x+y), sumWordVec, model[word])
                    n += 1
            if n > 1:
                sent.sentvec = map((lambda x: x/n), sumWordVec)
            else:
                print 'False'
        # get the document vector
        for sent in doc.sentsModel:
            sumDocVec = map((lambda x, y: x+y), sumDocVec, sent.sentvec)
        # calculate the doc's average vector
        if (len(doc.sentsModel) != 0):
            doc.docvec = map((lambda x: x/len(doc.sentsModel)), sumDocVec)


def mse(a, b):
    """compute euclidean distance"""
    return reduce(lambda x, y: x+y, map(lambda x, y: (x-y)**2, a, b), 0)


def find_closest(docset):
    """find the closest sentence to the document"""

    for doc in docset.docList:
        for sent in doc.sentsModel:
            distance = 0
            sentNum = ''
            distance = mse(sent.sentvec, docset.docsetvec)
            sentNum = sent.sentNum + '-' + sent.sentId
            sent.distance[sentNum] = distance

    # sort the sent.distance '''
    allSentences = []
    for doc in docset.docList:
        for sent in doc.sentsModel:
            allSentences.append(sent)
        # sorted(sent, key=lambda , reverse=False)
    t = sorted(allSentences,
               key=lambda sent: sent.distance.values(),
               reverse=False)
    return t


def outputSumm(t):
    """This is used to output the summarization into different catalogue"""

    docsetSumm = SummModel()
    for i in range(3):
        # get the summarization
        docsetSumm.summ += t[i].original
        # get the doc id
        docsetSumm.docID = t[i].sentId.split('-')[-2]
        # catalogue
        docsetSumm.catalog = t[i].sentNum
        # put the summ into list
    filename = docsetSumm.catalog[0:5] + docsetSumm.catalog[6:] + '.' + 'M.100.' + docsetSumm.catalog[5] + '.TAC2008'
    fp = open(filename, 'w')
    for summ in docsetSumm.summ:
        fp.write(summ)
        fp.write('\n')
    fp.close()


def outputSumm2(t):
    '''output 100 words summarization'''

    docsetSumm = SummModel()
    number = 100
    wordcount = 0
    for i in range(len(t)):
        if wordcount < number:
            # get the summarization
            docsetSumm.summ += t[i].original
            # get the doc id`
            docsetSumm.docID = t[i].sentId.split('-')[-2]
            # catalogue
            docsetSumm.catalog = t[i].sentNum
            wordcount += len(t[i].original[0].split())
        elif wordcount == number:
            break
        else:
            org_len = wordcount - len(t[i-1].original[0].split())
            more = number - org_len
            docsetSumm.summ.pop(-1)
            words_more = ''
            for j in range(more):
                words_more += t[i-1].original[0].split()[j]
                words_more += ' '
            docsetSumm.summ.append(words_more)
            break
    filename = docsetSumm.catalog[0:5] + docsetSumm.catalog[6:] + '.' + 'M.100.' + docsetSumm.catalog[5] + '.TAC2008'
    fp = open(filename, 'w')
    for summ in docsetSumm.summ:
        fp.write(summ)
        fp.write('\n')
    fp.close()


def main(filepath):

    # see whether the present catalog is ./summarization or not
    if os.popen('pwd').readline().strip().split('/')[-1].__eq__('summarization'):
        print 'in'
    elif isdir('./summarization'):
        os.chdir('./summarization')
    else:
        os.mkdir('./summarization')
        os.chdir('./summarization')

    # read the doc model
    docsetList = getsentences(filepath)
    model = gensim.models.Word2Vec.load('/home/jiankeguxin/word_embeding/models/text8-50.model')
    for docset in docsetList:
        sumDocsetVec = [0]*50
        # calculate the sentences` and documents` word2vec quantity
        computeSentVec(docset.docList, model)
        for doc in docset.docList:
            sumDocsetVec = map((lambda x, y: x+y), doc.docvec, sumDocsetVec)
        docset.docsetvec = map((lambda x: x/len(docset.docList)), sumDocsetVec)
        t = find_closest(docset)
        # print out the summarization
        outputSumm2(t)
        # pdb.set_trace()
    # print countin, countout


if __name__ == '__main__':
    filepath = '/home/jiankeguxin/workspace/ldaSummarization/UpdateSumm08_test_docs_files'
    # docList = getsentences(filepath)
    main(filepath)
    # pdb.set_trace()
