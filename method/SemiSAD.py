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
        for user in self.dao.trainingSet_u:
            S = len(self.dao.trainingSet_u[user].values())
            for i in range(1,5,0.5):
                n = 0
                for item in self.dao.trainingSet_u[user]:
                    if(self.dao.trainingSet_u[user][item].values()==i):
                        n+=1
                self.H[user] += -(n/S)*math.log(n/S)

            for user1 in self.trainingSet_u:
                A = 0
                B = 0
                N = 0
                for item in list(set(self.dao.trainingSet_u[user]).intersection(set(self.dao.trainingSet_u[user1]))):
                    A += self.dao.trainingSet_u[user][item].values()
                    B += self.dao.trainingSet_u[user1][item].values()
                    N += 1
                AverageA = A/N
                AverageB = B/N
                for item in list(set(self.dao.trainingSet_u[user]).intersection(set(self.dao.trainingSet_u[user1]))):
                    SimList =[sum((self.dao.trainingSet_u[user][item].values()-AverageA)*(self.dao.trainingSet_u[user1][item].values()-AverageB))/(math.sqrt(sum(np.square(self.dao.trainingSet_u[user][item].values()-AverageA)))*math.sqrt(sum(np.square(self.dao.trainingSet_u[user1][item].values()-AverageB)))) ]
            SimList.sort(reverse=True)
            for i in range(1,self.k):
                self.DegSim[user] += SimList[i]/self.k

            GlobalAverageMean = sum(self.trainingSet_u.values()) / (len(self.trainingSet_u.values()) + 0.0)
            self.LengVar[user] = abs(sum(self.trainingSet_u[user].values())-GlobalAverageMean)/pow(sum(self.trainingSet_u[user].values())-GlobalAverageMean,2)

            for item in self.trainingSet_i:
                self.itemMeans[item] = sum(self.trainingSet_i[item].values()) / (len(self.trainingSet_i[item].values()) + 0.0)
            for item in self.dao.trainingSet_u[user]:
                Divisor = abs(self.dao.trainingSet_u[user][item].values()-self.itemMeans[item])/len(self.trainingSet_i[item])
            self.RDMA[user] = len(self.trainingSet_u[user])/Divisor

            for item in self.trainingSet_i:
                if(self.dao.trainingSet_u[user][item].values()==5.0):
                    Minuend += sum(self.trainingSet_i[item].values())
                    index1 += len(self.trainingSet_i[item])
                else:
                    Subtrahend += sum(self.trainingSet_i[item].values())
                    index2 += len(self.trainingSet_i[item])
            self.FMTD[user] = abs(Minuend/index1-Subtrahend/index2)


        # computing H,DegSim,LengVar,RDMA,FMTD for UnLabledData set
        for user in self.dao.tesSet_u:
            S = len(self.dao.testSet_u[user].values())
            for i in range(1, 5, 0.5):
                n = 0
                for item in self.dao.testSet_u[user]:
                    if (self.dao.testSet_u[user][item].values() == i):
                        n += 1
                self.H[user] += -(n / S) * math.log(n / S)

            for user1 in self.testSet_u:
                A = 0
                B = 0
                N = 0
                for item in list(set(self.dao.testSet_u[user]).intersection(set(self.dao.testSet_u[user1]))):
                    A += self.dao.testSet_u[user][item].values()
                    B += self.dao.testSet_u[user1][item].values()
                    N += 1
                AverageA = A/N
                AverageB = B/N
                for item in list(set(self.dao.testSet_u[user]).intersection(set(self.dao.testSet_u[user1]))):
                    SimList =[sum((self.dao.testSet_u[user][item].values()-AverageA)*(self.dao.testSet_u[user1][item].values()-AverageB))/(math.sqrt(sum(np.square(self.dao.testSet_u[user][item].values()-AverageA)))*math.sqrt(sum(np.square(self.dao.testSet_u[user1][item].values()-AverageB)))) ]
            SimList.sort(reverse=True)
            for i in range(1,self.k):
                self.DegSim[user] += SimList[i]/self.k

            GlobalAverageMean = sum(self.testSet_u.values()) / (len(self.testSet_u.values()) + 0.0)
            self.LengVar[user] = abs(sum(self.testSet_u[user].values()) - GlobalAverageMean) / pow(sum(self.testSet_u[user].values()) - GlobalAverageMean, 2)

            for item in self.testSet_i:
                self.itemMeans[item] = sum(self.testSet_i[item].values()) / (len(self.testSet_i[item].values()) + 0.0)
            for item in self.dao.testSet_u[user]:
                Divisor = abs(self.dao.testSet_u[user][item].values() - self.itemMeans[item]) / sum(self.testSet_i[item])
            self.RDMA[user] = len(self.testSet_u[user]) / Divisor

            for item in self.testSet_i:
                if (self.dao.testSet_u[user][item].values() == 5.0):
                    Minuend += sum(self.testSet_i[item].values())
                    index1 += len(self.testSet_i[item])
                else:
                    Subtrahend += sum(self.testSet_i[item].values())
                    index2 += len(self.testSet_i[item])
            self.FMTD[user] = abs(Minuend / index1 - Subtrahend / index2)


         # preparing examples training for LabledData ,test for UnLableData
        self.training = []
        self.trainingLabels = []
        self.test = []
        #self.testLabels = []

        for user in self.dao.trainingSet_u:
            self.training.append([self.H[user], self.DegSim[user], self.LengVar[user],self.RDMA[user],self.FMTD[user]])
            self.trainingLabels.append(self.labels[user])

        for user in self.dao.testSet_u:
            self.test.append([self.H[user], self.DegSim[user], self.LengVar[user],self.RDMA[user],self.FMTD[user]])
            #self.testLabels.append(self.labels[user])

        def predict(self):
            classifier = GaussianNB()
            # split LableData To training and test
            X_train,X_test,y_train,y_test = train_test_split(self.training,self.trainingLabels,test_size=0.1,random_state=33)
            classifier.fit(X_train, y_train)
            # predict UnLabledData
            pred_labelsForTrainingUn = classifier.predict(self.test)
            while 1 :
                p1 = pred_labelsForTrainingUn
                # 将带λ参数的无标签数据拟合入分类器
                classifier.partial_fit(self.test, pred_labelsForTrainingUn, sample_weight=Lambda)
                pred_labelsForTrainingUn = classifier.predict(self.test)
                p2 = pred_labelsForTrainingUn
                # 判断分类器是否稳定
                if p1==p2 :
                    break
            pred_labels = classifier.predict(X_test)
            print 'naive_bayes:'
            print classification_report(y_test, pred_labels, digits=4)
            return classification_report(y_test, pred_labels, digits=4)