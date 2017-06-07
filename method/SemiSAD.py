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

    def buildModel(self):
        # K = top-K vals of cov
        self.k = 3
        # Lambda = λ参数
        self.Lambda = 0.5

        self.H = {}
        self.DegSim = {}
        self.LengVar = {}
        self.RDMA = {}
        self.FMTD = {}
        # computing H,DegSim,LengVar,RDMA,FMTD for LabledData set
        self.itemMeans = {}
        #self.SimList = {}
        for user in self.dao.trainingSet_u:
            S = len(self.dao.trainingSet_u[user])
            self.H[user] = 0
            for i in range(10,50,5):
                n = 0
                for item in self.dao.trainingSet_u[user]:
                    if(self.dao.trainingSet_u[user][item]==(i/10.0)):
                        n+=1
                if n==0:
                    self.H[user] += 0
                else:
                    self.H[user] += (-(n/(S*1.0))*math.log(n/(S*1.0)))

            SimList = []
            self.DegSim[user] = 0
            for user1 in self.dao.trainingSet_u:
                A = 0
                B = 0
                C = 0
                D = 0
                E = 0
                N = 0
                for item in list(set(self.dao.trainingSet_u[user]).intersection(set(self.dao.trainingSet_u[user1]))):
                    A += self.dao.trainingSet_u[user][item]
                    B += self.dao.trainingSet_u[user1][item]
                    N += 1
                if N==0:
                    AverageA = 0
                    AverageB = 0
                else:
                    AverageA = A/N
                    AverageB = B/N
                for item in list(set(self.dao.trainingSet_u[user]).intersection(set(self.dao.trainingSet_u[user1]))):
                    C += (self.dao.trainingSet_u[user][item]-AverageA)*(self.dao.trainingSet_u[user1][item]-AverageB)
                    D += np.square(self.dao.trainingSet_u[user][item]-AverageA)
                    E += np.square(self.dao.trainingSet_u[user1][item]-AverageB)
                if C==0:
                    SimList.append(0.0)
                else:
                    SimList.append(C/(math.sqrt(D)*math.sqrt(E)))
            SimList.sort(reverse=True)
            if self.k<= len(SimList):
                for i in range(1,self.k):
                    self.DegSim[user] += SimList[i]/self.k
            else:
                for i in range(1,len(SimList)):
                    self.DegSim[user] += SimList[i] / self.k

            GlobalAverage = 0
            F = 0
            for user2 in self.dao.trainingSet_u:
                GlobalAverage += len(self.dao.trainingSet_u[user2]) / (len(self.dao.trainingSet_u) + 0.0)
            for user3 in self.dao.trainingSet_u:
                F += pow(len(self.dao.trainingSet_u[user3])-GlobalAverage,2)
            self.LengVar[user] = abs(len(self.dao.trainingSet_u[user])-GlobalAverage)/(F*1.0)

            Divisor = 0
            for item1 in self.dao.trainingSet_i:
                self.itemMeans[item1] = sum(self.dao.trainingSet_i[item1].values()) / (len(self.dao.trainingSet_i[item1]) + 0.0)
            for item2 in self.dao.trainingSet_u[user]:
                Divisor += abs(self.dao.trainingSet_u[user][item2]-self.itemMeans[item2])/len(self.dao.trainingSet_i[item2])
            self.RDMA[user] = Divisor/len(self.dao.trainingSet_u[user])

            Minuend = 0
            index1 = 0
            Subtrahend  = 0
            index2 = 0
            for item3 in self.dao.trainingSet_u[user]:
                if(self.dao.trainingSet_u[user][item3]==5.0):
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

        # computing H,DegSim,LengVar,RDMA,FMTD for UnLabledData set
        for user in self.dao.testSet_u:
            S = len(self.dao.testSet_u[user])
            self.H[user] = 0
            for i in range(10,50,5):
                n = 0
                for item in self.dao.testSet_u[user]:
                    if(self.dao.testSet_u[user][item]==(i/10.0)):
                        n+=1
                if n==0:
                    self.H[user] += 0
                else:
                    self.H[user] += (-(n/(S*1.0))*math.log(n/(S*1.0)))

            SimList = []
            self.DegSim[user] = 0
            for user1 in self.dao.testSet_u:
                A = 0
                B = 0
                C = 0
                D = 0
                E = 0
                N = 0
                for item in list(set(self.dao.testSet_u[user]).intersection(set(self.dao.testSet_u[user1]))):
                    A += self.dao.testSet_u[user][item]
                    B += self.dao.testSet_u[user1][item]
                    N += 1
                if N==0:
                    AverageA = 0
                    AverageB = 0
                else:
                    AverageA = A/N
                    AverageB = B/N
                for item in list(set(self.dao.testSet_u[user]).intersection(set(self.dao.testSet_u[user1]))):
                    C += (self.dao.testSet_u[user][item]-AverageA)*(self.dao.testSet_u[user1][item]-AverageB)
                    D += np.square(self.dao.testSet_u[user][item]-AverageA)
                    E += np.square(self.dao.testSet_u[user1][item]-AverageB)
                if C==0:
                    SimList.append(0.0)
                else:
                    SimList.append(C/(math.sqrt(D)*math.sqrt(E)))
            SimList.sort(reverse=True)
            if self.k<= len(SimList):
                for i in range(1,self.k):
                    self.DegSim[user] += SimList[i]/self.k
            else:
                for i in range(1,len(SimList)):
                    self.DegSim[user] += SimList[i] / self.k

            GlobalAverage = 0
            F = 0
            for user2 in self.dao.testSet_u:
                GlobalAverage += len(self.dao.testSet_u[user2]) / (len(self.dao.testSet_u) + 0.0)
            for user3 in self.dao.testSet_u:
                F += pow(len(self.dao.testSet_u[user3])-GlobalAverage,2)
            self.LengVar[user] = abs(len(self.dao.testSet_u[user])-GlobalAverage)/(F*1.0)

            Divisor = 0
            for item1 in self.dao.testSet_i:
                self.itemMeans[item1] = sum(self.dao.testSet_i[item1].values()) / (len(self.dao.testSet_i[item1]) + 0.0)
            for item2 in self.dao.testSet_u[user]:
                Divisor += abs(self.dao.testSet_u[user][item2]-self.itemMeans[item2])/len(self.dao.testSet_i[item2])
            self.RDMA[user] = Divisor/len(self.dao.testSet_u[user])

            Minuend = 0
            index1 = 0
            Subtrahend  = 0
            index2 = 0
            for item3 in self.dao.testSet_u[user]:
                if(self.dao.testSet_u[user][item3]==5.0):
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


         # preparing examples training for LabledData ,test for UnLableData
        self.training = []
        self.trainingLabels = []
        self.test = []
        self.testLabels = []

        for user in self.dao.trainingSet_u:
            self.training.append([self.H[user], self.DegSim[user], self.LengVar[user],self.RDMA[user],self.FMTD[user]])
            self.trainingLabels.append(self.labels[user])

        for user in self.dao.testSet_u:
            self.test.append([self.H[user], self.DegSim[user], self.LengVar[user],self.RDMA[user],self.FMTD[user]])
            self.testLabels.append(self.labels[user])

    def predict(self):
            classifier = GaussianNB()
            #X_train,X_test,y_train,y_test = train_test_split(self.training,self.trainingLabels,test_size=0.1,random_state=33)
            classifier.fit(self.training, self.trainingLabels)
            # predict UnLabledData
            pred_labelsForTrainingUn = classifier.predict(self.test)
            while 1 :
                p1 = pred_labelsForTrainingUn
                # 将带λ参数的无标签数据拟合入分类器
                classifier.partial_fit(self.test, pred_labelsForTrainingUn,classes=['0','1'], sample_weight=np.ones(len(self.test),dtype=np.float)*self.Lambda)
                pred_labelsForTrainingUn = classifier.predict(self.test)
                p2 = pred_labelsForTrainingUn
                # 判断分类器是否稳定
                if list(p1)==list(p2) :
                    break
            pred_labels = classifier.predict(self.test)
            print 'naive_bayes:'
            print classification_report(self.testLabels, pred_labels, digits=4)
            return classification_report(self.testLabels, pred_labels, digits=4)