#coding:utf-8
#author:Yu Junliang
#Date: 2017-09-03
import random

import numpy as np
from attack import Attack
from averageAttack import AverageAttack
from bandwagonAttack import BandWagonAttack
from randomAttack import RandomAttack
from os.path import abspath
class HybridAttack(Attack):
    def __init__(self,conf):
        super(HybridAttack, self).__init__(conf)
        self.aveAttack = AverageAttack(conf)
        self.bandAttack = BandWagonAttack(conf)
        self.randAttack = RandomAttack(conf)


    def insertSpam(self,startID=0):
        self.aveAttack.insertSpam()
        self.bandAttack.insertSpam(self.aveAttack.startUserID+1)
        self.randAttack.insertSpam(self.bandAttack.startUserID+1)
        self.spamProfile = {}
        self.spamProfile.update(self.aveAttack.spamProfile)
        self.spamProfile.update(self.bandAttack.spamProfile)
        self.spamProfile.update(self.randAttack.spamProfile)

    def generateProfiles(self,filename):

        ratings = []
        path = self.outputDir + filename
        with open(path, 'w') as f:
            for user in self.userProfile:
                for item in self.userProfile[user]:
                    ratings.append(user + ' ' + item + ' ' + str(self.userProfile[user][item]) + '\n')

            for user in self.spamProfile:
                for item in self.spamProfile[user]:
                    ratings.append(user + ' ' + item + ' ' + str(self.spamProfile[user][item]) + '\n')
            f.writelines(ratings)
        print 'User labels have been output to ' + abspath(self.config['outputDir']) + '.'

    def generateLabels(self,filename):
        labels = []
        path = self.outputDir + filename
        with open(path,'w') as f:
            for user in self.spamProfile:
                labels.append(user+' 1\n')
            for user in self.userProfile:
                labels.append(user+' 0\n')
            f.writelines(labels)
        print 'User profiles have been output to '+abspath(self.config['outputDir'])+'.'







