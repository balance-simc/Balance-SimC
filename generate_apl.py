import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('simcpath', type=str, help='path to SimC root (include \\simc)')
parser.add_argument('-f', '--file', type=str, help='apl txt file')
args = parser.parse_args()
simc_path = args.simcpath

apl_lists = {}

with open(args.file, 'r') as apl_file:
    temp_comment=""
    for line in apl_file:
        if line.startswith('####'):
            temp_comment = line.strip('# \n')
        if line.startswith('actions'):
            apl = 'default'

            split_ = line.split('=', 1)
            pref = split_[0].rstrip('+')
            suf = split_[1].lstrip('/').rstrip('\n')

            if suf == 'flask' or suf == 'food' or suf == 'augmentation' or suf == 'snapshot_stats':
                continue

            pref_apl_ = pref.split('.')
            if len(pref_apl_) > 1:
                apl = pref_apl_[1]

            if apl not in apl_lists:
                apl_lists[apl] = []
            apl_lists[apl].append((suf,temp_comment))
            temp_comment=""

with open(os.path.join(simc_path, 'engine', 'class_modules', 'apl', 'balance_apl.inc'), 'w') as inc:
    for apl in apl_lists.keys():
        apl_var = apl
        if apl_var == 'default':
            apl_var = 'def'

        inc.write('action_priority_list_t* ' + apl_var + ' = get_action_priority_list( \"' + apl + '\" );\n')

    for apl in apl_lists.keys():
        apl_var = apl
        if apl_var == 'default':
            apl_var = 'def'

        inc.write('\n')
        for action in apl_lists[apl]:
            if action[1]:
                inc.write(apl_var + '->add_action( \"' + action[0] + '\",\"'+action[1]+'\" );\n')
            else:
                inc.write(apl_var + '->add_action( \"' + action[0] + '\" );\n')
