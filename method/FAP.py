from baseclass.SDetection import SDetection
from sklearn.metrics import classification_report
import numpy as np
import random

class FAP(SDetection):
    # s means the number of seedUser who be regarded as spammer in training
    s = 80
    # predict top-k user as spammer
    k = 70

    def __init__(self, conf, trainingSet=None, testSet=None, labels=None, fold='[1]'):
        super(FAP, self).__init__(conf, trainingSet, testSet, labels, fold)

    # record self.userAvg,user.totalAvvg,self.itemAvvvg
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

    # product transition probability matrix self.TPUI and self.TPIU
    def __computeTProbability(self):
        # m--user count; n--item count
        m, n, tmp = self.dao.trainingSize()
        self.TPUI = np.zeros((m, n))
        self.TPIU = np.zeros((n, m))
        for i in range(0, m):
            for j in range(0, n):
                user = str(i)
                item = str(j)
                # if has edge in graph,set a value ;otherwise set 0
                if (user in self.bipartiteGraphUI.keys()) and (item in self.bipartiteGraphUI[user].keys()):
                    w = float(self.bipartiteGraphUI[user][item])
                    # to avoid positive feedback and reliability problem,we should Polish the w
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
        # construction of the bipartite graph
        self.bipartiteGraphUI = {}
        for user in self.dao.trainingSet_u:
            tmpUserItemDic = {}  # user-item-point
            for item in self.dao.trainingSet_u[user].keys():
                # tmpItemUserDic = {}#item-user-point
                # compute the w
                recordValue = float(self.dao.trainingSet_u[user][item])
                w = 1 + abs((recordValue - self.userAvg[user]) / self.userAvg[user]) + abs(
                    (recordValue - self.itemAvg[item]) / self.itemAvg[item]) + abs(
                    (recordValue - self.totalAvg) / self.totalAvg)
                # print w
                # tmpItemUserDic[user] = w
                tmpUserItemDic[item] = w
            # self.bipartiteGraphIU[item] = tmpItemUserDic
            self.bipartiteGraphUI[user] = tmpUserItemDic
        # we do the polish in computing the transition probability
        self.__computeTProbability()

    def isConvergence(self, PUser, PUserOld):
        if len(PUserOld) == 0:
            return True
        for i in range(0, len(PUser)):
            if (PUser[i] - PUserOld[i]) > 0.05:
                return False
        return True

    def buildModel(self):
        # -------init--------
        m, n, tmp = self.dao.trainingSize()
        PUser = np.zeros(m)
        PItem = np.zeros(n)

        seedUser = []
        for i in range(0, self.s):
            randNum = random.randint(0, m - 1)
            while (randNum in seedUser) or (self.labels[str(randNum + 1)] == '0'):
                randNum = random.randint(0, m - 1)
            seedUser.append(randNum)

        for j in range(0, m):
            if j in seedUser:
                PUser[j] = 1
            else:
                PUser[j] = random.random()
        for tmp in range(0, n):
            PItem[tmp] = random.random()

        spammerSet = []
        for user in self.labels:
            if self.labels[user] == '1':
                spammerSet.append(int(user))

        testSet = []
        for user in spammerSet:
            if user not in seedUser:
                testSet.append(user)

        # -------iterator-------
        PUserOld = []
        while self.isConvergence(PUser, PUserOld):
            for j in seedUser:
                PUser[j] = 1
            PUserOld = PUser
            PItem = np.dot(self.TPIU, PUser)
            PUser = np.dot(self.TPUI, PItem)

        PUserDict = {}
        userId = 1
        for i in PUser:
            PUserDict[userId] = i
            userId += 1

        for j in seedUser:
            del PUserDict[j]

        PSort = sorted(PUserDict.iteritems(), key=lambda d: d[1], reverse=True)
        # top-k user as spammer
        spamList = []
        i = 0
        while i < self.k:
            spam = PSort[i]
            spamId = spam[0]
            spamList.append(spamId)
            i += 1

        spam_test = 0
        for i in spamList:
            if i in testSet:
                spam_test += 1

        self.precision = spam_test * 1.0 / len(spamList)
        self.recall = spam_test * 1.0 / len(testSet)
        self.F1 = 2*self.precision*self.recall / (self.precision + self.recall)


    def predict(self):
        print 'Precision@',self.k, 'is:', self.precision
        print 'Recall@',self.k, 'is:', self.recall
        print 'F1@',self.k, 'is:', self.F1
        return self.precision, self.recall, self.F1
