from baseclass.SDetection import SDetection
from sklearn.metrics import classification_report
import numpy as np
from tool import config
from collections import defaultdict
from math import log,exp
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from random import choice
from tool.qmath import sigmoid
import matplotlib
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
import random
#BayesDetector: Collaborative Shilling Detection Bridging Factorization and User Embedding
class BayesDetector(SDetection):
    def __init__(self, conf, trainingSet=None, testSet=None, labels=None, fold='[1]'):
        super(BayesDetector, self).__init__(conf, trainingSet, testSet, labels, fold)

    def readConfiguration(self):
        super(BayesDetector, self).readConfiguration()
        extraSettings = config.LineConfig(self.config['BayesDetector'])
        self.k = int(extraSettings['-k'])
        self.negCount = int(extraSettings['-negCount'])  # the number of negative samples
        if self.negCount < 1:
            self.negCount = 1

        self.regR = float(extraSettings['-gamma'])
        self.filter = int(extraSettings['-filter'])
        self.delta = float(extraSettings['-delta'])
        learningRate = config.LineConfig(self.config['learnRate'])
        self.lRate = float(learningRate['-init'])
        self.maxLRate = float(learningRate['-max'])
        self.maxIter = int(self.config['num.max.iter'])
        regular = config.LineConfig(self.config['reg.lambda'])
        self.regU, self.regI = float(regular['-u']), float(regular['-i'])
        # self.delta = float(self.config['delta'])
    def printAlgorConfig(self):
        super(BayesDetector, self).printAlgorConfig()
        print 'k: %d' % self.negCount
        print 'regR: %.5f' % self.regR
        print 'filter: %d' % self.filter
        print '=' * 80

    def initModel(self):
        super(BayesDetector, self).initModel()
        # self.c = np.random.rand(len(self.dao.all_User) + 1) / 20  # bias value of context
        self.G = np.random.rand(len(self.dao.all_User)+1, self.k) / 100  # context embedding
        self.P = np.random.rand(len(self.dao.all_User)+1, self.k) / 100  # latent user matrix
        self.Q = np.random.rand(len(self.dao.all_Item)+1, self.k) / 100  # latent item matrix

        # constructing SPPMI matrix
        self.SPPMI = defaultdict(dict)
        D = len(self.dao.user)
        print 'Constructing SPPMI matrix...'
        # for larger data set has many items, the process will be time consuming
        occurrence = defaultdict(dict)
        for user1 in self.dao.all_User:
            iList1, rList1 = self.dao.allUserRated(user1)
            if len(iList1) < self.filter:
                continue
            for user2 in self.dao.all_User:
                if user1 == user2:
                    continue
                if not occurrence[user1].has_key(user2):
                    iList2, rList2 = self.dao.allUserRated(user2)
                    if len(iList2) < self.filter:
                        continue
                    count = len(set(iList1).intersection(set(iList2)))
                    if count > self.filter:
                        occurrence[user1][user2] = count
                        occurrence[user2][user1] = count

        maxVal = 0
        frequency = {}
        for user1 in occurrence:
            frequency[user1] = sum(occurrence[user1].values()) * 1.0
        D = sum(frequency.values()) * 1.0
        # maxx = -1
        for user1 in occurrence:
            for user2 in occurrence[user1]:
                try:
                    val = max([log(occurrence[user1][user2] * D / (frequency[user1] * frequency[user2]), 2) - log(
                        self.negCount, 2), 0])
                except ValueError:
                    print self.SPPMI[user1][user2]
                    print self.SPPMI[user1][user2] * D / (frequency[user1] * frequency[user2])
                if val > 0:
                    if maxVal < val:
                        maxVal = val
                    self.SPPMI[user1][user2] = val
                    self.SPPMI[user2][user1] = self.SPPMI[user1][user2]

        # normalize
        for user1 in self.SPPMI:
            for user2 in self.SPPMI[user1]:
                self.SPPMI[user1][user2] = self.SPPMI[user1][user2] / maxVal

    def buildModel(self):
        self.dao.ratings = dict(self.dao.trainingSet_u, **self.dao.testSet_u)
        #suspicous set
        print 'Preparing sets...'
        self.sSet = defaultdict(dict)
        #normal set
        self.nSet = defaultdict(dict)
        # self.NegativeSet = defaultdict(list)

        for user in self.dao.user:
            for item in self.dao.ratings[user]:
                # if self.dao.ratings[user][item] >= 5 and self.labels[user]=='1':
                if self.labels[user] =='1':
                    self.sSet[item][user] = 1
                # if self.dao.ratings[user][item] >= 5 and self.labels[user] == '0':
                if self.labels[user] == '0':
                    self.nSet[item][user] = 1
        # Jointly decompose R(ratings) and SPPMI with shared user latent factors P
        iteration = 0
        while iteration < self.maxIter:
            self.loss = 0

            for item in self.sSet:
                i = self.dao.all_Item[item]
                if not self.nSet.has_key(item):
                    continue
                normalUserList = self.nSet[item].keys()
                for user in self.sSet[item]:
                    su = self.dao.all_User[user]
                    # if len(self.NegativeSet[user]) > 0:
                    #     item_j = choice(self.NegativeSet[user])
                    # else:
                    normalUser = choice(normalUserList)
                    nu = self.dao.all_User[normalUser]

                    s = sigmoid(self.P[su].dot(self.Q[i]) - self.P[nu].dot(self.Q[i]))
                    self.Q[i] += (self.lRate * (1 - s) * (self.P[su] - self.P[nu]))
                    self.P[su] += (self.lRate * (1 - s) * self.Q[i])
                    self.P[nu] -= (self.lRate * (1 - s) * self.Q[i])

                    self.Q[i] -= self.lRate * self.regI * self.Q[i]
                    self.P[su] -= self.lRate * self.regU * self.P[su]
                    self.P[nu] -= self.lRate * self.regU * self.P[nu]

                    self.loss += (-log(s))
            #
            # for item in self.sSet:
            #     if not self.nSet.has_key(item):
            #         continue
            #     for user1 in self.sSet[item]:
            #         for user2 in self.sSet[item]:
            #             su1 = self.dao.all_User[user1]
            #             su2 = self.dao.all_User[user2]
            #             self.P[su1] += (self.lRate*(self.P[su1]-self.P[su2]))*self.delta
            #             self.P[su2] -= (self.lRate*(self.P[su1]-self.P[su2]))*self.delta
            #
            #             self.loss += ((self.P[su1]-self.P[su2]).dot(self.P[su1]-self.P[su2]))*self.delta


            for user in self.dao.ratings:
                for item in self.dao.ratings[user]:
                    rating = self.dao.ratings[user][item]
                    if rating < 5:
                        continue
                    error = rating - self.predictRating(user,item)
                    u = self.dao.all_User[user]
                    i = self.dao.all_Item[item]
                    p = self.P[u]
                    q = self.Q[i]
                    # self.loss += (error ** 2)*self.b
                    # update latent vectors
                    self.P[u] += (self.lRate * (error * q - self.regU * p))
                    self.Q[i] += (self.lRate * (error * p - self.regI * q))


            for user in self.SPPMI:
                u = self.dao.all_User[user]
                p = self.P[u]
                for context in self.SPPMI[user]:
                    v = self.dao.all_User[context]
                    m = self.SPPMI[user][context]
                    g = self.G[v]
                    diff = (m - p.dot(g))
                    self.loss += (diff ** 2)
                    # update latent vectors
                    self.P[u] += (self.lRate * diff * g)
                    self.G[v] += (self.lRate * diff * p)
            self.loss += self.regU * (self.P * self.P).sum() + self.regI * (self.Q * self.Q).sum()  + self.regR * (self.G * self.G).sum()
            iteration += 1
            print 'iteration:',iteration

        # preparing examples
        self.training = []
        self.trainingLabels = []
        self.test = []
        self.testLabels = []

        for user in self.dao.trainingSet_u:
            self.training.append(self.P[self.dao.all_User[user]])
            self.trainingLabels.append(self.labels[user])
        for user in self.dao.testSet_u:
            self.test.append(self.P[self.dao.all_User[user]])
            self.testLabels.append(self.labels[user])
        #
        # tsne = TSNE(n_components=2)
        # self.Y = tsne.fit_transform(self.P)
        #
        # self.normalUsers = []
        # self.spammers = []
        # for user in self.labels:
        #     if self.labels[user] == '0':
        #         self.normalUsers.append(user)
        #     else:
        #         self.spammers.append(user)
        #
        #
        # print len(self.spammers)
        # self.normalfeature = np.zeros((len(self.normalUsers), 2))
        # self.spamfeature = np.zeros((len(self.spammers), 2))
        # normal_index = 0
        # for normaluser in self.normalUsers:
        #     if normaluser in self.dao.all_User:
        #         self.normalfeature[normal_index] = self.Y[self.dao.all_User[normaluser]]
        #         normal_index += 1
        #
        # spam_index = 0
        # for spamuser in self.spammers:
        #     if spamuser in self.dao.all_User:
        #         self.spamfeature[spam_index] = self.Y[self.dao.all_User[spamuser]]
        #         spam_index += 1
        # self.randomNormal = np.zeros((500,2))
        # self.randomSpam = np.zeros((500,2))
        # # for i in range(500):
        # #     self.randomNormal[i] = self.normalfeature[random.randint(0,len(self.normalfeature)-1)]
        # #     self.randomSpam[i] = self.spamfeature[random.randint(0,len(self.spamfeature)-1)]
        # plt.scatter(self.normalfeature[:, 0], self.normalfeature[:, 1], c='red',s=8,marker='o',label='NormalUser')
        # plt.scatter(self.spamfeature[:, 0], self.spamfeature[:, 1], c='blue',s=8,marker='o',label='Spammer')
        # plt.legend(loc='lower left')
        # plt.xticks([])
        # plt.yticks([])
        # plt.savefig('9.png',dpi=500)


    def predictRating(self,user,item):
        u = self.dao.all_User[user]
        i = self.dao.all_Item[item]
        return self.P[u].dot(self.Q[i])

    def predict(self):
        classifier =  RandomForestClassifier(n_estimators=12)
        # classifier = DecisionTreeClassifier(criterion='entropy')
        classifier.fit(self.training, self.trainingLabels)
        pred_labels = classifier.predict(self.test)
        print 'Decision Tree:'
        return pred_labels
