#coding:utf8
import random

import numpy as np

from relationAttack import RelationAttack


class RandomRelationAttack(RelationAttack):
    def __init__(self):
        super(RandomRelationAttack, self).__init__()

    def farmLink(self,scale=0.5):  # 随机注入虚假关系

        for spam in self.spamProfile:


            for item in self.spamItem[spam]:
                for target in self.itemProfile[item]:
                    self.spamLink[spam].append(target)
                    response = np.random.random()
                    reciprocal = self.getReciprocal(target)
                    if response <= reciprocal:
                        self.trustLink[target].append(spam)
                        self.activeUser[target] = 1
                    else:
                        self.linkedUser[target] = 1

            for user in self.userProfile:
                if random.random() < scale:
                    self.spamLink[spam].append(user)
                    response = np.random.random()
                    reciprocal = self.getReciprocal(user)
                    if response < reciprocal:
                        self.trustLink[user].append(spam)
                        self.activeUser[user] = 1
                    else:
                        self.linkedUser[user] = 1


