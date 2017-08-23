#coding:utf8
import random

import numpy as np

from randomRelationAttack import RandomRelationAttack
from averageAttack import AverageAttack
from os.path import abspath
#
# 随机关系平均攻击
#
class RA_Attack(RandomRelationAttack,AverageAttack):
    def __init__(self,conf):
        super(RA_Attack, self).__init__(conf)




