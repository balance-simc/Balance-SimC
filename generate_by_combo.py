import requests
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('apikey', type=str, help='raidbots apikey')
parser.add_argument('-t', '--targets', type=int, nargs='?', default=1, const=1, help='set desired sim targets')
parser.add_argument('--spread', type=bool, nargs='?', default=False, help='add a target 15yd away')
args = parser.parse_args()
apikey = args.apikey
targets = str(args.targets)
spread_add = args.spread

post_url = 'https://mimiron.raidbots.com/sim'
get_url = 'https://mimiron.raidbots.com/api/job/'
report_url = 'https://mimiron.raidbots.com/simbot/report/'

profile = sets = mplus = move = spread = ""

covs = []
legs = {}

with open('leg_x_cov.txt', 'r') as fp:
    while line_ := fp.readline():
        if line_[0] == '#':
            continue
        split_ = line_.split('=')
        if split_[0] == 'covenant':
            covs.append(split_[1].strip('\"\n'))
            continue
        if line_ == '\n':
            line_1 = fp.readline()
            if line_1[0] == '#':
                continue
            key_ = line_1.split(',')[0].split('-')[-1]
            line_2 = fp.readline()
            if line_2[0] == '#':
                continue
            value_ = line_2.split('=')[-1]
            legs[key_] = int(value_)
            continue

with open('sandbag.txt', 'r') as fp:
    profile = fp.read()

with open('talent_profiles.txt', 'r') as fp:
    sets = fp.read()

with open('dungeon.txt', 'r') as fp:
    mplus = fp.read()

with open('move.txt', 'r') as fp:
    move = fp.read()

with open('spread.txt', 'r') as fp:
    spread = fp.read()

buffer = {}

for cov in covs:
    for leg, bonus in legs.items():
        name = cov + ' - ' + leg

        if spread_add == True:
            target_str = '\ndesired_targets=1\n' + spread
        elif args.targets == 0:
            target_str = '\n' + mplus + '\n' + move
        elif args.targets < 0:
            target_str = '\ndesired_targets=' + targets.strip('-') + '\n' + move
        else:
            target_str = '\ndesired_targets=' + targets

        if cov == 'kyrian':
            cov_str = '\ncovenant=kyrian\nsoulbind=combat_meditation/fury_of_the_skies:7/umbral_intensity:7/let_go_of_the_past'
        elif cov == 'necrolord':
            cov_str = '\ncovenant=necrolord\nsoulbind=lead_by_example/fury_of_the_skies:7/evolved_swarm:7'
        elif cov == 'night_fae':
            cov_str = '\ncovenant=night_fae\nsoulbind=grove_invigoration/conflux_of_elements:7/niyas_tools_burrs'
        elif cov == 'venthyr':
            cov_str = '\ncovenant=venthyr\nsoulbind=soothing_shade/endless_thirst:7/fury_of_the_skies:7'

        simc = profile + '\ntalents=0000000' + cov_str + '\n\ntabard=,id=31405,bonus_id=' + str(bonus) + '\n\nname=\"' + name + '\"\n\n' + target_str + '\n\n' + sets

        while True:
            time.sleep(5) 

            try:
                post = requests.post(post_url, json={'type': 'advanced', 'apiKey': apikey, 'simcVersion': 'nightly', 'advancedInput': simc})
                reply = post.json()
                simID = reply['simId']
                sim_url = report_url + simID
                print(sim_url)
                break
            except:
                continue

        while True:
            time.sleep(5)

            try:
                get = requests.get(get_url + simID)
                status = get.json()
                if (status['job']['state'] == 'complete'):
                    data = requests.get(sim_url + '/data.json')
                    results = data.json()
                    break
                continue
            except:
                continue

        dps_list = {}
        for actor in results['sim']['profilesets']['results']:
            dps_list[actor['name']] = actor['mean']

        dps_max = max(dps_list, key=dps_list.get)
        name2 = cov.rjust(9,'$') + '-' + leg.ljust(7,'$')
        html = '<div><a href=\"chart.html?simid=' + simID + '\" target=\"simframe\">' + name2.replace('$', '&nbsp;') + '|' + str(dps_max).replace('_', '&nbsp;') + ' ' + f'{dps_list[dps_max]:.2f}' + '</a></div>\n'
        buffer[html] = dps_list[dps_max]

sorted_buf = sorted(buffer.items(), key=lambda x: x[1], reverse=True)

output = 'by_combo_'
if spread_add == True:
    output += 'S'
else:
    output += targets

betabot = open(output + '.html', 'w')
betabot.write('<html><style>body {margin-left:0; margin-right:0} a {color:#FF7D0A; text-decoration:none; font-family:monospace; font-size:large;}</style><body>\n')

for buf in sorted_buf:
    betabot.write(buf[0])

betabot.write('</body></html>\n')
betabot.close()
