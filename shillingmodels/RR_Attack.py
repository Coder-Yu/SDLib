#coding:utf8
import random

import numpy as np

from randomRelationAttack import RandomRelationAttack
from randomAttack import RandomAttack
from os.path import abspath
#
# 双随机攻击
#
class RR_Attack(RandomRelationAttack,RandomAttack):
    def __init__(self,conf):
        super(RR_Attack, self).__init__(conf)




