from baseclass.SDetection import SDetection
from tool import config
from sklearn.metrics import classification_report
import numpy as np
import random
from sklearn import metrics

class FAP(SDetection):

    def __init__(self, conf, trainingSet=None, testSet=None, labels=None, fold='[1]'):
        super(FAP, self).__init__(conf, trainingSet, testSet, labels, fold)

    def readConfiguration(self):
        super(FAP, self).readConfiguration()
        # # s means the number of seedUser who be regarded as spammer in training
        self.s =int( self.config['seedUser'])
        # # predict top-k user as spammer
        self.k = int(self.config['topKSpam'])

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

        self.userUserIdDic = {}
        self.itemItemIdDic = {}
        tmpUser = self.dao.user.values()
        tmpUserId = self.dao.user.keys()
        tmpItem = self.dao.item.values()
        tmpItemId = self.dao.item.keys()
        for users in range(0, m):
            self.userUserIdDic[tmpUser[users]] = tmpUserId[users]
        for items in range(0, n):
            self.itemItemIdDic[tmpItem[items]] = tmpItemId[items]
        for i in range(0, m):
            for j in range(0, n):
                user = self.userUserIdDic[i]
                item = self.itemItemIdDic[j]
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
                    # wPrime = w*1.0/(otherUserW * otherItemW)
                    wPrime = w
                    self.TPUI[i][j] = wPrime / otherItemW
                    self.TPIU[j][i] = wPrime / otherUserW
            if i % (m/10) == 0:
                print 'computing transition probaility of user',i

    def initModel(self):
        # construction of the bipartite graph
        print "constrructe bipartite graph..."
        self.bipartiteGraphUI = {}
        for user in self.dao.trainingSet_u:
            tmpUserItemDic = {}  # user-item-point
            for item in self.dao.trainingSet_u[user]:
                # tmpItemUserDic = {}#item-user-point
                recordValue = float(self.dao.trainingSet_u[user][item])
                w = 1 + abs((recordValue - self.dao.userMeans[user]) / self.dao.userMeans[user]) + abs(
                    (recordValue - self.dao.itemMeans[item]) / self.dao.itemMeans[item]) + abs(
                    (recordValue - self.dao.globalMean) / self.dao.globalMean)
                # tmpItemUserDic[user] = w
                tmpUserItemDic[item] = w
            # self.bipartiteGraphIU[item] = tmpItemUserDic
            self.bipartiteGraphUI[user] = tmpUserItemDic
        # we do the polish in computing the transition probability
        print "compute transition probability..."
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

        # preserve the real spammer ID
        spammer = []
        for i in self.dao.user:
            if self.labels[i] == '1':
                spammer.append(self.dao.user[i])

        # preserve seedUser Index
        self.seedUser = []
        randList = []
        for i in range(0, self.s):
            randNum = random.randint(0, len(spammer)-1)
            while randNum in randList:
                randNum = random.randint(0, self.s)
            randList.append(randNum)
            self.seedUser.append(int(spammer[randNum]))

        #initial user and item spam probability
        for j in range(0, m):
            if j in self.seedUser:
                #print type(j),j
                PUser[j] = 1
            else:
                PUser[j] = random.random()
        for tmp in range(0, n):
            PItem[tmp] = random.random()

        # -------iterator-------
        PUserOld = []
        iterator = 0
        while self.isConvergence(PUser, PUserOld):
        #while iterator < 100:
            for j in self.seedUser:
                PUser[j] = 1
            PUserOld = PUser
            PItem = np.dot(self.TPIU, PUser)
            PUser = np.dot(self.TPUI, PItem)
            iterator += 1
            print 'This is', iterator,'iterator'

        PUserDict = {}
        userId = 0
        for i in PUser:
            PUserDict[userId] = i
            userId += 1
        for j in self.seedUser:
            del PUserDict[j]

        self.PSort = sorted(PUserDict.iteritems(), key=lambda d: d[1], reverse=True)


    def predict(self):
        # predLabels
        # top-k user as spammer
        spamList = []
        sIndex = 0
        while sIndex < self.k:
            spam = self.PSort[sIndex][0]
            spamList.append(spam)
            self.predLabels[spam] = 1
            sIndex += 1

        # trueLabels
        for user in self.dao.trainingSet_u:
            userInd = self.dao.user[user]
            # print type(user), user, userInd
            self.trueLabels[userInd] = int(self.labels[user])

        # delete seedUser labels
        differ = 0
        for user in self.seedUser:
            user = int(user - differ)
            # print type(user)
            del self.predLabels[user]
            del self.trueLabels[user]
            differ += 1

        print classification_report(self.trueLabels, self.predLabels, digits=4)
        print metrics.confusion_matrix(self.trueLabels, self.predLabels)
        return classification_report(self.trueLabels, self.predLabels, digits=4)
