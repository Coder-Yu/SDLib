#coding:utf-8
import numpy as np
import random
from relationAttack import RelationAttack

class RandomRelationAttack(RelationAttack):
    def __init__(self,conf):
        super(RandomRelationAttack, self).__init__(conf)
        self.scale = float(self.config['linkSize'])

    def farmLink(self):  # 随机注入虚假关系

        for spam in self.spamProfile:

            #对购买了目标项目的用户种植链接
            for item in self.spamItem[spam]:
                if random.random() < 0.01:
                    for target in self.itemProfile[item]:
                        self.spamLink[spam].append(target)
                        response = np.random.random()
                        reciprocal = self.getReciprocal(target)
                        if response <= reciprocal:
                            self.trustLink[target].append(spam)
                            self.activeUser[target] = 1
                        else:
                            self.linkedUser[target] = 1
            #对其它用户以scale的比例种植链接
            for user in self.userProfile:
                if random.random() < self.scale:
                    self.spamLink[spam].append(user)
                    response = np.random.random()
                    reciprocal = self.getReciprocal(user)
                    if response < reciprocal:
                        self.trustLink[user].append(spam)
                        self.activeUser[user] = 1
                    else:
                        self.linkedUser[user] = 1