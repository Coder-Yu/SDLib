from data.rating import Rating
from tool.config import Config,LineConfig
from os.path import abspath
from time import strftime,localtime,time
from tool.file import FileIO
from sklearn.metrics import classification_report
class Detector(object):

    def __init__(self,conf,trainingSet=None,testSet=None,labels=None,fold='[1]'):
        self.config = conf
        self.isSave = False
        self.isLoad = False
        self.foldInfo = fold
        self.labels = labels
        self.data = Rating(self.config, trainingSet, testSet)
        self.training = []
        self.trainingLabels = []
        self.test = []
        self.testLabels = []

    def readConfiguration(self):
        self.algorName = self.config['methodName']
        self.output = LineConfig(self.config['output.setup'])


    def printAlgorConfig(self):
        "show algorithm's configuration"
        print 'Algorithm:',self.config['methodName']
        print 'Ratings dataSet:',abspath(self.config['ratings'])
        if LineConfig(self.config['evaluation.setup']).contains('-testSet'):
            print 'Test set:',abspath(LineConfig(self.config['evaluation.setup']).getOption('-testSet'))
        #print 'Count of the users in training set: ',len()
        print 'Training set size: (user count: %d, item count %d, record count: %d)' %(self.dao.trainingSize())
        print 'Test set size: (user count: %d, item count %d, record count: %d)' %(self.dao.testSize())
        print '='*80

    def initModel(self):
        pass

    def buildModel(self):
        pass

    def saveModel(self):
        pass

    def loadModel(self):
        pass

    def predict(self):
        pass

    def execute(self):
        self.readConfiguration()
        if self.foldInfo == '[1]':
            self.printAlgorConfig()
        # load model from disk or build model
        if self.isLoad:
            print 'Loading model %s...' % (self.foldInfo)
            self.loadModel()
        else:
            print 'Initializing model %s...' % (self.foldInfo)
            self.initModel()
            print 'Building Model %s...' % (self.foldInfo)
            self.buildModel()

        # preict the ratings or item ranking
        print 'Predicting %s...' % (self.foldInfo)
        prediction = self.predict()
        report = classification_report(self.testLabels, prediction, digits=4)
        currentTime = strftime("%Y-%m-%d %H-%M-%S", localtime(time()))
        FileIO.writeFile(self.output['-dir'],self.algorName+'@'+currentTime+self.foldInfo,report)
        # save model
        if self.isSave:
            print 'Saving model %s...' % (self.foldInfo)
            self.saveModel()
        print report
        return report