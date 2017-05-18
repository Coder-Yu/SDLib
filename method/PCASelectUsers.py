from baseclass.SDetection import SDetection
from sklearn.metrics import classification_report
from sklearn import preprocessing
import numpy as np
from sklearn import metrics


class PCASelectUsers(SDetection):
    def __init__(self, conf, trainingSet=None, testSet=None, labels=None, fold='[1]', k=None, n=None ):
        super(PCASelectUsers, self).__init__(conf, trainingSet, testSet, labels, fold)
        # K = top-K vals of cov
        self.k = 3
        # n = attack size
        self.n = 0.1

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
        valsInd = np.argsort(vals)
        valsInd = valsInd[-1:-(self.k + 1):-1]  #descend
        #valsInd = valsInd[0:self.k:1]          #ascend
        #use np.real() to get real parts
        vecsInd = np.real(vecs[:, valsInd])

        newArray = np.dot(dataArray**2, np.real(vecsInd))

        distanceDict = {}
        userId = 1
        for user in newArray:
            distance = 0
            for tmp in user:
                distance += tmp
            distanceDict[userId] = float(distance)
            userId += 1

        #predict spammer
        disSort = sorted(distanceDict.iteritems(), key=lambda d: d[1], reverse=False)
        spamList = []


        i = 0
        while i < self.n * len(disSort):
            spam = disSort[i]
            spamId = int(spam[0]-1)
            spamList.append(spamId)
            self.predLabels[spamId] = 1
            i += 1

        #trueLabels
        for user in self.dao.trainingSet_u:
            userInd = int(user) -1
            self.trueLabels[userInd] = self.labels[user]


    def predict(self):
        print classification_report(self.trueLabels, self.predLabels, digits=4)
        print metrics.confusion_matrix(self.trueLabels, self.predLabels)
        return classification_report(self.trueLabels, self.predLabels, digits=4)











