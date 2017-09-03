from averageAttack import AverageAttack
from bandwagonAttack import BandWagonAttack
from randomAttack import RandomAttack
from RR_Attack import RR_Attack
from hybridAttack import HybridAttack

attack = HybridAttack('./config/config.conf')
attack.insertSpam()
#attack.farmLink()
attack.generateLabels('labels.txt')
attack.generateProfiles('profiles.txt')
#attack.generateSocialConnections('relations.txt')