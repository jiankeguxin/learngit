#!/usr/bin/env python
# coding=utf-8
from os import listdir
from os.path import isfile, join
import os
import pdb

mypath = '/home/jiankeguxin/桌面/mydocnew'
alldir = [d for d in listdir(mypath)]
for adir in alldir:
    filedir = join(mypath, adir)
    files = [f for f in listdir(filedir) if isfile(join(filedir, f))]
    fopen = open(join(filedir, files[0]))
    lines = [line.strip() for line in fopen.readlines()]
    for line in lines:
        if line == 'The number of corporate employers offering retiree health benefits has declined steadily for 15 years.':
            print filedir
