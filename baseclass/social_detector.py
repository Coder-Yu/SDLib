from detector import Detector
from data.social import Social
from tool.config import Config,LineConfig
from os.path import abspath
from time import strftime,localtime,time
from tool.file import FileIO
from sklearn.metrics import classification_report
class SocialDetector(Detector):

    def __init__(self,conf,trainingSet=None,testSet=None,labels=None,relation=list(),fold='[1]'):
        super(Detector,self).__init__(conf,trainingSet,testSet,labels,fold)
        self.social = Social(self.config, relation)  # social relations access control
