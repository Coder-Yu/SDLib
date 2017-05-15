from baseclass.SDetection import SDetection
from sklearn.metrics import classification_report
from sklearn import preprocessing
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

        dataArray = preprocessing.scale(dataArray, axis=0)
        dataArrayT = np.transpose(dataArray)
        #cov
        covArray = np.dot(dataArrayT, dataArray)
        #eigen-value-decomposition
        vals, vecs  = np.linalg.eig(covArray)
        #top-K vals of cov
        k = 5
        valsInd = np.argsort(vals)
        #valsInd = valsInd[-1:-(k + 1):-1]
        valsInd = valsInd[0:k:1]
        #use np.real() to get real parts
        vecsInd = np.real(vecs[:, valsInd])
        print vecsInd
        pca_1 = []
        pca_2 = []
        pca_3 = []
        # pca_4 = []
        # pca_5 = []
        for i in vecsInd:
            pca_1.append(i[0])
            pca_2.append(i[1])
            pca_3.append(i[2])
            # pca_4.append(i[3])
            # pca_5.append(i[4])
        # print pca_1
        # print pca_2
        # print pca_3

        newArray = np.dot(dataArray**2, np.real(vecsInd))
        #print newArray

        distanceDict = {}
        userId = 1
        for user in newArray:
            distance = 0
            #print user
            for tmp in user:
                distance += tmp
            distanceDict[userId] = float(distance)
            userId += 1
        #print distanceDict

        disSort = sorted(distanceDict.iteritems(), key=lambda d: d[1], reverse=False)
        #print disSort
        spamList = []

        i = 0
        while i <= 0.1 * len(disSort):
            spam = disSort[i]
            spamId = int(spam[0]-1)
            spamList.append(spamId)
            self.predLabels[spamId] = 1
            i += 1

        #trueLabels
        for user in self.dao.trainingSet_u:
            userInd = int(user) -1
            self.trueLabels[userInd] = self.labels[user]
        #print self.trueLabels


    def predict(self):
        print classification_report(self.trueLabels, self.predLabels, digits=4)
        return classification_report(self.trueLabels, self.predLabels, digits=4)











