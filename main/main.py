import sys
sys.path.append("..")
from SDLib import SDLib
from tool.config import Config


if __name__ == '__main__':

    print '='*80
    print '   SDLib: A Python library used to collect shilling detection methods.'
    print '='*80
    print '1. DegreeSAD     2. PCASelectUsers     3. SemiSAD     4. FAP     5. HySAD'
    print '-'*80
    algor = -1
    conf = -1
    order = input('please enter the num of the method to run it:')
    import time
    s = time.clock()
    # if order == 0:
    #     try:
    #         import seaborn as sns
    #     except ImportError:
    #         print '!!!To obtain nice data charts, ' \
    #               'we strongly recommend you to install the third-party package <seaborn>!!!'
    #     conf = Config('../config/visual/visual.conf')
    #     Display(conf).render()
    #     exit(0)
    if order == 1:
        conf = Config('../config/DegreeSAD.conf')
    elif order  == 2:
        conf = Config('../config/PCASelectUsers.conf')

    elif order == 3:
        conf = Config('../config/SemiSAD.conf')

    elif order == 4:
        conf = Config('../config/FAP.conf')

    elif order ==  5:
        conf = Config('../config/HySAD.conf')

    else:
        print 'Error num!'
        exit(-1)
    sd = SDLib(conf)
    sd.execute()
    e = time.clock()
    print "Run time: %f s" % (e - s)