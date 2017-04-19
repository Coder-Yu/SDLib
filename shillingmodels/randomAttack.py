#coding:utf-8
#author:Yu Junliang
import random

import numpy as np
from attack import Attack

class RandomAttack(Attack):
    def __init__(self,conf):
        super(RandomAttack, self).__init__(conf)


    def insertSpam(self):
        print 'Modeling random attack...'
        itemList = self.itemProfile.keys()
        userList = self.userProfile.keys()
        startUserID = len(self.userProfile)+1

        for i in range(int(len(self.userProfile)*self.attackSize)):
            #fill 装填项目
            fillerItems = self.getFillerItems()
            for item in fillerItems:
                self.spamProfile[str(startUserID)][str(itemList[item])] = random.randint(1,6)

            #target 目标项目
            for j in range(self.targetCount):
                target = np.random.randint(len(self.targetItems))
                self.spamProfile[str(startUserID)][self.targetItems[target]] = self.targetScore
                self.spamItem[str(startUserID)].append(self.targetItems[target])
            startUserID += 1
