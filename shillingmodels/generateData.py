from averageAttack import AverageAttack
from bandwagonAttack import BandWagonAttack
from randomAttack import RandomAttack

attack = AverageAttack('./config/config.conf')
attack.insertSpam()
attack.generateLabels('labels.txt')
attack.generateProfiles('profiles.txt')