#coding:utf-8
from collections import defaultdict

from baseclass.attack import Attack

from dataio import loadTrusts


class RelationAttack(Attack):
    def __init__(self):
        super(RelationAttack, self).__init__()
        self.spamLink = defaultdict(list)
        self.trustLink,self.trusteeLink = loadTrusts(self.config['social'])
        self.activeUser = {}  # 关注了虚假用户的正常用户
        self.linkedUser = {}  # 被虚假用户种植过链接的用户

    def reload(self):
        super(RelationAttack, self).reload()
        self.spamLink = defaultdict(list)
        self.trustLink, self.trusteeLink = loadTrusts(self.config['social'])
        self.activeUser = {}  # 关注了虚假用户的正常用户
        self.linkedUser = {}  # 被虚假用户种植过链接的用户

    def farmLink(self,scale=0.5):
        pass

    def getReciprocal(self,target):
        reciprocal = float(2 * len(set(self.trustLink[target]).intersection(self.trusteeLink[target])) + 0.1) \
                     / (len(set(self.trustLink[target]).union(self.trusteeLink[target])) + 1)
        reciprocal += (len(self.trustLink[target]) + 0.1) / (len(self.trustLink[target]) + len(self.trusteeLink[target]) + 1)
        reciprocal /= 2
        return reciprocal