#coding:utf-8
from baseclass.SDetection import SDetection
import math
import numpy as np
from copy import deepcopy
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import classification_report
import random
import heapq
class HySAD(SDetection):
    def __init__(self, conf, trainingSet=None, testSet=None, labels=None, fold='[1]'):
        super(HySAD, self).__init__(conf, trainingSet, testSet, labels, fold)


    def buildModel(self):
        # K = top-K vals of cov
        self.k = 3
        # Lambda = λ参数
        self.Lambda = 0.5

        self.Entropy = {}
        self.DegSim = {}
        self.LengthVar = {}
        self.RDMA = {}
        self.WDMA = {}
        self.WDA = {}
        self.MeanVar = {}
        self.FMTD = {}
        self.FMV = {}
        self.FMD = {}

        # computing Entropy,DegSim,LengthVar,RDMA,FMTD... for LabledData set
        self.itemMeans = {}

        self.nearestUser = []

        for user in self.dao.trainingSet_u:

            S = len(self.dao.trainingSet_u[user])
            self.Entropy[user] = 0
            for i in range(10,50,5):
                n = 0
                for item in self.dao.trainingSet_u[user]:
                    if(self.dao.trainingSet_u[user][item]==(i/10.0)):
                        n+=1
                if n==0:
                    self.Entropy[user] += 0
                else:
                    self.Entropy[user] += (-(n/(S*1.0))*math.log(n/(S*1.0))) #calculate Entropy

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

            self.nearestUser.append(SimList.index(max(SimList)))

            SimList.sort(reverse=True)
            if self.k<= len(SimList):
                for i in range(1,self.k):
                    self.DegSim[user] += SimList[i]/self.k
            else:
                for i in range(1,len(SimList)):
                    self.DegSim[user] += SimList[i] / self.k #calculate DegSim

            GlobalAverage = 0
            F = 0
            for user2 in self.dao.trainingSet_u:
                GlobalAverage += len(self.dao.trainingSet_u[user2]) / (len(self.dao.trainingSet_u) + 0.0)
            for user3 in self.dao.trainingSet_u:
                F += pow(len(self.dao.trainingSet_u[user3])-GlobalAverage,2)
            self.LengthVar[user] = abs(len(self.dao.trainingSet_u[user])-GlobalAverage)/(F*1.0) #calculate Lengthvar

            Divisor1 = 0
            Divisor2 = 0
            SUM = 0
            for item1 in self.dao.trainingSet_i:
                self.itemMeans[item1] = sum(self.dao.trainingSet_i[item1].values()) / (len(self.dao.trainingSet_i[item1]) + 0.0)
            for item2 in self.dao.trainingSet_u[user]:
                Divisor1 += abs(self.dao.trainingSet_u[user][item2]-self.itemMeans[item2])/len(self.dao.trainingSet_i[item2])
                Divisor2 += abs(self.dao.trainingSet_u[user][item2]-self.itemMeans[item2])/((len(self.dao.trainingSet_i[item2]))**2)
                SUM += abs(self.dao.trainingSet_u[user][item2]-self.itemMeans[item2])
            self.FMD[user] = SUM/len(self.dao.trainingSet_u[user])        #calculate FMD
            self.WDA[user] = Divisor1                                     #calculate WDA
            self.RDMA[user] = Divisor1/len(self.dao.trainingSet_u[user])  #calculate RDMA
            self.WDMA[user] = Divisor2/len(self.dao.trainingSet_u[user])  #calculate WDMA

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
                self.FMTD[user] = abs(Minuend / index1 - Subtrahend / index2) #calculate FMTD

            #calculate FMV
            self.Divisor3 = 0
            self.User_m_F  = deepcopy(self.dao.trainingSet_u[user])
            topValue = max(self.User_m_F.values())
            for item4 in self.dao.trainingSet_u[user]:
                if(self.User_m_F[item4]==topValue):
                    del self.User_m_F[item4]
            for item4_1 in self.User_m_F:
                self.Divisor3 += (self.User_m_F[item4_1] - self.itemMeans[item4_1])**2
            if len(self.User_m_F) == 0:
                self.FMV[user] = 0
            else:
                self.FMV[user] =self.Divisor3/len(self.User_m_F)


            #calculate MeanVar
            self.Divisor4 = 0
            self.User_m_t = deepcopy(self.dao.trainingSet_u[user])
            for item5 in self.dao.trainingSet_u[user]:
                if (self.User_m_t[item5]==topValue):
                    del self.User_m_t[item5]
                    break
            for item5_1 in self.User_m_t:
                self.Divisor4 += (self.User_m_t[item5_1] - self.itemMeans[item5_1])**2
            if len(self.dao.trainingSet_u[user])==1:
                self.MeanVar[user] = 0
            else:
                self.MeanVar[user]= self.Divisor4/(len(self.dao.trainingSet_u[user])-1)


        # computing Entropy,DegSim,LengthVar,RDMA,FMTD.... for UnLabledData set
        for user in self.dao.testSet_u:
            S = len(self.dao.testSet_u[user])
            self.Entropy[user] = 0
            for i in range(10,50,5):
                n = 0
                for item in self.dao.testSet_u[user]:
                    if(self.dao.testSet_u[user][item]==(i/10.0)):
                        n+=1
                if n==0:
                    self.Entropy[user] += 0
                else:
                    self.Entropy[user] += (-(n/(S*1.0))*math.log(n/(S*1.0))) #calculate Entropy

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
                    self.DegSim[user] += SimList[i] / self.k  #calculate DegSim

            GlobalAverage = 0
            F = 0
            for user2 in self.dao.testSet_u:
                GlobalAverage += len(self.dao.testSet_u[user2]) / (len(self.dao.testSet_u) + 0.0)
            for user3 in self.dao.testSet_u:
                F += pow(len(self.dao.testSet_u[user3])-GlobalAverage,2)
            self.LengthVar[user] = abs(len(self.dao.testSet_u[user])-GlobalAverage)/(F*1.0) #calculate Lengthvar

            Divisor1 = 0
            Divisor2 = 0
            SUM =0
            for item1 in self.dao.testSet_i:
                self.itemMeans[item1] = sum(self.dao.testSet_i[item1].values()) / (len(self.dao.testSet_i[item1]) + 0.0)
            for item2 in self.dao.testSet_u[user]:
                Divisor1 += abs(self.dao.testSet_u[user][item2]-self.itemMeans[item2])/len(self.dao.testSet_i[item2])
                Divisor2 += abs(self.dao.testSet_u[user][item2]-self.itemMeans[item2])/((len(self.dao.testSet_i[item2]))**2)
                SUM += abs(self.dao.testSet_u[user][item2] - self.itemMeans[item2])
            self.FMD[user] = SUM / len(self.dao.testSet_u[user])  # calculate FMD
            self.WDA[user] = Divisor1                                 #calculate WDA
            self.RDMA[user] = Divisor1/len(self.dao.testSet_u[user])  #calculate RDMA
            self.WDMA[user] = Divisor2/len(self.dao.testSet_u[user])  #calculate WDMA

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
                self.FMTD[user] = abs(Minuend / index1 - Subtrahend / index2) #calculate FMTD

            #calculate FMV
            self.Divisor3 = 0
            self.User_m_F  = deepcopy(self.dao.testSet_u[user])
            topValue = max(self.User_m_F.values())
            for item4 in self.dao.testSet_u[user]:
                if(self.User_m_F[item4]==topValue):
                    del self.User_m_F[item4]
            for item4_1 in self.User_m_F:
                self.Divisor3 += (self.User_m_F[item4_1] - self.itemMeans[item4_1])**2
            if len(self.User_m_F) ==0 :
                self.FMV[user] = 0
            else:
                self.FMV[user] =self.Divisor3/len(self.User_m_F)


            #calculate MeanVar
            self.Divisor4 = 0
            self.User_m_t = deepcopy(self.dao.testSet_u[user])
            for item5 in self.dao.testSet_u[user]:
                if (self.User_m_t[item5]==topValue):
                    del self.User_m_t[item5]
                    break
            for item5_1 in self.User_m_t:
                self.Divisor4 += (self.User_m_t[item5_1] - self.itemMeans[item5_1])**2
            if len(self.dao.testSet_u[user]) ==1:
                self.MeanVar[user] =0
            else:
                self.MeanVar[user]= self.Divisor4/(len(self.dao.testSet_u[user])-1)




         # preparing examples training for LabledData ,test for UnLableData


        self.training = []
        self.trainingLabels = []
        self.test = []
        self.testLabels = []


        self.featureWeight= [0,0,0,0,0,0,0,0,0,0]
        self.slectFeatureTrain = []
        self.slectFeatureTest = []

        for user in self.dao.trainingSet_u:
            self.training.append([self.Entropy[user], self.DegSim[user], self.LengthVar[user],self.RDMA[user],self.FMTD[user]
                                     ,self.WDMA[user],self.WDA[user],self.FMV[user],self.MeanVar[user],self.FMD[user]])
            self.trainingLabels.append(self.labels[user])

        for sampleTimes in range(0,500): #sample times = 500
            randUser = random.randint(0,len(self.dao.trainingSet_u)) # choose random user
            neiborUser = self.nearestUser[randUser]
            for i in range(0,10):
                self.featureWeight[i]=(self.featureWeight[i]+(self.training[randUser][i]-self.training[neiborUser][i])) #待改
        self.topFeature = []
        self.username =self.dao.id2user.values()
        self.userid = self.dao.id2user.keys()
        for user in self.dao.trainingSet_u:
            if user in self.username:
                userindexTrain=self.userid[self.username.index(user)]
            for i in range(0,5):
                self.topFeature.append(self.featureWeight.index(heapq.nlargest(5,self.featureWeight)[i]))
            self.slectFeatureTrain.append([self.training[userindexTrain][self.topFeature[0]],self.training[userindexTrain][self.topFeature[1]],self.training[userindexTrain][self.topFeature[2]],
                                      self.training[userindexTrain][self.topFeature[3]],self.training[userindexTrain][self.topFeature[4]]])


        for user in self.dao.testSet_u:
            self.test.append([self.Entropy[user], self.DegSim[user], self.LengthVar[user],self.RDMA[user],self.FMTD[user]
                                     ,self.WDMA[user],self.WDA[user],self.FMV[user],self.MeanVar[user],self.FMD[user]])
            self.testLabels.append(self.labels[user])
        self.userindex =0
        for user in self.dao.testSet_u:
            self.slectFeatureTest.append([self.test[i][self.topFeature[0]],self.test[i][self.topFeature[1]],self.test[i][self.topFeature[2]],
                                 self.test[i][self.topFeature[3]],self.test[i][self.topFeature[4]]])
            self.userindex+=1


    def predict(self):
            classifier = GaussianNB()
            classifier.fit(self.slectFeatureTrain ,self.trainingLabels)
            pred_labelsForTrainingUn = classifier.predict(self.slectFeatureTest)
            while 1 :
                p1 = pred_labelsForTrainingUn
                classifier.partial_fit(self.slectFeatureTest, pred_labelsForTrainingUn,classes=['0','1'], sample_weight=np.ones(len(self.slectFeatureTest),dtype=np.float)*self.Lambda)
                pred_labelsForTrainingUn = classifier.predict(self.slectFeatureTest)
                p2 = pred_labelsForTrainingUn
                if list(p1)==list(p2) :
                    break
            pred_labels = classifier.predict(self.slectFeatureTest)
            print 'naive_bayes:'
            print classification_report(self.testLabels, pred_labels, digits=4)
            return classification_report(self.testLabels, pred_labels, digits=4)
