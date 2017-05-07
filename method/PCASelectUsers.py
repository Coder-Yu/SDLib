from baseclass.SDetection import SDetection
from sklearn.metrics import classification_report
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix

class PCASelectUsers(SDetection):
    def __init__(self, conf, trainingSet=None, testSet=None, labels=None, fold='[1]'):
        super(PCASelectUsers, self).__init__(conf, trainingSet, testSet, labels, fold)

    def buildModel(self):
        #matrix initialization
        userNum = len(self.dao.trainingSet_u)
        itemNum = len(self.dao.trainingSet_i)
        print userNum, itemNum
        dataMatrix = np.zeros([userNum, itemNum], dtype=float)
        print dataMatrix.shape
        #dataMatrix = np.float32(np.mat(data))
        #csr_matrix((userNum, itemNum), dtype=np.int8).toarray()
        #print csr_matrix.shape

        #add data
        for user in self.dao.trainingSet_u:
            for key in self.dao.trainingSet_u[user].keys():
                value = self.dao.trainingSet_u[user][key]
                a = int(user) - 1
                b = int(key) - 1
                dataMatrix[a][b] = value
        #print dataMatrix[0]
        # for i in dataMatrix[0]:
        #     print i
        # print self.dao.trainingSet_u['1']


        #z-scores



        #cov
        #eigen-value-decomposition
        #first eigenvector of cov
        #second eigenvector of cov
        #third  eigenvector of cov
        #distance










