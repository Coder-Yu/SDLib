from baseclass.detector import Detector
from tool import config
from sklearn.metrics import classification_report
from sklearn import preprocessing
import numpy as np
from sklearn import metrics
import scipy
from scipy.sparse import csr_matrix


class PCASelectUsers(Detector):
    def __init__(self, conf, trainingSet=None, testSet=None, labels=None, fold='[1]', k=None, n=None ):
        super(PCASelectUsers, self).__init__(conf, trainingSet, testSet, labels, fold)


    def readConfiguration(self):
        super(PCASelectUsers, self).readConfiguration()
        # K = top-K vals of cov
        self.k = int(self.config['kVals'])
        self.userNum = len(self.data.trainingSet_u)
        self.itemNum = len(self.data.trainingSet_i)
        if self.k >= min(self.userNum, self.itemNum):
            self.k = 3
            print '*** k-vals is more than the number of user or item, so it is set to', self.k

        # n = attack size or the ratio of spammers to normal users
        self.n = float(self.config['attackSize'])


    def buildModel(self):
        #array initialization
        dataArray = np.zeros([self.userNum, self.itemNum], dtype=float)
        self.testLabels = np.zeros(self.userNum)
        self.predLabels = np.zeros(self.userNum)

        #add data
        print 'construct matrix'
        for user in self.data.trainingSet_u:
            for item in self.data.trainingSet_u[user].keys():
                value = self.data.trainingSet_u[user][item]
                a = self.data.user[user]
                b = self.data.item[item]
                dataArray[a][b] = value

        sMatrix = csr_matrix(dataArray)
        # z-scores
        sMatrix = preprocessing.scale(sMatrix, axis=0, with_mean=False)
        sMT = np.transpose(sMatrix)
        # cov
        covSM = np.dot(sMT, sMatrix)
        # eigen-value-decomposition
        vals, vecs = scipy.sparse.linalg.eigs(covSM, k=self.k, which='LM')

        newArray = np.dot(dataArray**2, np.real(vecs))

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


    def predict(self):
        print 'predict spammer'
        spamList = []
        i = 0
        while i < self.n * len(self.disSort):
            spam = self.disSort[i][0]
            spamList.append(spam)
            self.predLabels[spam] = 1
            i += 1

        # trueLabels
        for user in self.data.trainingSet_u:
            userInd = self.data.user[user]
            self.testLabels[userInd] = int(self.labels[user])

        return self.predLabels











