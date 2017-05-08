from baseclass.SDetection import SDetection
from sklearn.metrics import classification_report
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
#from sklearn import preprocessing
import math

class PCASelectUsers(SDetection):
    def __init__(self, conf, trainingSet=None, testSet=None, labels=None, fold='[1]'):
        super(PCASelectUsers, self).__init__(conf, trainingSet, testSet, labels, fold)

    def buildModel(self):
        #matrix initialization
        userNum = len(self.dao.trainingSet_u)
        itemNum = len(self.dao.trainingSet_i)
        #print userNum, itemNum
        dataArray = np.zeros([userNum, itemNum], dtype=float)
        #print dataArray.shape

        # # z-scores
        # for user in self.dao.trainingSet_u:
        #     rateNum = len(self.dao.trainingSet_u[user])
        #     rateSum = 0
        #     for item in self.dao.trainingSet_u[user].keys():
        #         rateSum += self.dao.trainingSet_u[user][item]
        #     rateMean = '%.4f' % (rateSum*1.0 / rateNum)
        #     # rateStd = 0
        #     # for item in self.dao.trainingSet_u[user].keys():
        #     #     rateStd += (float(self.dao.trainingSet_u[user][item]) - float(rateMean))**2
        #     # rateStd = '%.4f' %( math.sqrt(rateStd / rateNum))
        #
        #     for item in self.dao.trainingSet_u[user].keys():
        #         self.dao.trainingSet_u[user][item] = '%.4f' % (float(self.dao.trainingSet_u[user][item]) - float(rateMean))
        # print self.dao.trainingSet_u

        #add data
        for user in self.dao.trainingSet_u:
            for item in self.dao.trainingSet_u[user].keys():
                value = self.dao.trainingSet_u[user][item]
                a = int(user) - 1
                b = int(item) - 1
                dataArray[a][b] = value

        dataMatrix = csr_matrix(dataArray)
        #print dataMatrix
        #print dataMatrix.shape

        #T
        dataMatrixT = csr_matrix.transpose(dataMatrix)
        #cov
        covMatrix = dataMatrixT.dot(dataMatrix)
        covArry = covMatrix.toarray()
        D,V = np.linalg.eig(covArry)
        pca1 = V[:, 0]
        pca2 = V[:, 1]
        pca3 = V[:, 3]









        # eigen-value-decomposition
        # first eigenvector of cov
        # second eigenvector of cov
        # third  eigenvector of cov
        # distance





        '''
        #z-scores
        # rateSum_u = csr_matrix.sum(dataMatrix, 1)
        # rateNnz_u = np.count_nonzero(dataMatrix)(axis = 1)
        # print rateNnz_u

        rateMean_uDict = {}
        userIndex = 1
        for user in dataMatrix:
            #print user
            rateSum_u = csr_matrix.sum(user)
            #print rateSum_u
            rateNum_u = rateNum_uDict.get(str(userIndex))
            #print rateNum_u
            rateMean_u = '%.4f' % (rateSum_u / rateNum_u)
            rateMean_uDict[str(userIndex)] = rateMean_u
            #print rateMean_u
            userIndex += 1
        #print rateMean_uDict

        userIndex_n = 1
        for user in dataMatrix:
            user.data = user.data - float(rateMean_uDict.get(str(userIndex_n)))
        print dataMatrix[0,]
            # min_max_scaler = preprocessing.MinMaxScaler
            # user.data = min_max_scaler.fit_transform(userRate)
        #     print user.data
        #     userIndex_n += 1
        # print dataMatrix


            # rateNz_u = np.count_nonzero(user)
            # print rateNz_u
        '''

        #cov




        #eigen-value-decomposition
        #first eigenvector of cov
        #second eigenvector of cov
        #third  eigenvector of cov
        #distance










