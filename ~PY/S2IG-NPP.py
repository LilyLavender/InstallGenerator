import os
from Npp import notepad, editor, console

def process_file():
    valid_acmd_prefixes = ['game', 'effect', 'sound', 'expression']
    agents = {}

    input_file_path = notepad.getCurrentFilename()

    if not os.path.isfile(input_file_path):
        console.writeError("File not found: {}\n".format(input_file_path))
        return

    with open(input_file_path, 'r') as input_file:
        lines = input_file.readlines()

    for line in lines:
        if '_' not in line:
            continue
        
        if 'unsafe extern "C" fn ' in line:
            console.write("Found a function definition: {}\n".format(line.strip()))
            line = line.replace('unsafe extern "C" fn ', '')
            if '(agent: &mut L2CAgentBase) {' in line:
                line = line.replace('(agent: &mut L2CAgentBase) {', '').strip()
                prefix_type = "ACMD"
            elif '(fighter: &mut L2CFighterCommon) {' in line:
                line = line.replace('(fighter: &mut L2CFighterCommon) {', '').strip()
                console.write("Identified as a fighter frame script.\n")
            elif '(weapon: &mut L2CWeaponCommon) {' in line:
                line = line.replace('(weapon: &mut L2CWeaponCommon) {', '').strip()
                console.write("Identified as a weapon frame script.\n")

            if line.endswith('}'):
                line = line[:-1].rstrip()

            if '-> L2CValue' in line:
                console.write("Identified as a status script.\n")
                parts = line.split('(')
                status_name = parts[0].strip()
                agent_name = ""

                if "weapon" in line:
                    agent_name = status_name.split('_', 2)[:2]
                    agent_name = "_".join(agent_name)
                else:
                    agent_name = status_name.split('_', 1)[0]

                status_type = status_name.rsplit('_', 1)[-1]
                valid_status_types = ['pre', 'init', 'main', 'exec', 'exit', 'end']
                if status_type in valid_status_types:
                    formatted_status_type = status_type.capitalize()
                else:
                    console.write("Invalid status type: {}. Skipping this script.\n".format(status_type))
                    continue

                if agent_name not in agents:
                    agents[agent_name] = []
                
                formatted_line = '        .status({}, *UNKNOWN_STATUS, {})'.format(formatted_status_type, status_name)
                agents[agent_name].append(formatted_line)

            elif 'frame' in line:
                parts = line.split('(')
                frame_name = parts[0].strip()
                
                if frame_name in ["global_fighter_frame", "global_frame", "fighter_frame"]:
                    agent_name = "fighter"
                else:
                    agent_name = frame_name.rsplit('_', 1)[0]

                if agent_name not in agents:
                    agents[agent_name] = []
                
                formatted_line = '        .on_line(Main, {})'.format(frame_name)
                agents[agent_name].append(formatted_line)

            elif '_' in line:
                prefix_index = -1
                for prefix in valid_acmd_prefixes:
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
                    
                    formatted_line = '        .{}_acmd("{}_{}", {}, Default)'.format(prefix, prefix, rest, line)
                    agents[agent_name].append(formatted_line)
                    console.write("Identified as a {} ACMD script: {}.\n".format(prefix, line.strip()))

    if agents:
        with open(input_file_path, 'a') as output_file:
            output_file.write('\npub fn install() {\n')
            for agent, commands in agents.items():
                output_file.write('    Agent::new("{}")\n'.format(agent))
                for command in commands:
                    output_file.write('{}\n'.format(command))
                output_file.write('        .install();\n')
            output_file.write('}\n')

    console.write("Found {} agents.\n".format(len(agents)))

console.write("Processing started.\n")
process_file()
console.write("Processing complete.\n")
