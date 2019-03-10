from baseclass.detector import Detector
from sklearn.metrics import classification_report
import numpy as np
from tool import config
from collections import defaultdict
from math import log,exp
from sklearn.tree import DecisionTreeClassifier
from math import exp
from tool.qmath import sigmoid
#CoDetectorPlus: Collaborative Shilling Detection Bridging Factorization and User Embedding
class CoDetectorPlus(Detector):
    def __init__(self, conf, trainingSet=None, testSet=None, labels=None, fold='[1]'):
        super(CoDetectorPlus, self).__init__(conf, trainingSet, testSet, labels, fold)

    def readConfiguration(self):
        super(CoDetectorPlus, self).readConfiguration()
        extraSettings = config.LineConfig(self.config['CoDetectorPlus'])
        self.k = int(extraSettings['-k'])
        self.negCount = int(extraSettings['-negCount'])  # the number of negative samples
        if self.negCount < 1:
            self.negCount = 1

        self.gamma = float(extraSettings['-gamma'])
        self.filter = int(extraSettings['-filter'])
        learningRate = config.LineConfig(self.config['learnRate'])
        self.lRate = float(learningRate['-init'])
        self.maxLRate = float(learningRate['-max'])
        self.maxIter = int(self.config['num.max.iter'])
        self.beta = float(extraSettings['-beta'])
        self.alpha = float(extraSettings['-alpha'])
        regular = config.LineConfig(self.config['reg.lambda'])
        self.regU, self.regI = float(regular['-u']), float(regular['-i'])

    def printAlgorConfig(self):
        super(CoDetectorPlus, self).printAlgorConfig()
        print 'k: %d' % self.negCount
        print 'gamma: %.5f' % self.gamma
        print 'filter: %d' % self.filter
        print '=' * 80

    def initModel(self):
        super(CoDetectorPlus, self).initModel()
        self.w = np.random.rand(len(self.data.all_User)+1) / 20  # bias value of user
        self.c = np.random.rand(len(self.data.all_User)+1)/ 20  # bias value of context
        self.G = np.random.rand(len(self.data.all_User)+1, self.k) / 20  # context embedding
        self.P = np.random.rand(len(self.data.all_User)+1, self.k) / 20  # latent user matrix
        self.Q = np.random.rand(len(self.data.all_Item)+1, self.k) / 20  # latent item matrix

        # constructing SPPMI matrix
        self.SPPMI = defaultdict(dict)
        #
        # #filter low ratings
        self.highRatings = defaultdict(dict)
        self.data.ratings = dict(self.data.trainingSet_u, **self.data.testSet_u)
        for user in self.data.ratings:
            for item in self.data.ratings[user]:
                if self.data.ratings[user][item]>4.0:
                    self.highRatings[user][item] = self.data.ratings[user][item]
                    #self.data.ratings[user][item] =sigmoid(self.data.ratings[user][item])



        # print 'Constructing SPPMI matrix...'
        # # for larger data set has many items, the process will be time consuming
        #
        # occurrence = defaultdict(dict)
        # i=0
        # for user1 in self.highRatings:
        #     iList1 = self.highRatings[user1].keys()
        #
        #     if len(iList1) < self.filter:
        #         continue
        #     for user2 in self.highRatings:
        #         if user1 == user2:
        #             continue
        #         if not occurrence[user1].has_key(user2):
        #             iList2 = self.highRatings[user2].keys()
        #             if len(iList2) < self.filter:
        #                 continue
        #             count = len(set(iList1).intersection(set(iList2)))
        #             if count > self.filter:
        #                 occurrence[user1][user2] = count
        #                 occurrence[user2][user1] = count
        #     i+=1
        #     if i%200==0:
        #         print i,'/',len(self.highRatings)
        # maxVal = 0
        # frequency = {}
        # for user1 in occurrence:
        #     frequency[user1] = sum(occurrence[user1].values()) * 1.0
        # D = sum(frequency.values()) * 1.0
        # # maxx = -1
        # for user1 in occurrence:
        #     for user2 in occurrence[user1]:
        #         try:
        #             val = max([log(occurrence[user1][user2] * D / (frequency[user1] * frequency[user2]), 2) - log(
        #                 self.negCount, 2), 0])
        #         except ValueError:
        #             print self.SPPMI[user1][user2]
        #             print self.SPPMI[user1][user2] * D / (frequency[user1] * frequency[user2])
        #         if val > 0:
        #             if maxVal < val:
        #                 maxVal = val
        #             self.SPPMI[user1][user2] = val
        #             self.SPPMI[user2][user1] = self.SPPMI[user1][user2]
        # normalize
        # for user1 in self.SPPMI:
        #     for user2 in self.SPPMI[user1]:
        #         self.SPPMI[user1][user2] = self.SPPMI[user1][user2] / maxVal

        import pickle
        f=open('sppmi.mat','wb')
        pickle.dump(self.SPPMI,f)
        #
        # f=open('sppmi.mat','r')
        # self.SPPMI = pickle.load(f)

        #group analysis
        self.conspirator = defaultdict(dict)

        for u1 in self.highRatings:
            if self.labels[u1]=='0' or not self.data.trainingSet_u.has_key(u1):
                continue
            iList1 = self.highRatings[u1].keys()
            s1= set(iList1)
            for u2 in self.highRatings:
                if u1==u2:
                    continue
                if self.labels[u2]=='0' or not self.data.trainingSet_u.has_key(u2):
                    continue
                iList2 = self.highRatings[u2].keys()
                common = len(s1.intersection(set(iList2)))
                if common>3:
                    self.conspirator[u1][u2]=sigmoid(common)




    def buildModel(self):
        # Jointly decompose R(ratings) and SPPMI with shared user latent factors P
        iteration = 0
        while iteration < self.maxIter:
            self.loss = 0
            self.data.ratings = dict(self.data.trainingSet_u, **self.data.testSet_u)
            for user in self.data.ratings:
                for item in self.data.ratings[user]:
                    rating = self.data.ratings[user][item]
                    error = rating -self.predictRating(user,item)
                    u = self.data.all_User[user]
                    i = self.data.all_Item[item]
                    p = self.P[u]
                    q = self.Q[i]
                    self.loss += self.alpha*error ** 2
                    # update latent vectors
                    self.P[u] += self.lRate * self.alpha*(error * q - self.regU * p)
                    self.Q[i] += self.lRate * self.alpha*(error * p - self.regI * q)

            for user in self.SPPMI:
                u = self.data.all_User[user]
                p = self.P[u]
                for context in self.SPPMI[user]:
                    v = self.data.all_User[context]
                    m = self.SPPMI[user][context]
                    g = self.G[v]
                    diff = (m - p.dot(g))# - self.w[u] - self.c[v])
                    self.loss += diff ** 2
                    # update latent vectors
                    self.P[u] += self.lRate * self.gamma* diff * g
                    self.G[v] += self.lRate * self.gamma* diff * p
                    # self.w[u] += self.lRate * diff
                    # self.c[v] += self.lRate * diff


            for user in self.conspirator:
                fPred = 0
                denom = 0
                u = self.data.all_User[user]
                p = self.P[u]
                mates = self.conspirator[user].keys()
                for mate in mates:
                    weight= self.conspirator[user][mate]
                    uf = self.data.all_User[mate]
                    fPred += weight * self.P[uf]
                    denom += weight
                if denom <> 0:
                    matesLoss = p - fPred / denom

                self.loss +=  self.beta *  matesLoss.dot(matesLoss)

                # update latent vectors
                self.P[u] -= self.lRate * self.beta * matesLoss

            self.loss += self.regU * (self.P * self.P).sum() + self.regI * (self.Q * self.Q).sum()  + \
                         self.regU * (self.G * self.G).sum()



            iteration += 1
            print 'iteration:',iteration,'loss:',self.loss

        # preparing examples
        self.training = []
        self.trainingLabels = []
        self.test = []
        self.testLabels = []

        for user in self.data.trainingSet_u:
            self.training.append(self.P[self.data.all_User[user]])
            self.trainingLabels.append(self.labels[user])
        for user in self.data.testSet_u:
            self.test.append(self.P[self.data.all_User[user]])
            self.testLabels.append(self.labels[user])

    def predictRating(self,user,item):
        u = self.data.all_User[user]
        i = self.data.all_Item[item]
        return self.P[u].dot(self.Q[i])

    def predict(self):
        classifier =  DecisionTreeClassifier(criterion='entropy')
        classifier.fit(self.training, self.trainingLabels)
        pred_labels = classifier.predict(self.test)
        print 'Decision Tree:'
        return pred_labels