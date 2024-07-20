import sys
import os

if len(sys.argv) != 2:
    sys.exit(1)

input_file_path = sys.argv[1]

valid_prefixes = ['game', 'effect', 'sound', 'expression']
agents = {}

with open(input_file_path, 'r') as input_file:
    for line in input_file:
        if 'unsafe extern "C" fn ' in line:
            line = line.replace('unsafe extern "C" fn ', '').replace('(agent: &mut L2CAgentBase) {', '').strip()

            prefix_index = -1
            for prefix in valid_prefixes:
                index = line.find(prefix)
                if index != -1:
                    prefix_index = index
                    break
            
            if prefix_index != -1:
                parts_before_prefix = line[:prefix_index].strip('_')
                prefix = line[prefix_index:].split('_')[0]
                rest = line[prefix_index + len(prefix) + 1:] 

                agent_name = parts_before_prefix if parts_before_prefix else "UNKNOWN"
                
                if agent_name not in agents:
                    agents[agent_name] = []
                
                formatted_line = f'        .{prefix}_acmd("{prefix}_{rest}", {line}, Default)'
                agents[agent_name].append(formatted_line)

with open(input_file_path, 'a') as output_file:
    output_file.write('\n\npub fn install() {\n')
    for agent, commands in agents.items():
        output_file.write(f'    Agent::new("{agent}")\n')
        for command in commands:
            output_file.write(f'{command}\n')
        output_file.write('        .install();\n')
    output_file.write('}\n')
