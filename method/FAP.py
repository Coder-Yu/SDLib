from baseclass.SDetection import SDetection
from sklearn.metrics import classification_report
import numpy as np
import random
from sklearn import metrics

class FAP(SDetection):
    # s means the number of seedUser who be regarded as spammer in training
    s = 70
    # predict top-k user as spammer
    k = 80

    def __init__(self, conf, trainingSet=None, testSet=None, labels=None, fold='[1]'):
        super(FAP, self).__init__(conf, trainingSet, testSet, labels, fold)

    # record self.userAvg,user.totalAvvg,self.itemAvvvg
    def __getAverage(self):
        # average rating of the user, the average rating of the item, and the global average
        self.userAvg = {}
        self.totalAvg = 0
        for user in self.dao.trainingSet_u:
            avgPoint = 0
            for item in self.dao.trainingSet_u[user]:
                avgPoint += float(self.dao.trainingSet_u[user][item])
                self.totalAvg += float(self.dao.trainingSet_u[user][item])
            avgPoint = avgPoint / len(self.dao.trainingSet_u[user])
            self.userAvg[user] = avgPoint
        self.totalAvg = self.totalAvg / self.dao.trainingSize()[2]

        self.itemAvg = {}
        for item in self.dao.trainingSet_i:
            avgPoint = 0
            for user in self.dao.trainingSet_i[item]:
                avgPoint += float(self.dao.trainingSet_i[item][user])
            avgPoint = avgPoint / len(self.dao.trainingSet_i[item])
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
                if (user not in self.bipartiteGraphUI) or (item not in self.bipartiteGraphUI[user]):
                    continue
                else:
                    w = float(self.bipartiteGraphUI[user][item])
                    # to avoid positive feedback and reliability problem,we should Polish the w
                    otherItemW = 0
                    otherUserW = 0
                    for otherItem in self.bipartiteGraphUI[user]:
                        otherItemW += float(self.bipartiteGraphUI[user][otherItem])
                    for otherUser in self.dao.trainingSet_i[item]:
                        otherUserW += float(self.bipartiteGraphUI[otherUser][item])
                    wPrime = w
                    self.TPUI[i][j] = wPrime / otherItemW
                    self.TPIU[j][i] = wPrime / otherUserW

    def initModel(self):
        print "compute average value..."
        self.__getAverage()
        # construction of the bipartite graph
        print "constrructe the bipartite graph..."
        self.bipartiteGraphUI = {}
        for user in self.dao.trainingSet_u:
            tmpUserItemDic = {}  # user-item-point
            for item in self.dao.trainingSet_u[user]:
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
        print "compute the transition probability..."
        self.__computeTProbability()

    def isConvergence(self, PUser, PUserOld):
        if len(PUserOld) == 0:
            return True
        for i in range(0, len(PUser)):
            if (PUser[i] - PUserOld[i]) > 0.01:
                return True
        return False

    def buildModel(self):
        # -------init--------
        m, n, tmp = self.dao.trainingSize()
        PUser = np.zeros(m)
        PItem = np.zeros(n)
        self.trueLabels = [0 for i in range(m)]
        self.predLabels = [0 for i in range(m)]

        seedUser = []
        for i in range(0, self.s):
            randNum = random.randint(0, m - 1)
            while (randNum in seedUser) or (self.labels[str(randNum + 1)] == '0'):
                randNum = random.randint(0, m - 1)
            seedUser.append(randNum)
        #print seedUser

        for j in range(0, m):
            if j in seedUser:
                PUser[j] = 1
            else:
                PUser[j] = random.random()
        for tmp in range(0, n):
            PItem[tmp] = random.random()

        # -------iterator-------
        PUserOld = []
        iterator = 0
        while self.isConvergence(PUser, PUserOld):
            for j in seedUser:
                PUser[j] = 1
            PUserOld = PUser
            PItem = np.dot(self.TPIU, PUser)
            PUser = np.dot(self.TPUI, PItem)
            iterator += 1
            print 'This is', iterator,'iterator'

        PUserDict = {}
        userId = 1
        for i in PUser:
            PUserDict[userId] = i
            userId += 1
        for j in seedUser:
            del PUserDict[j]
        #print len(PUserDict)


        # predLabels
        PSort = sorted(PUserDict.iteritems(), key=lambda d: d[1], reverse=True)
        #print PSort
        # top-k user as spammer
        spamList = []
        index = 0
        while index < self.k:
            spam = PSort[index]
            spamId = int(spam[0] - 1)
            spamList.append(spamId)
            self.predLabels[spamId] = 1
            index += 1
            # print self.predLabels

        # trueLabels
        for user in self.dao.trainingSet_u:
            userInd = int(user) - 1
            self.trueLabels[userInd] = int(self.labels[user])
        #print len(self.trueLabels)

        #delete seedUser labels
        differ = 0
        for user in seedUser:
            user = int(user - differ)
            #print type(user)
            del self.predLabels[user]
            del self.trueLabels[user]
            differ +=1
        #print len(self.trueLabels), self.trueLabels
        #print len(self.predLabels), self.predLabels


    def predict(self):
        print classification_report(self.trueLabels, self.predLabels, digits=4)
        print metrics.confusion_matrix(self.trueLabels, self.predLabels)
        return classification_report(self.trueLabels, self.predLabels, digits=4)
