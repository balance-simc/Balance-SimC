import requests
import time
import argparse
import json
import sys
from itertools import combinations

post_url = 'https://www.raidbots.com/sim'
get_url = 'https://www.raidbots.com/api/job/'
report_url = 'https://www.raidbots.com/simbot/report/'

parser = argparse.ArgumentParser()
parser.add_argument('apikey', type=str, help='raidbots apikey')
parser.add_argument('-t', '--targets', type=int, nargs='?',
                    default=1, const=1, help='set desired sim targets')
parser.add_argument('-d', '--dungeon', default=False, action='store_true')
parser.add_argument('-m', '--move', default=False, action='store_true')
parser.add_argument('-s', '--spread', default=False, action='store_true')
args = parser.parse_args()
targets = str(max(1, args.targets))

profile_base = profile_nf = apl = dungeon = move = spread = ""
with open('sandbag_base.txt', 'r') as fp:
    profile_base = fp.read()
with open('sandbag_nf.txt', 'r') as fp:
    profile_nf = fp.read()
with open('balance.txt', 'r') as fp:
    apl = fp.read()
with open('composite.txt', 'r') as fp:
    dungeon = fp.read()
with open('move.txt', 'r') as fp:
    move = fp.read()
with open('spread.txt', 'r') as fp:
    spread = fp.read()

talents = [
    ['NB ', 'WOE', 'FON'],
    ['SOTF', 'SL  ', 'INC '],
    ['TM', 'SD', 'SF'],
    ['SOL', 'FOE', 'NM ']
]
legendaries = {
    'boat': 'legs=,id=172318,bonus_id=7107/6716/6648/6649/1532',
    'dream': 'finger2=,id=178926,bonus_id=7108/6716/7193/6648/6649/1532,gems=16mastery,enchant=tenet_of_haste',
    'oneth': 'back=,id=173242,bonus_id=6716/7087/6649/6648/1532',
    'pulsar': 'finger2=,id=178926,bonus_id=7088/6716/7193/6648/6649,gems=16mastery,enchant=tenet_of_haste',
    'lycaras':'waist=,id=172320,bonus_id=6716/7110/6649/6648/1532/,gems=16mastery',
    'draught': 'neck=,id=178927,bonus_id=7086/6716/7193/6648/6649/1532,gems=16mastery',
    'eonar':'waist=,id=172320,bonus_id=7100/6716/7194/6648/6649/1532,gems=16mastery',
    'circle': 'finger2=,id=178926,bonus_id=7085/6716/7193/6648/6649/1532,gems=16mastery,enchant=tenet_of_haste',
    'covenant': {
        'kyrian': 'neck=,id=178927,bonus_id=7477/6716/7193/6648/6649,gems=16mastery',
        'necrolord': 'wrist=,id=172321,bonus_id=7472/6716/6648/6649/1532,gems=16mastery',
        'night_fae': 'legs=,id=172318,bonus_id=7571/6716/6648/6649/1532',
        'venthyr': 'waist=,id=172320,bonus_id=7474/6716/7194/6648/6649/1532,gems=16mastery'
    }
}
conduits = [
    'fury_of_the_skies:9',
    'umbral_intensity:9',
    'precise_alignment:9',
    'stellar_inspiration:9'
]
cov_conduit = {
    'kyrian': 'deep_allegiance:9',
    'necrolord': 'evolved_swarm:9',
    'night_fae': 'conflux_of_elements:9',
    'venthyr': 'endless_thirst:9'
}
covenants = {
    'kyrian': {
        'pelagos': {
            # /newfound_resolve
            'base': 'combat_meditation/better_together',
            'trait': []
        },
        'kleia': {
            # light_the_path
            'base': '',
            'trait': ['pointed_courage']
        },
        'mikanikos': {
            # /effusive_anima_accelerator
            'base': 'brons_call_to_action/soulglow_spectrometer',
            'trait': ['hammer_of_genesis']
        }
    },
    'necrolord': {
        'marileth': {
            # kevins_oozeling
            'base': '',
            'trait': ['plagueys_preemptive_strike']
        },
        'emeni': {
            # /pustule_eruption
            'base': 'lead_by_example',
            'trait': ['gnashing_chompers']
        },
        'heirmir': {
            # /mnemonic_equipment
            'base': 'forgeborne_reveries/carvers_eye',
            'trait': ['heirmirs_arsenal_marrowed_gemstone']
        }
    },
    'night_fae': {
        'niya': {
            # /bonded_hearts
            'base': 'grove_invigoration',
            'trait': ['niyas_tools_burrs']
        },
        'dreamweaver': {
            # /dream_delver
            'base': 'field_of_blossoms',
            'trait': ['social_butterfly']
        },
        'korayn': {
            # /wild_hunt_strategem
            'base': 'wild_hunt_tactics',
            'trait': ['first_strike']
        }
    },
    'venthyr': {
        'nadjia': {
            # /fatal_flaw
            'base': 'thrill_seeker',
            'trait': ['exacting_preparation', 'dauntless_duelist']
        },
        'theotar': {
            # /party_favors
            'base': 'soothing_shade',
            'trait': ['refined_palate', 'wasteland_propriety']
        },
        'draven': {
            # /battlefield_presence
            'base': '',
            'trait': ['built_for_war']
        }
    }
}

