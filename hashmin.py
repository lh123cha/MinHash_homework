import os
import re
import random
import time
import binascii
from bisect import bisect_right
from heapq import heappop, heappush
import sys

numDocs=20
# dataFile = "./data/articles_" + str(numDocs) + ".train"
truthFile = "./data/articles_" + str(numDocs) + ".truth"
dataFile = "./data/en_articles.train"


class MinHash(object):
    def __init__(self,documents,numhashes,numdocs):
        self.documents=documents
        self.numhashes = numhashes
        self.numdocs = numdocs
        self.docNames =[]
        # Create a dictionary of the articles, mapping the article identifier (e.g.,
        # "t8470") to the list of shingle IDs that appear in the document.
        self.docsAsShingleSets={}
        self.signatures=[]
        self.JSim=[]
        self.estJSim=[]


    # =============================================================================
    #               Convert Documents To Sets of Shingles
    # =============================================================================

    def convert_document_to_shingles(self):
        print("Shingling articles...")

        # The current shingle ID value to assign to the next new shingle we
        # encounter. When a shingle gets added to the dictionary, we'll increment this
        # value.
        curShingleID = 0



        # Open the data file.
        f = open(dataFile, "r",encoding="utf-8")

        t0 = time.time()

        totalShingles = 0

        for i in range(0, numDocs):

            # Read all of the words (they are all on one line) and split them by white
            # space.
            words = f.readline().split(" ")

            # Retrieve the article ID, which is the first word on the line.
            docID = words[0]

            # Maintain a list of all document IDs.
            self.docNames.append(docID)

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
            self.docsAsShingleSets[docID] = shinglesInDoc

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

        maxSingle_ID=2**32-1;
        nextPrime = 4294967311

        #哈希函数f(x)=(a*x+b)%c
        #生成哈希函数所需的素数系数,生成k个随机系数
        def pickRandomCoeffs(k):
            #生成k个随机系数，randList
            randList=[]
            while k>0:
                randIndex = random.randint(0,maxSingle_ID)

                while randIndex in randList:
                    randIndex = random.randint(0,maxSingle_ID)
                randList.append(randIndex)

                k=k-1
            return randList
        coffA = pickRandomCoeffs(self.numhashes)
        coffB = pickRandomCoeffs(self.numhashes)

        print("Generating MinHash signutures for all documents\n")

        for docId in self.docNames:
            shingleIdSet = self.docsAsShingleSets[docId]

            signature = []

            for i in range(self.numhashes):
                minHashCode = nextPrime+1;

                for shingleId in shingleIdSet:
                    hashcode = (coffA[i]*shingleId+coffB[i])%nextPrime

                    if hashcode<minHashCode:
                        minHashCode=hashcode
                signature.append(minHashCode)

            self.signatures.append(signature)
        print(self.signatures[0])
        print("Generating MinHash signutures finished\n")
    #生成上三角矩阵索引
    def getTriangleIndex(self,i,j):
        # If i == j that's an error.
        if i == j:
            sys.stderr.write("Can't access triangle matrix with i == j")
            sys.exit(1)
        # If j < i just swap the values.
        if j < i:
            temp = i
            i = j
            j = temp
        k = int(i * (numDocs - (i + 1) / 2.0) + j - i) - 1

        return k

    def Triangle_Mactrices(self):
        numElems = int(self.numdocs*(self.numdocs-1)/2)

        self.JSim=[0 for x in range(numElems)]
        self.estJSim = [0 for x in range(numElems)]

    def Compare_All_Signatures(self):
        self.Triangle_Mactrices()
        print("Comparing add signatures\n")

        for i in range(self.numdocs):
            signature1 = self.signatures[i]
            for j in range(i+1,self.numdocs):
                signature2=self.signatures[j]

                count=0

                for k in range(0,self.numhashes):
                    count = count+(signature1[k]==signature2[k])
                self.estJSim[self.getTriangleIndex(i,j)]=(count/self.numhashes)
                print(self.estJSim[self.getTriangleIndex(i,j)])
        print("Compare signatures finished!\n")
    def display(self):
        # =============================================================================
        #                   Display Similar Document Pairs
        # =============================================================================

        # Count the true positives and false positives.
        tp = 0
        fp = 0

        top_five_file = {}

        threshold = 0.05
        print("\nList of Document Pairs with J(d1,d2) more than", threshold)
        print("Values shown are the estimated Jaccard similarity and the actual")
        print("Jaccard similarity.\n")
        print("                   Est. J   Act. J")

        # For each of the document pairs...
        for i in range(0, numDocs):
            for j in range(i + 1, numDocs):
                # Retrieve the estimated similarity value for this pair.
                estJ = self.estJSim[self.getTriangleIndex(i, j)]

                # If the similarity is above the threshold...
                if estJ > threshold:

                    # Calculate the actual Jaccard similarity for validation.
                    s1 = self.docsAsShingleSets[self.docNames[i]]
                    s2 = self.docsAsShingleSets[self.docNames[j]]
                    J = (len(s1.intersection(s2)) / len(s1.union(s2)))

                    # Print out the match and similarity values with pretty spacing.
                    print("  %5s --> %5s   %.2f     %.2f" % (self.docNames[i], self.docNames[j], estJ, J))

                    # Check whether this is a true positive or false positive.
                    # We don't need to worry about counting the same true positive twice
                    # because we implemented the for-loops to only compare each pair once.
                    # if plagiaries[docNames[i]] == docNames[j]:
                    #     tp = tp + 1
                    # else:
                    #     fp = fp + 1

        # Display true positive and false positive counts.



mh = MinHash(0,100,20)
mh.convert_document_to_shingles()
mh.Generate_MinHash_Signatures()
mh.Compare_All_Signatures()
mh.display()

