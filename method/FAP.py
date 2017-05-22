from baseclass.SDetection import SDetection
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
# from random import shuffle
from sklearn.metrics import classification_report
from sklearn.tree import DecisionTreeClassifier
import numpy as np
import math
import random

class FAP(SDetection):
    def __init__(self, conf, trainingSet=None, testSet=None, labels=None, fold='[1]'):
        super(FAP, self).__init__(conf, trainingSet, testSet, labels, fold)

    #record self.userAvg,user.totalAvvg,self.itemAvvvg
    def __getAverage(self):
        # average rating of the user, the average rating of the item, and the global average
        self.userAvg = {}
        self.totalAvg = 0
        for user in self.dao.trainingSet_u:
            avgPoint = 0
            for item in self.dao.trainingSet_u[user].keys():
                avgPoint += float(self.dao.trainingSet_u[user][item])
                self.totalAvg += float(self.dao.trainingSet_u[user][item])
            avgPoint = avgPoint / len(self.dao.trainingSet_u[user].keys())
            self.userAvg[user] = avgPoint
        self.totalAvg = self.totalAvg / self.dao.trainingSize()[2]

        self.itemAvg = {}
        for item in self.dao.trainingSet_i:
            avgPoint = 0
            for user in self.dao.trainingSet_i[item].keys():
                avgPoint += float(self.dao.trainingSet_i[item][user])
            avgPoint = avgPoint / len(self.dao.trainingSet_i[item].keys())
            self.itemAvg[item] = avgPoint

    #product transition probability matrix self.TPUI and self.TPIU
    def __computeTProbability(self):
        #m--user count; n--item count
        m,n,tmp = self.dao.trainingSize() 
        self.TPUI = np.zeros((m,n))
        self.TPIU = np.zeros((n,m))
        for i in range(0,m):
            for j in range(0,n):
                user = str(i)
                item = str(j)
                #if has edge in graph,set a value ;otherwise set 0
                if (user in self.bipartiteGraphUI.keys()) and (item in self.bipartiteGraphUI[user].keys()):
                    w = float(self.bipartiteGraphUI[user][item])
                    #to avoid positive feedback and reliability problem,we should Polish the w 
                    otherItemW = 0
                    otherUserW = 0
                    for otherItem in self.bipartiteGraphUI[user].keys():
                        otherItemW += float(self.bipartiteGraphUI[user][otherItem])
                    for otherUser in self.dao.trainingSet_i[item].keys():
                        otherUserW += float(self.bipartiteGraphUI[otherUser][item])                    
                    wPrime = w 
                    self.TPUI[i][j] = wPrime / otherItemW
                    self.TPIU[j][i] = wPrime / otherUserW

    def initModel(self):
        self.__getAverage()

        #construction of the bipartite graph  
        self.bipartiteGraphUI = {}
        for user in self.dao.trainingSet_u:
            tmpUserItemDic = {}#user-item-point
            for item in self.dao.trainingSet_u[user].keys():
                #tmpItemUserDic = {}#item-user-point
                #compute the w
                recordValue = float(self.dao.trainingSet_u[user][item])
                w = 1 + abs((recordValue - self.userAvg[user]) / self.userAvg[user]) + abs((recordValue - self.itemAvg[item]) / self.itemAvg[item]) + abs((recordValue - self.totalAvg) / self.totalAvg)
                # print w
                #tmpItemUserDic[user] = w
                tmpUserItemDic[item] = w
            #self.bipartiteGraphIU[item] = tmpItemUserDic
            self.bipartiteGraphUI[user] = tmpUserItemDic
        #we do the polish in computing the transition probability
        self.__computeTProbability()
        
        # for i in range(0,1658):
        #     sums = 0
        #     for j in range(0,2071):
        #         sums += self.TPUI[i][j]
        #     #sums should be near to 1
        #     print sums

    def isConvergence(PUser,PUserOld):
        if len(PUserOld) == 0:
            return True
        for i in range(0,len(PUser)):
            if (PUser[i] - PUserOld[i]) > 0.05:
                return False
        return True

    def buildModel(self):
        # -------init--------
        m,n,tmp = self.dao.trainingSize() 
        PUser = np.zeros((m,1))
        PItem = np.zeros((n,1))
        k = 50
        seedUser = []
        for i in range(0,k):
            randNum = random.randint(0,m-1)
            while (randNum in seedUser) or (self.labels[str(randNum+1)] == '0'):
                randNum = random.randint(0,m-1)
            seedUser.append(randNum)
        for j in range(0,m):
            if j in seedUser:
                PUser[j] = 1
            else:
                PUser[j] = random.random()
        for k in range(0,n):
            PItem[k] = random.random()
        #-------iterator-------
        kk = 1
        for i in PUser:
            print i
        PUserOld = []
        while isConvergence(PUser,PUserOld):
            for j in seedUser:
                PUser[j] = 1
            PUserOld = PUser
            PItem = np.dot(self.TPIU,PUser)
            PUser = np.dot(self.TPUI,PItem)



    def predict(self):
        print 'Decision Tree:'
        # print classification_report(self.testLabels, pred_labels,digits=4)
        # return classification_report(self.testLabels, pred_labels,digits=4)