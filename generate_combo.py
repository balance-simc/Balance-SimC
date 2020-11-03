import requests
import time
import argparse
import json

post_url = 'https://www.raidbots.com/sim'
get_url = 'https://www.raidbots.com/api/job/'
report_url = 'https://www.raidbots.com/simbot/report/'

parser = argparse.ArgumentParser()
parser.add_argument('apikey', type=str, help='raidbots apikey')
parser.add_argument('-t', '--targets', type=int, nargs='?', default=1, const=1, help='set desired sim targets')
parser.add_argument('-d', '--dungeon', default=False, action='store_true')
parser.add_argument('-m', '--move', default=False, action='store_true')
parser.add_argument('-s', '--spread', default=False, action='store_true')
args = parser.parse_args()
targets = str(max(1, args.targets))

profile = mplus = move = spread = ""
with open('sandbag.txt', 'r') as fp:
    profile = fp.read()
with open('dungeon.txt', 'r') as fp:
    dungeon = fp.read()
with open('move.txt', 'r') as fp:
    move = fp.read()
with open('spread.txt', 'r') as fp:
    spread = fp.read()

#talents = [ ['NB ', 'WOE', 'FON'], ['SOTF', 'SL  ', 'INC '], ['SD', 'TM', 'SF'], ['SOL', 'FOE', 'NM '] ]
talents = [ ['NB ', 'WOE'], ['SOTF', 'SL  '], ['SD', 'TM'], ['SOL', 'FOE'] ]
legendaries = {
    #'oneth':'7087',
    #'pulsar':'7088',
    #'dream':'7108',
    #'lycaras':'7110',
    #'boat':'7107',
    #'circle':'7085',
    'draught':'7086',
    'eonar':'7100'
}
conduits = [
    #'fury_of_the_skies:7',
    'umbral_intensity:7',
    'precise_alignment:7',
    'stellar_inspiration:7'
]
cov_conduit = {
    'kyrian':'deep_allegiance:7',
    'necrolord':'evolved_swarm:7',
    'night_fae':'conflux_of_elements:7',
    'venthyr':'endless_thirst:7'
}
covenants = {
    'kyrian':{
        'pelagos':{
            'base':'combat_meditation/let_go_of_the_past',
            'trait':[]
        },
        'kleia':{
            'base':'',
            'trait':['pointed_courage']
        },
        'mikanikos':{
            'base':'brons_call_to_action',
            'trait':['hammer_of_genesis']
        }
    },
    'necrolord':{
        'marileth':{
            'base':'',
            'trait':['plagueys_preemptive_strike']
        },
        'emeni':{
            'base':'lead_by_example',
            'trait':['gnashing_chompers']
        },
        'heirmir':{
            'base':'',
            'trait':['heirmirs_arsenal_marrowed_gemstone']
        }
    },
    'night_fae':{
        'niya':{
            'base':'grove_invigoration',
            'trait':['niyas_tools_burrs']
        },
        'dreamweaver':{
            'base':'field_of_blossoms',
            'trait':['social_butterfly']
        },
        'korayn':{
            'base':'wild_hunt_tactics',
            'trait':['first_strike']
        }
    },
    'venthyr':{
        'nadjia':{
            'base':'thrill_seeker',
            'trait':['exacting_preparation', 'dauntless_duelist']
        },
        'theotar':{
            'base':'soothing_shade',
            'trait':['refined_palate', 'wasteland_propriety']
        },
        'draven':{
            'base':'',
            'trait':['built_for_war']
        }
    }
}

#error_str = 'target_error=0.1'
error_str = ''

if args.dungeon:
    error_str = 'target_error=0.2'
    target_str = dungeon
elif args.spread:
    target_str = spread
else:
    target_str = 'desired_targets=' + targets

if args.move:
    target_str += '\n' + move

sets_list = []
for leg, bonus in legendaries.items():
    legendary_str = 'tabard=,id=31405,bonus_id=' + bonus

    for cov, soulbinds in covenants.items():
        covenant_str = 'covenant=' + cov

        for soul, traits in soulbinds.items():
            soulbind_list = []
            if traits['base']:
                soulbind_list.append(traits['base'])

            this_conduits = conduits.copy()
            this_conduits.append(cov_conduit[cov])
            for trait in traits['trait']:
                this_conduits.append(trait)

            for cond in this_conduits:
                this_soulbind_list = soulbind_list.copy()
                this_soulbind_list.append(cond)
                soulbind_str = 'soulbind+=' + '/'.join(this_soulbind_list)

                name = '-'.join([cov, soul, cond, leg])
                sets_list.append('profileset.' + name + '=' + legendary_str)
                sets_list.append('profileset.' + name + '+=' + covenant_str)
                sets_list.append('profileset.' + name + '+=' + soulbind_str)
sets_str = '\n'.join(sets_list)

buffer = []

for t15, talent15 in enumerate(talents[0], 1):
    for t40, talent40 in enumerate(talents[1], 1):
        for t45, talent45 in enumerate(talents[2], 1):
            for t50, talent50 in enumerate(talents[3], 1):
                talent = str(t15) + '000' + str(t40) + str(t45) + str(t50)
                talent_str = 'talents=' + str(t15) + '000' + str(t40) + str(t45) + str(t50)
                name_str = 'name=' + talent

                simc = '\n'.join([profile, talent_str, name_str, error_str, target_str, sets_str])

                while True:
                    time.sleep(3)
                    try:
                        post = requests.post(post_url, json={'type': 'advanced', 'apiKey': args.apikey, 'simcVersion': 'nightly', 'advancedInput': simc})
                        reply = post.json()
                        simID = reply['simId']
                        sim_url = report_url + simID
                        print(sim_url)
                        break
                    except:
                        continue

                while True:
                    time.sleep(3)
                    try:
                        get = requests.get(get_url + simID)
                        status = get.json()
                        if status['job']['state'] == 'complete':
                            data = requests.get(sim_url + '/data.json')
                            results = data.json()
                            if results['simbot']['hasFullJson']:
                                data = requests.get(sim_url + '/data.full.json')
                                results = data.json()
                            break
                        continue
                    except:
                        continue

                tal_key = results['sim']['players'][0]['name']

                for actor in results['sim']['profilesets']['results']:
                    cov_key, soul_key, cond_key, leg_key = actor['name'].split('-')
                    dps_key = actor['mean']

                    buffer.append({'cov':cov_key, 'leg':leg_key, 'soul':soul_key, 'cond':cond_key, 'tal':tal_key, 'dps':dps_key})

json_name = 'combo_'
if args.dungeon:
    json_name += 'D'
elif args.spread:
    json_name += 'S'
else:
    json_name += targets
    if args.move:
        json_name += 'M'

with open(json_name + '.json', 'w') as fp:
    fp.write(json.dumps(buffer).replace('},', '},\n'))
