import numpy as np
#from structure import sparseMatrix,new_sparseMatrix
from tool.config import Config,LineConfig
from tool.qmath import normalize
from tool.dataSplit import DataSplit
import os.path
from re import split
from collections import defaultdict

class RatingDAO(object):
    'data access control'
    def __init__(self,config, trainingData, testData):
        self.config = config
        self.ratingConfig = LineConfig(config['ratings.setup'])
        self.user = {} #used to store the order of users in the training set
        self.item = {} #used to store the order of items in the training set
        self.id2user = {}
        self.id2item = {}
        self.all_Item = {}
        self.all_User = {}
        self.userMeans = {} #used to store the mean values of users's ratings
        self.itemMeans = {} #used to store the mean values of items's ratings


        self.globalMean = 0
        self.timestamp = {}
        # self.trainingMatrix = None
        # self.validationMatrix = None
        self.testSet_u = testData.copy() # used to store the test set by hierarchy user:[item,rating]
        self.testSet_i = defaultdict(dict) # used to store the test set by hierarchy item:[user,rating]
        self.trainingSet_u = trainingData.copy()
        self.trainingSet_i = defaultdict(dict)
        #self.rScale = []

        self.trainingData = trainingData
        self.testData = testData
        self.__generateSet()
        self.__computeItemMean()
        self.__computeUserMean()
        self.__globalAverage()



    def __generateSet(self):
        scale = set()
        # find the maximum rating and minimum value
        # for i, entry in enumerate(self.trainingData):
        #     userName, itemName, rating = entry
        #     scale.add(float(rating))
        # self.rScale = list(scale)
        # self.rScale.sort()

        for i,user in enumerate(self.trainingData):
            for item in self.trainingData[user]:

                # makes the rating within the range [0, 1].
                #rating = normalize(float(rating), self.rScale[-1], self.rScale[0])
                #self.trainingSet_u[userName][itemName] = float(rating)
                self.trainingSet_i[item][user] = self.trainingData[user][item]
                # order the user
                if not self.user.has_key(user):
                    self.user[user] = len(self.user)
                    self.id2user[self.user[user]] = user
                # order the item
                if not self.item.has_key(item):
                    self.item[item] = len(self.item)
                    self.id2item[self.item[item]] = item

                # userList.append
        #     triple.append([self.user[userName], self.item[itemName], rating])
        # self.trainingMatrix = new_sparseMatrix.SparseMatrix(triple)

        self.all_User.update(self.user)
        self.all_Item.update(self.item)
        for i, user in enumerate(self.testData):
            for item in self.testData[user]:
                # order the user
                if not self.user.has_key(user):
                    self.all_User[user] = len(self.all_User)
                # order the item
                if not self.item.has_key(item):
                    self.all_Item[item] = len(self.all_Item)
                #self.testSet_u[userName][itemName] = float(rating)
                self.testSet_i[item][user] = self.testData[user][item]


    def __globalAverage(self):
        total = sum(self.userMeans.values())
        if total==0:
            self.globalMean = 0
        else:
            self.globalMean = total/len(self.userMeans)

    def __computeUserMean(self):
        # for u in self.user:
        #     n = self.row(u) > 0
        #     mean = 0
        #
        #     if not self.containsUser(u):  # no data about current user in training set
        #         pass
        #     else:
        #         sum = float(self.row(u)[0].sum())
        #         try:
        #             mean =  sum/ n[0].sum()
        #         except ZeroDivisionError:
        #             mean = 0
        #     self.userMeans[u] = mean
        for u in self.trainingSet_u:
            self.userMeans[u] = sum(self.trainingSet_u[u].values())/(len(self.trainingSet_u[u].values())+0.0)

    def __computeItemMean(self):
        # for c in self.item:
        #     n = self.col(c) > 0
        #     mean = 0
        #     if not self.containsItem(c):  # no data about current user in training set
        #         pass
        #     else:
        #         sum = float(self.col(c)[0].sum())
        #         try:
        #             mean = sum / n[0].sum()
        #         except ZeroDivisionError:
        #             mean = 0
        #     self.itemMeans[c] = mean
        for item in self.trainingSet_i:
            self.itemMeans[item] = sum(self.trainingSet_i[item].values())/(len(self.trainingSet_i[item].values()) + 0.0)

    def getUserId(self,u):
        if self.user.has_key(u):
            return self.user[u]
        else:
            return -1

    def getItemId(self,i):
        if self.item.has_key(i):
            return self.item[i]
        else:
            return -1

    def trainingSize(self):
        return (len(self.trainingSet_u),len(self.testSet_i),len(self.trainingData))

    def testSize(self):
        return (len(self.testSet_u),len(self.testSet_i),len(self.testData))

    def contains(self,u,i):
        'whether user u rated item i'
        if self.trainingSet_u.has_key(u) and self.trainingSet_u[u].has_key(i):
            return True
        return False

    def containsUser(self,u):
        'whether user is in training set'
        return self.trainingSet_u.has_key(u)

    def containsItem(self,i):
        'whether item is in training set'
        return self.trainingSet_i.has_key(i)

    # def userRated(self,u):
    #     if self.trainingMatrix.matrix_User.has_key(self.getUserId(u)):
    #         itemIndex =  self.trainingMatrix.matrix_User[self.user[u]].keys()
    #         rating = self.trainingMatrix.matrix_User[self.user[u]].values()
    #         return (itemIndex,rating)
    #     return ([],[])
    #
    # def itemRated(self,i):
    #     if self.trainingMatrix.matrix_Item.has_key(self.getItemId(i)):
    #         userIndex = self.trainingMatrix.matrix_Item[self.item[i]].keys()
    #         rating = self.trainingMatrix.matrix_Item[self.item[i]].values()
    #         return (userIndex,rating)
    #     return ([],[])

    # def row(self,u):
    #     return self.trainingMatrix.row(self.getUserId(u))
    #
    # def col(self,c):
    #     return self.trainingMatrix.col(self.getItemId(c))
    #
    # def sRow(self,u):
    #     return self.trainingMatrix.sRow(self.getUserId(u))
    #
    # def sCol(self,c):
    #     return self.trainingMatrix.sCol(self.getItemId(c))
    #
    # def rating(self,u,c):
    #     return self.trainingMatrix.elem(self.getUserId(u),self.getItemId(c))
    #
    # def ratingScale(self):
    #     return (self.rScale[0],self.rScale[1])

    # def elemCount(self):
    #     return self.trainingMatrix.elemCount()
