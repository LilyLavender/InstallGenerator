import os
import sys

def process_file(input_file_path):
    valid_acmd_prefixes = ['game', 'effect', 'sound', 'expression']
    agents = {}

    if not os.path.isfile(input_file_path):
        print(f"File not found: {input_file_path}")
        return

    with open(input_file_path, 'r') as input_file:
        lines = input_file.readlines()

    for line in lines:
        if '_' not in line:
            continue

        if 'unsafe extern "C" fn ' in line:
            print(f"Found a function definition: {line.strip()}")
            line = line.replace('unsafe extern "C" fn ', '')
            if '(agent: &mut L2CAgentBase) {' in line:
                line = line.replace('(agent: &mut L2CAgentBase) {', '').strip()
                prefix_type = "ACMD"
            elif '(fighter: &mut L2CFighterCommon) {' in line:
                line = line.replace('(fighter: &mut L2CFighterCommon) {', '').strip()
                print("Identified as a fighter frame script.")
            elif '(weapon: &mut L2CWeaponCommon) {' in line:
                line = line.replace('(weapon: &mut L2CWeaponCommon) {', '').strip()
                print("Identified as a weapon frame script.")

            if line.endswith('}'):
                line = line[:-1].rstrip()

            if '-> L2CValue' in line:
                print("Identified as a status script.")
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
                    print(f"Invalid status type: {status_type}. Skipping this script.")
                    continue

                if agent_name not in agents:
                    agents[agent_name] = []

                formatted_line = f'        .status({formatted_status_type}, *UNKNOWN_STATUS, {status_name})'
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

                formatted_line = f'        .on_line(Main, {frame_name})'
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

                    formatted_line = f'        .{prefix}_acmd("{prefix}_{rest}", {line}, Default)'
                    agents[agent_name].append(formatted_line)
                    print(f"Identified as a {prefix} ACMD script: {line.strip()}.")

    if agents:
        with open(input_file_path, 'a') as output_file:
            output_file.write('\npub fn install() {\n')
            for agent, commands in agents.items():
                output_file.write(f'    Agent::new("{agent}")\n')
                for command in commands:
                    output_file.write(f'{command}\n')
                output_file.write('        .install();\n')
            output_file.write('}\n')

    print(f"Found {len(agents)} agents.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_file>")
    else:
        input_file_path = sys.argv[1]
        print("Processing started.")
        process_file(input_file_path)
        print("Processing complete.")
