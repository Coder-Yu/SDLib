from baseclass.SDetection import SDetection
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
# from random import shuffle
from sklearn.metrics import classification_report
from sklearn.tree import DecisionTreeClassifier


class CUE(SDetection):
    def __init__(self, conf, trainingSet=None, testSet=None, labels=None, fold='[1]'):
        super(CUE, self).__init__(conf, trainingSet, testSet, labels, fold)

    def buildModel(self):
        self.MUD = {}
        self.RUD = {}
        self.QUD = {}
        # computing MUD,RUD,QUD for training set
        sList = sorted(self.dao.trainingSet_i.iteritems(), key=lambda d: len(d[1]), reverse=True)
        maxLength = len(sList[0][1])
        for user in self.dao.trainingSet_u:
            self.MUD[user] = 0
            for item in self.dao.trainingSet_u[user]:
                self.MUD[user] += len(self.dao.trainingSet_i[item])# / float(maxLength)
            self.MUD[user]/float(len(self.dao.trainingSet_u[user]))
            lengthList = [len(self.dao.trainingSet_i[item]) for item in self.dao.trainingSet_u[user]]
            lengthList.sort(reverse=True)
            self.RUD[user] = lengthList[0] - lengthList[-1]

            lengthList = [len(self.dao.trainingSet_i[item]) for item in self.dao.trainingSet_u[user]]
            lengthList.sort()
            self.QUD[user] = lengthList[int((len(lengthList) - 1) / 4.0)]

        # computing MUD,RUD,QUD for test set
        for user in self.dao.testSet_u:
            self.MUD[user] = 0
            for item in self.dao.testSet_u[user]:
                self.MUD[user] += len(self.dao.trainingSet_i[item]) / float(maxLength)
        for user in self.dao.testSet_u:
            lengthList = [len(self.dao.trainingSet_i[item]) for item in self.dao.testSet_u[user]]
            lengthList.sort(reverse=True)
            self.RUD[user] = lengthList[0] - lengthList[-1]
        for user in self.dao.testSet_u:
            lengthList = [len(self.dao.trainingSet_i[item]) for item in self.dao.testSet_u[user]]
            lengthList.sort()
            self.QUD[user] = lengthList[int((len(lengthList) - 1) / 4.0)]

        # preparing examples
        self.training = []
        self.trainingLabels = []
        self.test = []
        self.testLabels = []

        for user in self.dao.trainingSet_u:
            self.training.append([self.MUD[user], self.RUD[user], self.QUD[user]])
            self.trainingLabels.append(self.labels[user])

        for user in self.dao.testSet_u:
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
        print classification_report(self.testLabels, pred_labels,digits=4)
        return classification_report(self.testLabels, pred_labels,digits=4)