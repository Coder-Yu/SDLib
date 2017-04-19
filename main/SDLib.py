import sys
from re import split
from tool.config import Config,LineConfig
from tool.file import FileIO
from tool.dataSplit import *
from multiprocessing import Process,Manager
from tool.file import FileIO
from time import strftime,localtime,time
class SDLib(object):
    def __init__(self,config):
        self.trainingData = []  # training data
        self.testData = []  # testData
        self.relation = []
        self.measure = []
        self.config =config
        self.ratingConfig = LineConfig(config['ratings.setup'])
        self.labels = FileIO.loadLabels(config['label'])

        if self.config.contains('evaluation.setup'):
            self.evaluation = LineConfig(config['evaluation.setup'])
            
            if self.evaluation.contains('-testSet'):
                #specify testSet
                self.trainingData = FileIO.loadDataSet(config, config['ratings'])
                self.testData = FileIO.loadDataSet(config, self.evaluation['-testSet'], bTest=True)

            elif self.evaluation.contains('-ap'):
                #auto partition
                self.trainingData = FileIO.loadDataSet(config,config['ratings'])
                self.trainingData,self.testData = DataSplit.\
                    dataSplit(self.trainingData,test_ratio=float(self.evaluation['-ap']))

            elif self.evaluation.contains('-cv'):
                #cross validation
                self.trainingData = FileIO.loadDataSet(config, config['ratings'])
                #self.trainingData,self.testData = DataSplit.crossValidation(self.trainingData,int(self.evaluation['-cv']))

        else:
            print 'Evaluation is not well configured!'
            exit(-1)

        if config.contains('social'):
            self.socialConfig = LineConfig(self.config['social.setup'])
            self.relation = FileIO.loadRelationship(config,self.config['social'])

        print 'preprocessing...'






    def execute(self):
        #import the algorithm module
        importStr = 'from method.' + self.config['methodName'] + ' import ' + self.config['methodName']
        exec (importStr)
        if self.evaluation.contains('-cv'):
            k = int(self.evaluation['-cv'])
            if k <= 1 or k > 10:
                k = 3
            #create the manager used to communication in multiprocess
            manager = Manager()
            m = manager.dict()
            i = 1
            tasks = []            

            for train,test in DataSplit.crossValidation(self.trainingData,k):
                fold = '['+str(i)+']'
                if self.config.contains('social'):
                    method = self.config['methodName'] + "(self.config,train,test,self.labels,self.relation,fold)"
                else:
                    method = self.config['methodName']+ "(self.config,train,test,self.labels,fold)"
               #create the process
                p = Process(target=run,args=(m,eval(method),i))
                tasks.append(p)
                i+=1
            #start the processes
            for p in tasks:
                p.start()
            #wait until all processes are completed
            for p in tasks:
                p.join()
            #compute the mean error of k-fold cross validation
            # self.measure = [dict(m)[i] for i in range(1,k+1)]
            # res = []
            # for i in range(len(self.measure[0])):
            #     measure = self.measure[0][i].split(':')[0]
            #     total = 0
            #     for j in range(k):
            #         total += float(self.measure[j][i].split(':')[1])
            #     res.append(measure+':'+str(total/k)+'\n')
            #output result
            # currentTime = strftime("%Y-%m-%d %H-%M-%S", localtime(time()))
            # outDir = LineConfig(self.config['output.setup'])['-dir']
            # fileName = self.config['methodName'] +'@'+currentTime+'-'+str(k)+'-fold-cv' + '.txt'
            # FileIO.writeFile(outDir,fileName,res)


        else:
            if self.config.contains('social'):
                method = self.config['methodName']+'(self.config,self.trainingData,self.testData,self,labels,self.relation)'
            else:
                method = self.config['methodName'] + '(self.config,self.trainingData,self.testData,self.labels)'
            eval(method).execute()


def run(measure,algor,order):
    measure[order] = algor.execute()