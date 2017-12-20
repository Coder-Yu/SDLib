from baseclass.SDetection import SDetection
from sklearn.metrics import classification_report
import numpy as np
from tool import config
from collections import defaultdict
from math import log,exp
from sklearn.tree import DecisionTreeClassifier

#CoDetector: Collaborative Shilling Detection Bridging Factorization and User Embedding
class CoDetector(SDetection):
    def __init__(self, conf, trainingSet=None, testSet=None, labels=None, fold='[1]'):
        super(CoDetector, self).__init__(conf, trainingSet, testSet, labels, fold)

    def readConfiguration(self):
        super(CoDetector, self).readConfiguration()
        extraSettings = config.LineConfig(self.config['CoDetector'])
        self.k = int(extraSettings['-k'])
        self.negCount = int(extraSettings['-negCount'])  # the number of negative samples
        if self.negCount < 1:
            self.negCount = 1

        self.regR = float(extraSettings['-gamma'])
        self.filter = int(extraSettings['-filter'])

        learningRate = config.LineConfig(self.config['learnRate'])
        self.lRate = float(learningRate['-init'])
        self.maxLRate = float(learningRate['-max'])
        self.maxIter = int(self.config['num.max.iter'])
        regular = config.LineConfig(self.config['reg.lambda'])
        self.regU, self.regI = float(regular['-u']), float(regular['-i'])

    def printAlgorConfig(self):
        super(CoDetector, self).printAlgorConfig()
        print 'k: %d' % self.negCount
        print 'regR: %.5f' % self.regR
        print 'filter: %d' % self.filter
        print '=' * 80

    def initModel(self):
        super(CoDetector, self).initModel()
        self.w = np.random.rand(len(self.dao.all_User)+1) / 20  # bias value of user
        self.c = np.random.rand(len(self.dao.all_User)+1)/ 20  # bias value of context
        self.G = np.random.rand(len(self.dao.all_User)+1, self.k) / 20  # context embedding
        self.P = np.random.rand(len(self.dao.all_User)+1, self.k) / 20  # latent user matrix
        self.Q = np.random.rand(len(self.dao.all_Item)+1, self.k) / 20  # latent item matrix


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
        # Jointly decompose R(ratings) and SPPMI with shared user latent factors P
        iteration = 0
        while iteration < self.maxIter:
            self.loss = 0

            self.dao.ratings = dict(self.dao.trainingSet_u, **self.dao.testSet_u)
            for user in self.dao.ratings:
                for item in self.dao.ratings[user]:
                    rating = self.dao.ratings[user][item]
                    error = rating - self.predictRating(user,item)
                    u = self.dao.all_User[user]
                    i = self.dao.all_Item[item]
                    p = self.P[u]
                    q = self.Q[i]
                    self.loss += error ** 2
                    # update latent vectors
                    self.P[u] += self.lRate * (error * q - self.regU * p)
                    self.Q[i] += self.lRate * (error * p - self.regI * q)


            for user in self.SPPMI:
                u = self.dao.all_User[user]
                p = self.P[u]
                for context in self.SPPMI[user]:
                    v = self.dao.all_User[context]
                    m = self.SPPMI[user][context]
                    g = self.G[v]
                    diff = (m - p.dot(g) - self.w[u] - self.c[v])
                    self.loss += diff ** 2
                    # update latent vectors
                    self.P[u] += self.lRate * diff * g
                    self.G[v] += self.lRate * diff * p
                    self.w[u] += self.lRate * diff
                    self.c[v] += self.lRate * diff
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

    def predictRating(self,user,item):
        u = self.dao.all_User[user]
        i = self.dao.all_Item[item]
        return self.P[u].dot(self.Q[i])

    def predict(self):
        classifier =  DecisionTreeClassifier(criterion='entropy')
        classifier.fit(self.training, self.trainingLabels)
        pred_labels = classifier.predict(self.test)
        print 'Decision Tree:'
        return pred_labels