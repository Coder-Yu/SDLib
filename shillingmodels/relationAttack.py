#coding:utf-8
from collections import defaultdict

from attack import Attack
from tool.file import FileIO
from os.path import abspath


#注意！关系攻击模型默认为有向无权图
class RelationAttack(Attack):
    def __init__(self,conf):
        super(RelationAttack, self).__init__(conf)
        self.spamLink = defaultdict(list)
        self.relation = FileIO.loadRelationship(self.config,self.config['social'])
        self.trustLink = defaultdict(list)
        self.trusteeLink = defaultdict(list)
        for u1,u2,t in self.relation:
            self.trustLink[u1].append(u2)
            self.trusteeLink[u2].append(u1)
        self.activeUser = {}  # 关注了虚假用户的正常用户
        self.linkedUser = {}  # 被虚假用户种植过链接的用户

    # def reload(self):
    #     super(RelationAttack, self).reload()
    #     self.spamLink = defaultdict(list)
    #     self.trustLink, self.trusteeLink = loadTrusts(self.config['social'])
    #     self.activeUser = {}  # 关注了虚假用户的正常用户
    #     self.linkedUser = {}  # 被虚假用户种植过链接的用户

    def farmLink(self):
        pass

    def getReciprocal(self,target):
        #当前目标用户关注spammer的概率，依赖于粉丝数和关注数的交集
        reciprocal = float(2 * len(set(self.trustLink[target]).intersection(self.trusteeLink[target])) + 0.1) \
                     / (len(set(self.trustLink[target]).union(self.trusteeLink[target])) + 1)
        reciprocal += (len(self.trustLink[target]) + 0.1) / (len(self.trustLink[target]) + len(self.trusteeLink[target]) + 1)
        reciprocal /= 2
        return reciprocal

    def generateSocialConnections(self,filename):
        relations = []
        path = self.outputDir + filename
        with open(path, 'w') as f:
            for u1 in self.trustLink:
                for u2 in self.trustLink[u1]:
                    relations.append(u1 + ' ' + u2 + ' 1\n')

            for u1 in self.spamLink:
                for u2 in self.spamLink[u1]:
                    relations.append(u1 + ' ' + u2 + ' 1\n')
            f.writelines(relations)
        print 'Social relations have been output to ' + abspath(self.config['outputDir']) + '.'