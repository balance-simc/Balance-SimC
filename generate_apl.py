import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('simcpath', type=str, help='path to SimC root (include \\simc)')
args = parser.parse_args()
simc_path = args.simcpath

cpp_path = os.path.join(simc_path, 'engine', 'class_modules', 'sc_druid.cpp')

apl_lists = {}

with open('balance.txt', 'r') as apl_file:
    next_comment=""
    for line in apl_file:
        if line.startswith('####'):
            next_comment=line.strip('# \n')
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
            if next_comment:
                apl_lists[apl].append(suf,next_comment)
                next_comment=""
            else:
                apl_lists[apl].append(suf,)

marker_start = '### BALANCE_APL_START ###'
marker_end = '### BALANCE_APL_END ###'

cpp_old = open(cpp_path, 'r')
cpp_new = open(cpp_path + '__', 'w')

state = 0

for line in cpp_old:
    if marker_end in line:
        state = 0

    if state == 0:
        cpp_new.write(line)

    if marker_start in line:
        state = 2

    if state == 2:
        state = 1

        for apl in apl_lists.keys():
            apl_var = apl
            if apl_var == 'default':
                apl_var = 'def'

            cpp_new.write('  action_priority_list_t* ' + apl_var + ' = get_action_priority_list( \"' + apl + '\" );\n')

        for apl in apl_lists.keys():
            apl_var = apl
            if apl_var == 'default':
                apl_var = 'def'

            cpp_new.write('\n')
            for action in apl_lists[apl]:
                if action[1]:                    
                    cpp_new.write('  ' + apl_var + '->add_action( \"' + action[0] + '\",\"'+action[1]+'\" );\n')
                else:
                    cpp_new.write('  ' + apl_var + '->add_action( \"' + action[0] + '\" );\n')

cpp_new.close()
cpp_old.close()

os.replace(cpp_path + '__', cpp_path)
