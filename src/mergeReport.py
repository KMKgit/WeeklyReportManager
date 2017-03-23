# -*- coding: utf-8 -*-
import os, sys, datetime
from pdfrw import PdfReader, PdfWriter

writer = PdfWriter()
now = datetime.datetime.now()
data_path = os.getcwd() + "/data/"
dir_path = data_path + str(now.year) + '_' + sys.argv[1] + "week"

if not os.path.exists(dir_path + "/result"):
    os.mkdir(dir_path + "/result")

files = [x for x in os.listdir(dir_path) if x.endswith('.pdf')]
for fname in sorted(files, key = lambda x: int(x.split(".")[0])):
    print ("[" + fname + "] Merged")
    writer.addpages(PdfReader(os.path.join(dir_path, fname)).pages)

writer.write(dir_path + "/result/"+ str(now.year) + "_" + sys.argv[1] + "_merge.pdf")
print("\nENDED MERGE REPORT!")