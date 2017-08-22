#coding:utf-8
from baseclass.SDetection import SDetection
from sklearn.metrics import classification_report
from sklearn.cross_validation import train_test_split
import numpy as np
import math
from sklearn.naive_bayes import GaussianNB


class SemiSAD(SDetection):
    def __init__(self, conf, trainingSet=None, testSet=None, labels=None, fold='[1]'):
        super(SemiSAD, self).__init__(conf, trainingSet, testSet, labels, fold)

    def readConfiguration(self):
        super(SemiSAD, self).readConfiguration()
        # K = top-K vals of cov
        self.k = int(self.config['topK'])
        # Lambda = λ参数
        self.Lambda = float(self.config['Lambda'])

    def buildModel(self):
        self.H = {}
        self.DegSim = {}
        self.LengVar = {}
        self.RDMA = {}
        self.FMTD = {}
        print 'Begin feature engineering...'
        # computing H,DegSim,LengVar,RDMA,FMTD for LabledData set
        trainingIndex = 0
        testIndex = 0
        trainingUserCount, trainingItemCount, trainingrecordCount = self.dao.trainingSize()
        testUserCount, testItemCount, testrecordCount = self.dao.testSize()
        for user in self.dao.trainingSet_u:
            trainingIndex += 1
            self.H[user] = 0
            for i in range(10,50,5):
                n = 0
                for item in self.dao.trainingSet_u[user]:
                    if(self.dao.trainingSet_u[user][item]==(i/10.0)):
                        n+=1
                if n==0:
                    self.H[user] += 0
                else:
                    self.H[user] += (-(n/(trainingUserCount*1.0))*math.log(n/(trainingUserCount*1.0),2))

            SimList = []
            self.DegSim[user] = 0
            for user1 in self.dao.trainingSet_u:
                userA, userB, C, D, E, Count = 0,0,0,0,0,0
                for item in list(set(self.dao.trainingSet_u[user]).intersection(set(self.dao.trainingSet_u[user1]))):
                    userA += self.dao.trainingSet_u[user][item]
                    userB += self.dao.trainingSet_u[user1][item]
                    Count += 1
                if Count==0:
                    AverageA = 0
                    AverageB = 0
                else:
                    AverageA = userA/Count
                    AverageB = userB/Count
                for item in list(set(self.dao.trainingSet_u[user]).intersection(set(self.dao.trainingSet_u[user1]))):
                    C += (self.dao.trainingSet_u[user][item]-AverageA)*(self.dao.trainingSet_u[user1][item]-AverageB)
                    D += np.square(self.dao.trainingSet_u[user][item]-AverageA)
                    E += np.square(self.dao.trainingSet_u[user1][item]-AverageB)
                if C==0:
                    SimList.append(0.0)
                else:
                    SimList.append(C/(math.sqrt(D)*math.sqrt(E)))
            SimList.sort(reverse=True)
            for i in range(1,self.k+1):
                self.DegSim[user] += SimList[i] / (self.k)

            GlobalAverage = 0
            F = 0
            for user2 in self.dao.trainingSet_u:
                GlobalAverage += len(self.dao.trainingSet_u[user2]) / (len(self.dao.trainingSet_u) + 0.0)
            for user3 in self.dao.trainingSet_u:
                F += pow(len(self.dao.trainingSet_u[user3])-GlobalAverage,2)
            self.LengVar[user] = abs(len(self.dao.trainingSet_u[user])-GlobalAverage)/(F*1.0)

            Divisor = 0
            for item1 in self.dao.trainingSet_u[user]:
                Divisor += abs(self.dao.trainingSet_u[user][item1]-self.dao.itemMeans[item1])/len(self.dao.trainingSet_i[item1])
            self.RDMA[user] = Divisor/len(self.dao.trainingSet_u[user])

            Minuend, index1, Subtrahend, index2 = 0, 0, 0, 0
            for item3 in self.dao.trainingSet_u[user]:
                if(self.dao.trainingSet_u[user][item3]==5.0 or self.dao.trainingSet_u[user][item3]==1.0) :
                    Minuend += sum(self.dao.trainingSet_i[item3].values())
                    index1 += len(self.dao.trainingSet_i[item3])
                else:
                    Subtrahend += sum(self.dao.trainingSet_i[item3].values())
                    index2 += len(self.dao.trainingSet_i[item3])
            if index1 == 0 and index2 == 0:
                self.FMTD[user] = 0
            elif index1 == 0:
                self.FMTD[user] = abs(Subtrahend / index2)
            elif index2 == 0:
                self.FMTD[user] = abs(Minuend / index1)
            else:
                self.FMTD[user] = abs(Minuend / index1 - Subtrahend / index2)

            if trainingIndex==(trainingUserCount/5):
                print 'trainingData Done 20%...'
            elif trainingIndex==(trainingUserCount/5*2):
                print 'trainingData Done 40%...'
            elif trainingIndex==(trainingUserCount/5*3):
                print 'trainingData Done 60%...'
            elif trainingIndex==(trainingUserCount/5*4):
                print 'trainingData Done 80%...'
            elif trainingIndex==(trainingUserCount):
                print 'trainingData Done 100%...'

        # computing H,DegSim,LengVar,RDMA,FMTD for UnLabledData set
        for user in self.dao.testSet_u:
            testIndex += 1
            self.H[user] = 0
            for i in range(10,50,5):
                n = 0
                for item in self.dao.testSet_u[user]:
                    if(self.dao.testSet_u[user][item]==(i/10.0)):
                        n+=1
                if n==0:
                    self.H[user] += 0
                else:
                    self.H[user] += (-(n/(testUserCount*1.0))*math.log(n/(testUserCount*1.0),2))

            SimList = []
            self.DegSim[user] = 0
            for user1 in self.dao.testSet_u:
                userA, userB, C, D, E, Count = 0,0,0,0,0,0
                for item in list(set(self.dao.testSet_u[user]).intersection(set(self.dao.testSet_u[user1]))):
                    userA += self.dao.testSet_u[user][item]
                    userB += self.dao.testSet_u[user1][item]
                    Count += 1
                if Count==0:
                    AverageA = 0
                    AverageB = 0
                else:
                    AverageA = userA/Count
                    AverageB = userB/Count
                for item in list(set(self.dao.testSet_u[user]).intersection(set(self.dao.testSet_u[user1]))):
                    C += (self.dao.testSet_u[user][item]-AverageA)*(self.dao.testSet_u[user1][item]-AverageB)
                    D += np.square(self.dao.testSet_u[user][item]-AverageA)
                    E += np.square(self.dao.testSet_u[user1][item]-AverageB)
                if C==0:
                    SimList.append(0.0)
                else:
                    SimList.append(C/(math.sqrt(D)*math.sqrt(E)))
            SimList.sort(reverse=True)
            for i in range(1,self.k+1):
                self.DegSim[user] += SimList[i] / self.k

            GlobalAverage = 0
            F = 0
            for user2 in self.dao.testSet_u:
                GlobalAverage += len(self.dao.testSet_u[user2]) / (len(self.dao.testSet_u) + 0.0)
            for user3 in self.dao.testSet_u:
                F += pow(len(self.dao.testSet_u[user3])-GlobalAverage,2)
            self.LengVar[user] = abs(len(self.dao.testSet_u[user])-GlobalAverage)/(F*1.0)

            Divisor = 0
            for item1 in self.dao.testSet_u[user]:
                Divisor += abs(self.dao.testSet_u[user][item1]-self.dao.itemMeans[item1])/len(self.dao.testSet_i[item1])
            self.RDMA[user] = Divisor/len(self.dao.testSet_u[user])

            Minuend, index1, Subtrahend, index2= 0,0,0,0
            for item3 in self.dao.testSet_u[user]:
                if(self.dao.testSet_u[user][item3]==5.0 or self.dao.testSet_u[user][item3]==1.0):
                    Minuend += sum(self.dao.testSet_i[item3].values())
                    index1 += len(self.dao.testSet_i[item3])
                else:
                    Subtrahend += sum(self.dao.testSet_i[item3].values())
                    index2 += len(self.dao.testSet_i[item3])
            if index1 == 0 and index2 == 0:
                self.FMTD[user] = 0
            elif index1 == 0:
                self.FMTD[user] = abs(Subtrahend / index2)
            elif index2 == 0:
                self.FMTD[user] = abs(Minuend / index1)
            else:
                self.FMTD[user] = abs(Minuend / index1 - Subtrahend / index2)

            if testIndex == testUserCount / 5:
                 print 'testData Done 20%...'
            elif testIndex == testUserCount / 5 * 2:
                print 'testData Done 40%...'
            elif testIndex == testUserCount / 5 * 3:
                print 'testData Done 60%...'
            elif testIndex == testUserCount / 5 * 4:
                print 'testData Done 80%...'
            elif testIndex == testUserCount:
                print 'testData Done 100%...'

        # preparing examples training for LabledData ,test for UnLableData

        for user in self.dao.trainingSet_u:
            self.training.append([self.H[user], self.DegSim[user], self.LengVar[user],self.RDMA[user],self.FMTD[user]])
            self.trainingLabels.append(self.labels[user])

        for user in self.dao.testSet_u:
            self.test.append([self.H[user], self.DegSim[user], self.LengVar[user],self.RDMA[user],self.FMTD[user]])
            self.testLabels.append(self.labels[user])

    def predict(self):
            ClassifierN = 0
            classifier = GaussianNB()
            #X_train,X_test,y_train,y_test = train_test_split(self.training,self.trainingLabels,test_size=0.1,random_state=33)
            classifier.fit(self.training, self.trainingLabels)
            # predict UnLabledData
            pred_labelsForTrainingUn = classifier.predict(self.test)
            print 'Enhanced classifier...'
            while 1 :
                p1 = pred_labelsForTrainingUn
                # 将带λ参数的无标签数据拟合入分类器
                classifier.partial_fit(self.test, pred_labelsForTrainingUn,classes=['0','1'], sample_weight=np.ones(len(self.test),dtype=np.float)*self.Lambda)
                pred_labelsForTrainingUn = classifier.predict(self.test)
                p2 = pred_labelsForTrainingUn
                # 判断分类器是否稳定
                if list(p1)==list(p2) :
                    ClassifierN += 1
                elif ClassifierN > 0:
                    ClassifierN = 0
                if ClassifierN == 20:
                    break
            pred_labels = classifier.predict(self.test)
            print 'naive_bayes with EM algorithm:'
            return pred_labels