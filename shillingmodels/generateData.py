from averageAttack import AverageAttack
from bandwagonAttack import BandWagonAttack
from randomAttack import RandomAttack
from rrAttack import RRAttack

attack = RRAttack('./config/config.conf')
attack.insertSpam()
attack.farmLink()
attack.generateLabels('labels.txt')
attack.generateProfiles('profiles.txt')
attack.generateSocialConnections('relations.txt')