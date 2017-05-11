from baseclass.SDetection import SDetection
from sklearn.metrics import classification_report
import numpy as np
#from sklearn import preprocessing
import math


class PCASelectUsers(SDetection):
    def __init__(self, conf, trainingSet=None, testSet=None, labels=None, fold='[1]'):
        super(PCASelectUsers, self).__init__(conf, trainingSet, testSet, labels, fold)

    def buildModel(self):
        #array initialization
        userNum = len(self.dao.trainingSet_u)
        itemNum = len(self.dao.trainingSet_i)
        dataArray = np.zeros([userNum, itemNum], dtype=float)
        self.trueLabels = np.zeros(userNum)
        self.predLabels = np.zeros(userNum)

        #add data
        for user in self.dao.trainingSet_u:
            for item in self.dao.trainingSet_u[user].keys():
                value = self.dao.trainingSet_u[user][item]
                a = int(user) - 1
                b = int(item) - 1
                dataArray[a][b] = value
        #T
        dataArrayT = np.transpose(dataArray)
        #cov
        covArray = np.dot(dataArrayT, dataArray)
        #eigen-value-decomposition
        vals, vecs  = np.linalg.eig(covArray)
        # #top-K vals of cov
        k = 3
        valsInd = np.argsort(vals)
        valsInd = valsInd[-1:-(k + 1):-1]
        vecsInd = vecs[:, valsInd]

        newArray = np.dot(dataArray, np.real(vecsInd))
        #print newArray

        distanceDict = {}
        userId = 1
        for user in newArray:
            distance = 0
            #print user
            for tmp in user:
                distance += tmp**2
            distanceDict[userId] = float(distance)
            userId += 1
        print distanceDict

        disSort = sorted(distanceDict.iteritems(), key=lambda d: d[1], reverse=False)
        print disSort
        spamList = []

        i = 1
        while i <= 0.1 * len(disSort):
            spam = disSort[i]
            spamId = spam[0]
            spamList.append(spamId)
            self.predLabels[spamId] = 1
            i += 1
        print self.predLabels

        #trueLabels
        for user in self.dao.trainingSet_u:
            userInd = int(user) -1
            self.trueLabels[userInd] = self.labels[user]
        print self.trueLabels


    def predict(self):
        print classification_report(self.trueLabels, self.predLabels, digits=4)
        return classification_report(self.trueLabels, self.predLabels, digits=4)











