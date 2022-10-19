import random
import binascii
import sys

numDocs=20
numhashes=20
dataFile = "./data/en_articles.train"


class MinHash(object):
    def __init__(self,numhashes,numdocs):
        self.numhashes = numhashes
        self.numdocs = numdocs
        self.docNames =[]
        self.docsAsShingleSets={}
        self.signatures=[]
        self.JSim=[]
        self.estJSim=[]


    # =============================================================================
    #               Convert Documents To Sets of Shingles
    # =============================================================================
    #使用trigram mode，三个单词进行拼接作为一个shingle
    def convert_document_to_shingles(self):
        print("Shingling articles...")


        f = open(dataFile, "r",encoding="utf-8")

        totalShingles = 0

        for i in range(0, numDocs):
            words = f.readline().split(" ")
            docID = words[0]

            self.docNames.append(docID)

            del words[0]
            shinglesInDoc = set()

            for index in range(0, len(words) - 2):
                shingle = words[index] + " " + words[index + 1] + " " + words[index + 2]

                # Hash the shingle to a 32-bit integer.
                crc = binascii.crc32(str.encode(shingle)) & 0xffffffff

                shinglesInDoc.add(crc)
            self.docsAsShingleSets[docID] = shinglesInDoc
            totalShingles = totalShingles + (len(words) - 2)
        f.close()

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
        print("Generating MinHash signutures finished\n")
    #生成上三角矩阵索引
    def getTriangleIndex(self,i,j):
        if i == j:
            sys.stderr.write("Can't access triangle matrix with i == j")
            sys.exit(1)
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

    # =============================================================================
    #                 Calculate Jaccard Similarities
    # =============================================================================
    #计算真实的jaccard相似度
    def Calculate_Jaccard_Similarities(self):
        # if True:
        print("\nCalculating Jaccard Similarities...")

        # For every document pair...
        for i in range(0, self.numdocs):
            s1 = self.docsAsShingleSets[self.docNames[i]]

            for j in range(i + 1, self.numdocs):
                # Retrieve the set of shingles for document j.
                s2 = self.docsAsShingleSets[self.docNames[j]]

                # Calculate and store the actual Jaccard similarity.
                self.JSim[self.getTriangleIndex(i, j)] = (len(s1.intersection(s2)) / len(s1.union(s2)))

    # =============================================================================
    #                 Compare All Signatures
    # =============================================================================
    #使用签名估计相似度
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
        print("Compare signatures finished!\n")

    def Get_Top_five_files(self):
        estJim_dict={}
        Jim_dict={}
        for i in range(self.numdocs):
            for j in range(i+1,self.numdocs):
                estJim_key = self.docNames[i] +" "+self.docNames[j]
                estJim_dict[estJim_key]=self.estJSim[self.getTriangleIndex(i,j)]

        top5_estJim_files = sorted(estJim_dict.items(), key=lambda x: x[1],reverse=True)
        print(top5_estJim_files[0:5])

        for i in range(self.numdocs):
            for j in range(i+1,self.numdocs):
                Jim_key = self.docNames[i] +" "+self.docNames[j]
                Jim_dict[Jim_key]=self.JSim[self.getTriangleIndex(i,j)]
        top5_true_Jim_files = sorted(Jim_dict.items(),key=lambda x:x[1],reverse=True)
        print(top5_true_Jim_files[0:5])
        print("使用minhash估计得到的最相似的五对文章是：\n")
        for i in range(5):
            print(top5_estJim_files[i][0])
        print("使用真实jaccard得到的最相似的5对文章是：\n")
        for i in range(5):
            print(top5_true_Jim_files[i][0])


    def run(self):
        self.convert_document_to_shingles()
        self.Generate_MinHash_Signatures()
        self.Compare_All_Signatures()
        self.Calculate_Jaccard_Similarities()
        self.Get_Top_five_files()
mh = MinHash(numhashes,numDocs)
mh.run()
