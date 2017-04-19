from collections import defaultdict
import numpy as np
from tool.config import Config
from tool.file import FileIO

class Attack(object):
    def __init__(self):
        self.config = Config('config.conf')
        self.userProfile = FileIO.loadDataSet(self.config,self.config['ratings'])
        self.itemProfile = defaultdict(dict)
        for user in self.userProfile:
            for item in self.userProfile[user]:
                self.itemProfile[item][user] = self.userProfile[user][item]
        self.spamProfile = defaultdict(dict)
        self.spamItem = defaultdict(list) #items rated by spammers
        self.targetItems = []
        self.itemAverage = {}
        self.getAverageRating()

    # def selectTarget(count = 20):
    #     pass
    # def reload(self):
    #     self.userProfile, self.itemProfile = loadRatings(self.config['ratings'])
    #     self.spamProfile = defaultdict(dict)
    #     self.spamItem = defaultdict(list)




    def getAverageRating(self):
        for itemID in self.itemProfile:
            li = self.itemProfile[itemID].values()
            self.itemAverage[itemID] = float(sum(li)) / len(li)


    def selectTarget(self,count=20,threshold=3.0):
        itemList = self.itemProfile.keys()
        itemList.sort()
        while len(self.targetItems) < count:
            target = np.random.randint(len(itemList)) #generate a target order at random
            if len(self.targetItems) < float(count):
                if len(self.itemProfile[str(itemList[target])]) < 30 and len(self.itemProfile[str(itemList[target])]) > 10 \
                        and str(itemList[target]) not in self.targetItems \
                        and self.itemAverage[str(itemList[target])] <= threshold:
                    self.targetItems.append(str(itemList[target]))
                    print len(self.itemProfile[str(itemList[target])]), self.itemAverage[str(itemList[target])], str(itemList[target])



    def loadTarget(self,filename):
        with open(filename) as f:
            for line in f:
                self.targetItems.append(line.strip())

    def generateLabels(self,filename):
        labels = []
        with open(filename,'w') as f:
            for user in self.spamProfile:
