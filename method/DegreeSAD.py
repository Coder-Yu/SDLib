from baseclass.detector import Detector
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
# from random import shuffle

from sklearn.tree import DecisionTreeClassifier


class DegreeSAD(Detector):
    def __init__(self, conf, trainingSet=None, testSet=None, labels=None, fold='[1]'):
        super(DegreeSAD, self).__init__(conf, trainingSet, testSet, labels, fold)

    def buildModel(self):
        self.MUD = {}
        self.RUD = {}
        self.QUD = {}
        # computing MUD,RUD,QUD for training set
        sList = sorted(self.data.trainingSet_i.iteritems(), key=lambda d: len(d[1]), reverse=True)
        maxLength = len(sList[0][1])
        for user in self.data.trainingSet_u:
            self.MUD[user] = 0
            for item in self.data.trainingSet_u[user]:
                self.MUD[user] += len(self.data.trainingSet_i[item]) #/ float(maxLength)
            self.MUD[user]/float(len(self.data.trainingSet_u[user]))
            lengthList = [len(self.data.trainingSet_i[item]) for item in self.data.trainingSet_u[user]]
            lengthList.sort(reverse=True)
            self.RUD[user] = lengthList[0] - lengthList[-1]

            lengthList = [len(self.data.trainingSet_i[item]) for item in self.data.trainingSet_u[user]]
            lengthList.sort()
            self.QUD[user] = lengthList[int((len(lengthList) - 1) / 4.0)]

        # computing MUD,RUD,QUD for test set
        for user in self.data.testSet_u:
            self.MUD[user] = 0
            for item in self.data.testSet_u[user]:
                self.MUD[user] += len(self.data.trainingSet_i[item]) #/ float(maxLength)
        for user in self.data.testSet_u:
            lengthList = [len(self.data.trainingSet_i[item]) for item in self.data.testSet_u[user]]
            lengthList.sort(reverse=True)
            self.RUD[user] = lengthList[0] - lengthList[-1]
        for user in self.data.testSet_u:
            lengthList = [len(self.data.trainingSet_i[item]) for item in self.data.testSet_u[user]]
            lengthList.sort()
            self.QUD[user] = lengthList[int((len(lengthList) - 1) / 4.0)]

        # preparing examples

        for user in self.data.trainingSet_u:
            self.training.append([self.MUD[user], self.RUD[user], self.QUD[user]])
            self.trainingLabels.append(self.labels[user])

        for user in self.data.testSet_u:
            self.test.append([self.MUD[user], self.RUD[user], self.QUD[user]])
            self.testLabels.append(self.labels[user])

    def predict(self):
        # classifier = LogisticRegression()
        # classifier.fit(self.training, self.trainingLabels)
        # pred_labels = classifier.predict(self.test)
        # print 'Logistic:'
        # print classification_report(self.testLabels, pred_labels)
        #
        # classifier = SVC()
        # classifier.fit(self.training, self.trainingLabels)
        # pred_labels = classifier.predict(self.test)
        # print 'SVM:'
        # print classification_report(self.testLabels, pred_labels)

        classifier = DecisionTreeClassifier(criterion='entropy')
        classifier.fit(self.training, self.trainingLabels)
        pred_labels = classifier.predict(self.test)
        print 'Decision Tree:'
        return pred_labels