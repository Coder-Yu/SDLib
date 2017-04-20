#coding:utf-8
#author:Yu Junliang
#Date: 2016-03-15
import random

import numpy as np
from attack import Attack


class AverageAttack(Attack):
    def __init__(self,conf):
        super(AverageAttack, self).__init__(conf)


    def insertSpam(self):
        print 'Modeling average attack...'
        itemList = self.itemProfile.keys()
        startUserID = len(self.userProfile)+1

        for i in range(int(len(self.userProfile)*self.attackSize)):
            #fill 装填项目
            fillerItems = self.getFillerItems()
            for item in fillerItems:
                self.spamProfile[str(startUserID)][str(itemList[item])] = round(self.itemAverage[str(itemList[item])])
            #target 目标项目
            for j in range(self.targetCount):
                target = np.random.randint(len(self.targetItems))
                self.spamProfile[str(startUserID)][self.targetItems[target]] = self.targetScore
                self.spamItem[str(startUserID)].append(self.targetItems[target])
            startUserID += 1






