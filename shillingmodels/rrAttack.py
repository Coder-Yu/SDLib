#coding:utf8
import random

import numpy as np

from randomRelationAttack import RandomRelationAttack
from randomAttack import RandomAttack
from os.path import abspath
#
# 双随机攻击
#
class RRAttack(RandomRelationAttack,RandomAttack):
    def __init__(self,conf):
        super(RRAttack, self).__init__(conf)