if args.dungeon:
    target_str = dungeon
elif args.spread:
    target_str = spread
else:
    target_str = 'desired_targets=' + targets

if args.move:
    target_str += '\n' + move

buffer = []
for leg, leg_str in legendaries.items():
    # split for covenant legis
    if leg == 'covenant':
        leg_str = leg_str[cov]

    for cov, soulbinds in covenants.items():
        
        cov_str = 'covenant=' + cov

        profile = profile_base
        if cov == 'night_fae':
            profile=profile_nf

        for soul, traits in soulbinds.items():
            sets_list = []
            name_str = 'name=' + '-'.join([cov, leg, soul])
            soulbind_master = []
            if traits['base']:
                soulbind_master.append(traits['base'])
            conduits_master = conduits.copy()
            conduits_master.append(cov_conduit[cov])
            for t in traits['trait']:
                conduits_master.append(t)

            for combo in combinations(conduits_master, 3):
                cond1, cond2, cond3 = combo
                if all(set(traits['trait']) & set(subcombo) for subcombo in combinations([cond1, cond2, cond3], 2)):
                    continue

                soulbind_list = soulbind_master.copy()
                soulbind_list.append(cond1)
                soulbind_list.append(cond2)
                soulbind_list.append(cond3)
                soulbind_str = 'soulbind=' + '/'.join(soulbind_list)

                for t15, talent15 in enumerate(talents[0], 1):
                    for t40, talent40 in enumerate(talents[1], 1):
                        for t45, talent45 in enumerate(talents[2], 1):
                            for t50, talent50 in enumerate(talents[3], 1):
                                talent = str(t15) + '000' + \
                                    str(t40) + str(t45) + str(t50)
                                talent_str = 'talents=' + talent
                                profile_name = '\"' + \
                                    '-'.join([cond1, cond2,
                                              cond3, talent]) + '\"'
                                sets_list.append(
                                    'profileset.' + profile_name + '=' + talent_str)
                                sets_list.append(
                                    'profileset.' + profile_name + '+=' + soulbind_str)

            sets_str = '\n'.join(sets_list)

            simc = '\n'.join([profile, apl, leg_str, cov_str,
                                name_str, target_str, sets_str])

            while True:
                time.sleep(2)
                try:
                    post = requests.post(post_url, json={
                                        'type': 'advanced', 'apiKey': args.apikey, 'simcVersion': 'nightly','smartHighPrecision': False, 'advancedInput': simc})
                except:
                    continue
                if post.status_code==400:
                    sys.exit('Input Error')
                if post.status_code==401:
                    sys.exit('Invalid API key')
                if post.status_code>=500:
                    sys.exit('something went horribly wrong')
                if post.status_code==429:
                    print('Rate limited')
                    continue
                if post.status_code==200:
                    reply = post.json()
                    simID = reply['simId']
                    sim_url = report_url + simID
                    print(sim_url)
                    break
                sys.exit('Unknown error: '.format(post.status_code))
            while True:
                time.sleep(2)
                try:
                    get = requests.get(get_url + simID)
                except:
                    continue
                status = get.json()
                if 'message' in status and status['message'] == 'No job found':
                    sys.exit("The sim got lost :(")
                if status['job']['state'] == 'complete':
                    data = requests.get(sim_url + '/data.json')
                    results = data.json()
                    if 'error'in results:
                        sys.exit('Sim failed with error {}'.format(results['error']['type']))
                    if 'hasFullJson' in results['simbot'] and results['simbot']['hasFullJson']:
                        data = requests.get(sim_url + '/data.full.json')
                        results = data.json()
                    break

            cov_key, leg_key, soul_key = results['sim']['players'][0]['name'].split('-')

            for actor in results['sim']['profilesets']['results']:
                cond1_key, cond2_key, cond3_key, tal_key = actor['name'].split('-')
                dps_key = actor['mean']

                buffer.append({'cov': cov_key, 'leg': leg_key, 'soul': soul_key,
                                'cond1': cond1_key, 'cond2': cond2_key, 'cond3': cond3_key, 'tal': tal_key, 'dps': dps_key})

json_name = 'combo_'
if args.dungeon:
    json_name += 'd'
elif args.spread:
    json_name += 's'
else:
    json_name += targets
    if args.move:
        json_name += 'm'

with open(json_name + '.json', 'w') as fp:
    fp.write(json.dumps(buffer).replace('},', '},\n'))
