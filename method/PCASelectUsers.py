from baseclass.SDetection import SDetection
from sklearn.metrics import classification_report
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
#from sklearn import preprocessing
import math
from sklearn.decomposition import PCA

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

        # pca = PCA(n_components=3)
        # newData = pca.fit_transform(dataArray)
        # print newData


        #dataMatrix = csr_matrix(dataArray)
        #print dataMatrix
        #print dataMatrix.shape

        #T
        #dataMatrixT = csr_matrix.transpose(dataMatrix)
        dataArrayT = np.transpose(dataArray)
        #cov
        #covMatrix = dataMatrixT.dot(dataMatrix)
        covArray = np.dot(dataArray, dataArrayT)
        print covArray.shape

        # # whether the array is symmetric
        # for i in range(0, len(covArray)):
        #     for j in range(0, len(covArray[0])):
        #         if i > j:
        #             continue
        #         if covArray[i][j] != covArray[j][i]:
        #             print 'false'
        # print 'true'

        #covArray = covMatrix.toarray()
        #eigen-value-decomposition
        vals, vecs  = np.linalg.eig(covArray)
        # #top-K vals of cov
        k = 3
        valsSort = np.argsort(vals)
        vecsSort = valsSort[-1:-(k + 1):-1]
        print vecsSort
        vecs_k = vecs[ :, k]
        for i in vecs_k:
            print i


        #print vecs
        # pairs =[(np.abs(vals[i]), vecs[:,i]) for i in range(len(vals))]
        # print pairs
        # pairs.sort(reverse=True)
        # first = pairs[0][1]
        # second = pairs[1][1]
        # third = pairs[2][1]
        # print first
        # print second
        # print third
        #print vecs
        # distance
        #distanceDict_u = {}
        # for user in covArry:
        #     distance = pca1*(user**2)+pca2*(user**2)+pca3*(user**2)
        #     print distance
        #     distanceDict_u[user] = float(distance)
        # print distanceDict_u






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










