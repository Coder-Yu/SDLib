from SDetection import SDetection
from data.social import SocialDAO
from tool.config import Config,LineConfig
from os.path import abspath
from time import strftime,localtime,time
from tool.file import FileIO
from sklearn.metrics import classification_report
class SSDetection(SDetection):

    def __init__(self,conf,trainingSet=None,testSet=None,labels=None,relation=list(),fold='[1]'):
        super(SSDetection, self).__init__(conf,trainingSet,testSet,labels,fold)
        self.sao = SocialDAO(self.config, relation)  # social relations access control
