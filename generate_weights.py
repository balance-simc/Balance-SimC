import requests
import time
import argparse
import json

post_url = 'https://www.raidbots.com/sim'
get_url = 'https://www.raidbots.com/api/job/'
report_url = 'https://www.raidbots.com/simbot/report/'

parser = argparse.ArgumentParser()
parser.add_argument('apikey', type=str, help='raidbots apikey')
parser.add_argument('-c', '--covenant', type=str, help='covenant string')
parser.add_argument('-s', '--soulbind', type=str, help='soulbind string')
parser.add_argument('-t', '--talent', type=str, help='talent code in #')
parser.add_argument('-l', '--legendary', type=str, help='legendary')
args = parser.parse_args()

profile = apl = dungeon = move = spread = ""
with open('sandbag.txt', 'r') as fp:
    profile = fp.read()
with open('balance.txt', 'r') as fp:
    apl = fp.read()

talents = [
    ['NB ', 'WOE', 'FON'],
    ['SOTF', 'SL  ', 'INC '],
    ['SD', 'TM', 'SF'],
    ['SOL', 'FOE', 'NM ']
]
legendaries = {
    'boat':'legs=,id=172318,bonus_id=7107/6716/6648/6649/1532',
    'dream':'finger2=,id=178926,bonus_id=7108/6716/7193/6648/6649/1532,gems=16mastery,enchant=tenet_of_haste',
    'oneth':'feet=,id=172315,bonus_id=7087/6716/6648/6649/1532',
    'pulsar':'hands=,id=172316,bonus_id=7088/6716/6648/6649/1532',
    #'lycaras':'feet=,id=172315,bonus_id=7110/6716/6648/6649/1532',
    #'draught':'neck=,id=178927,bonus_id=7086/6716/7193/6648/6649/1532,gems=16mastery',
    #'eonar':'waist=,id=172320,bonus_id=7100/6716/7194/6648/6649/1532,gems=16mastery',
    'circle':'finger2=,id=178926,bonus_id=7085/6716/7193/6648/6649/1532,gems=16mastery,enchant=tenet_of_haste'
}
covenants = ['kyrian', 'necrolord', 'night_fae', 'venthyr']

if args.legendary not in legendaries:
    raise parser.error("Valid --legendary are: " + ', '.join(legendaries.keys()))
if args.covenant not in covenants:
    raise parser.error("Valid --covenants are: " + ', '.join(covenants))
if len(args.talent) < 7:
    raise parser.error("Valid --talent must have 7 numbers")
try:
    for c in args.talent:
        i = int(c)
        if i < 0 or i > 3:
            raise Exception()
except:
    raise parser.error("Valid --talent must be numerical code between 0 and 3")

stats = ['haste', 'mastery', 'crit', 'versatility']

scale = 16
max_scale = 75

sets_list = []

for stat in stats:
    gear_str = 'gear_' + stat + '_rating='
    config_str = 'calculate_scale_factors=1\nsingle_actor_batch=1\ngear_haste_rating=0\ngear_mastery_rating=0\ngear_crit_rating=0\ngear_versatility_rating=0'
    scale_str = 'scale_' + stat + '_rating=' + str(scale)
    only_str = 'scale_only=' + stat
    if stat == 'haste':
        iter_str = 'iterations=100000'
    else:
        iter_str = 'iterations=50000'

    for i in range(max_scale):



