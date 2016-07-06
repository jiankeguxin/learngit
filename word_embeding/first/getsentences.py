#!/usr/bin/env python
# coding=utf-8
from os import listdir
from os.path import isfile, join
# import gensim
import shutil
import os

mypath = '/home/jiankeguxin/workspace/ldaSummarization/UpdateSumm08_test_docs_files'
alldir = [d for d in listdir(mypath)]
os.mkdir('mydoc')
os.chdir('mydoc')
for sdir in alldir:
    subdir = [d for d in listdir(join(mypath, sdir))]
    for fdir in subdir:
        filedir = join(mypath, sdir, fdir)

        files = [f for f in listdir(filedir) if isfile(join(filedir, f))]
        specificFiles = [f for f in files if f.endswith('_nostop.txt')]
        # collect sentences
        allSentences = []
        for fp in specificFiles:
            f = open(join(filedir, fp), 'r')
            lines = [line.strip() for line in f.readlines()]
            i = 0
            sentences = []
            while(i < len(lines)):
                if '<doc' in lines[i]:
                    docid1 = lines[i].split()[2]
                    docid = 'id:' + docid1
                    sentences.append(docid)
                if '<p>' in lines[i]:
                    i += 1
                    while('</p' not in lines[i]):
                        sentences.append(lines[i])
                        i += 1
                i += 1
            allSentences.append(sentences)

        fileName = filedir.split('/')[-1] + '_allsent.txt'
        dirName = filedir.split('/')[-1]
        os.mkdir(dirName)
        fnew = open(fileName, 'w')
        # write sentences to a new file
        for doc in allSentences:
            for sent in doc:
                sent += '\n'
                fnew.write(sent)
            fnew.write('\n')
        fnew.close()
        shutil.move(fileName, dirName)


