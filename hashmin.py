import os
import re
import random
import time
import binascii
from bisect import bisect_right
from heapq import heappop, heappush

numDocs=100
dataFile = "./data/articles_" + str(numDocs) + ".train"
truthFile = "./data/articles_" + str(numDocs) + ".truth"

class MinHash(object):
    def __init__(self,documents,numhashs,numdocs):
        self.documents=documents
        self.numhashs = numhashs
        self.numdocs = numdocs

    # =============================================================================
    #               Convert Documents To Sets of Shingles
    # =============================================================================

    def convert_document_to_shingles(self):
        print("Shingling articles...")

        # The current shingle ID value to assign to the next new shingle we
        # encounter. When a shingle gets added to the dictionary, we'll increment this
        # value.
        curShingleID = 0

        # Create a dictionary of the articles, mapping the article identifier (e.g.,
        # "t8470") to the list of shingle IDs that appear in the document.
        docsAsShingleSets = {};

        # Open the data file.
        f = open(dataFile, "r")

        docNames = []

        t0 = time.time()

        totalShingles = 0

        for i in range(0, numDocs):

            # Read all of the words (they are all on one line) and split them by white
            # space.
            words = f.readline().split(" ")

            # Retrieve the article ID, which is the first word on the line.
            docID = words[0]

            # Maintain a list of all document IDs.
            docNames.append(docID)

            del words[0]

            # 'shinglesInDoc' will hold all of the unique shingle IDs present in the
            # current document. If a shingle ID occurs multiple times in the document,
            # it will only appear once in the set (this is a property of Python sets).
            shinglesInDoc = set()

            # For each word in the document...
            for index in range(0, len(words) - 2):
                # Construct the shingle text by combining three words together.
                shingle = words[index] + " " + words[index + 1] + " " + words[index + 2]

                # Hash the shingle to a 32-bit integer.
                crc = binascii.crc32(str.encode(shingle)) & 0xffffffff

                # Add the hash value to the list of shingles for the current document.
                # Note that set objects will only add the value to the set if the set
                # doesn't already contain it.
                shinglesInDoc.add(crc)

            # Store the completed list of shingles for this document in the dictionary.
            docsAsShingleSets[docID] = shinglesInDoc
            print(docsAsShingleSets[docID])
            print(len(docsAsShingleSets[docID]))
            print(len(docsAsShingleSets))

            # Count the number of shingles across all documents.
            totalShingles = totalShingles + (len(words) - 2)

        # Close the data file.
        f.close()

        # Report how long shingling took.
        print('\nShingling ' + str(numDocs) + ' docs took %.2f sec.' % (time.time() - t0))


        print('\nAverage shingles per doc: %.2f' % (totalShingles / numDocs))

# =============================================================================
#                 Generate MinHash Signatures
# =============================================================================

    def Generate_MinHash_Signatures(self):
        print("Generating random hash functions...")

        maxSingle_ID=

        #哈希函数f(x)=(a*x+b)%c
        def generate_hash_fun():







mh = MinHash(0,10,100)
mh.convert_document_to_shingles()

