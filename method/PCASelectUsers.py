from baseclass.SDetection import SDetection
from tool import config
from sklearn.metrics import classification_report
from sklearn import preprocessing
import numpy as np
from sklearn import metrics
import scipy
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds


class PCASelectUsers(SDetection):
    def __init__(self, conf, trainingSet=None, testSet=None, labels=None, fold='[1]', k=None, n=None ):
        super(PCASelectUsers, self).__init__(conf, trainingSet, testSet, labels, fold)

    def readConfiguration(self):
        super(PCASelectUsers, self).readConfiguration()
        # k = top-K vals of cov
        self.k = int(self.config['kVals'])
        # n = attack size or 0.1
        self.n = float(self.config['attackSize'])

    def buildModel(self):
        #array initialization
        userNum = len(self.dao.trainingSet_u)
        itemNum = len(self.dao.trainingSet_i)
        dataArray = np.zeros([userNum, itemNum], dtype=float)
        self.trueLabels = np.zeros(userNum)
        self.predLabels = np.zeros(userNum)

        #add data
        print 'construct matrix'
        for user in self.dao.trainingSet_u:
            for item in self.dao.trainingSet_u[user].keys():
                value = self.dao.trainingSet_u[user][item]
                a = self.dao.user[user]
                b = self.dao.item[item]
                dataArray[a][b] = value

        #test the value
        # j = 0
        # for i in dataArray:
        #     for m in i:
        #         if m != 0:
        #             print m
        #             j +=1
        # print j

        # #shift to sparse matrix
        # sMatrix = csr_matrix(np.transpose(dataArray))
        # sMatrix = preprocessing.scale(sMatrix, axis=0, with_mean=False)
        # print sMatrix
        # print sMatrix.shape
        #
        # u,s,v = scipy.sparse.linalg.svds(sMatrix, k=3, which ='LM') #k=min(userNum-1, itemNum-1)
        # print u.shape,u
        # print s.shape,s
        # print v.shape,v
        # #newArray = u[:,-self.k:]
        # #u = u[:, :self.k]
        # print u
        # newArray = np.dot(dataArray, u)
        # # print newArray
        # print newArray.shape
        # # #
        # #

        #print dataArray
        print 'z-scores'
        dataArray = preprocessing.scale(dataArray, axis=0)
        print 'tanspose'
        dataArrayT = np.transpose(dataArray)
        #cov
        print 'cov'
        covArray = np.dot(dataArrayT, dataArray)
        #eigen-value-decomposition
        print 'vals and vecs'
        vals, vecs  = np.linalg.eig(covArray)
        #top-K vals of cov
        print 'sort vals'
        valsInd = np.argsort(vals)
        valsInd = valsInd[-1:-(self.k + 1):-1]  #descend
        #valsInd = valsInd[0:self.k:1]          #ascend
        #use np.real() to get real parts
        vecsInd = np.real(vecs[:, valsInd])
        # print vecsInd.shape
        print 'new matrix'
        newArray = np.dot(dataArray**2, np.real(vecsInd))
        print newArray.shape
        #print newArray

        # print 'construct distanceDict of users'
        distanceDict = {}
        userId = 0
        for user in newArray:
            distance = 0
            for tmp in user:
                distance += tmp
            distanceDict[userId] = float(distance)
            userId += 1

        print 'sort distance '
        self.disSort = sorted(distanceDict.iteritems(), key=lambda d: d[1], reverse=False)

        print self.disSort

    #
    def predict(self):
        # predict spammer
        print 'predict spammer'
        spamList = []
        i = 0
        while i < self.n * len(self.disSort):
            spam = self.disSort[i][0]
            spamList.append(spam)
            self.predLabels[spam] = 1
            i += 1
        # for i in self.predLabels:
        #     print i
        # print '------------------------'

        # trueLabels
        print 'trueLabels'
        for user in self.dao.trainingSet_u:
            userInd = self.dao.user[user]
            self.trueLabels[userInd] = int(self.labels[user])
        # for j in self.trueLabels:
        #     print j

        print classification_report(self.trueLabels, self.predLabels, digits=4)
        print metrics.confusion_matrix(self.trueLabels, self.predLabels)
        return classification_report(self.trueLabels, self.predLabels, digits=4)

    #









