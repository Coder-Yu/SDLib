from random import random
from tool.file import FileIO
class DataSplit(object):

    def __init__(self):
        pass

    @staticmethod
    def dataSplit(data,test_ratio = 0.3,output=False,path='./',order=1):
        if test_ratio>=1 or test_ratio <=0:
            test_ratio = 0.3
        testSet = {}
        trainingSet = {}
        for user in data:
            if random() < test_ratio:
                testSet[user] = data[user].copy()
            else:
                trainingSet[user] = data[user].copy()

        if output:
            FileIO.writeFile(path,'testSet['+str(order)+']',testSet)
            FileIO.writeFile(path, 'trainingSet[' + str(order) + ']', trainingSet)
        return trainingSet,testSet

    @staticmethod
    def crossValidation(data,k,output=False,path='./',order=1):
        if k<=1 or k>10:
            k=3
        for i in range(k):
            trainingSet = {}
            testSet = {}
            for ind,user in enumerate(data):
                if ind%k == i:
                    testSet[user] = data[user].copy()
                else:
                    trainingSet[user] = data[user].copy()
            yield trainingSet,testSet


