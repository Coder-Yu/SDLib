#coding:utf8
import random

import numpy as np

from randomRelationAttack import RandomRelationAttack
from bandwagonAttack import BandWagonAttack
from os.path import abspath
#
# 随机关系流行攻击
#
class RB_Attack(RandomRelationAttack,BandWagonAttack):
    def __init__(self,conf):
        super(RB_Attack, self).__init__(conf)




