import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

export function activate(context: vscode.ExtensionContext) {

    let disposable = vscode.commands.registerCommand('smashline2installgenerator.processFile', () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No file is currently open.');
            return;
        }

        const document = editor.document;
        const inputFilePath = document.fileName;

        if (!fs.existsSync(inputFilePath)) {
            vscode.window.showErrorMessage(`File not found: ${inputFilePath}`);
            return;
        }

        processFile(inputFilePath);
    });

    context.subscriptions.push(disposable);
}

export function deactivate() {}

function processFile(inputFilePath: string) {
    const validAcmdPrefixes = ['game', 'effect', 'sound', 'expression'];
    let agents: { [key: string]: string[] } = {};

    const content = fs.readFileSync(inputFilePath, 'utf-8');
    const lines = content.split(/\r?\n/);

    lines.forEach(line => {
        if (!line.includes('_')) {
            return;
        }

        if (line.includes('unsafe extern "C" fn ')) {
            console.log(`Found a function definition: ${line.trim()}`);
            line = line.replace('unsafe extern "C" fn ', '');
            let scriptType = '';

            if (line.includes('(agent: &mut L2CAgentBase) {')) {
                line = line.replace('(agent: &mut L2CAgentBase) {', '').trim();
                scriptType = 'ACMD';
            } else if (line.includes('(fighter: &mut L2CFighterCommon) {')) {
                line = line.replace('(fighter: &mut L2CFighterCommon) {', '').trim();
                console.log('Identified as a fighter frame script.');
            } else if (line.includes('(weapon: &mut L2CWeaponCommon) {')) {
                line = line.replace('(weapon: &mut L2CWeaponCommon) {', '').trim();
                console.log('Identified as a weapon frame script.');
            }

            if (line.endsWith('}')) {
                line = line.slice(0, -1).trim();
            }

            if (line.includes('-> L2CValue')) {
                console.log('Identified as a status script.');
                processStatusScript(line, agents);
            } else if (line.includes('frame')) {
                console.log('Identified as a frame script.');
                processFrameScript(line, agents);
            } else if (scriptType === 'ACMD') {
                processAcmdScript(line, validAcmdPrefixes, agents);
            }
        }
    });

    if (Object.keys(agents).length > 0) {
        const outputContent = generateOutputContent(agents);
        fs.appendFileSync(inputFilePath, outputContent);
        console.log(`Processing complete. Found ${Object.keys(agents).length} agents.`);
    }
}

function processStatusScript(line: string, agents: { [key: string]: string[] }) {
    const parts = line.split('(');
    const statusName = parts[0].trim();
    let agentName = '';

    if (line.includes('weapon')) {
        agentName = statusName.split('_', 2).join('_');
    } else {
        agentName = statusName.split('_', 1)[0];
    }

    const statusType = statusName.split('_').pop() || '';
    const validStatusTypes = ['pre', 'init', 'main', 'exec', 'exit', 'end'];
    if (!validStatusTypes.includes(statusType)) {
        console.log(`Invalid status type: ${statusType}. Skipping this script.`);
        return;
    }

    const formattedStatusType = capitalizeFirstLetter(statusType);
    if (!agents[agentName]) {
        agents[agentName] = [];
    }

    const formattedLine = `        .status(${formattedStatusType}, *UNKNOWN_STATUS, ${statusName})`;
    agents[agentName].push(formattedLine);
}

function processFrameScript(line: string, agents: { [key: string]: string[] }) {
    const parts = line.split('(');
    const frameName = parts[0].trim();

    let agentName = '';
    if (["global_fighter_frame", "global_frame", "fighter_frame"].includes(frameName)) {
        agentName = 'fighter';
    } else {
        agentName = frameName.replace('_frame', '');
    }

    if (!agents[agentName]) {
        agents[agentName] = [];
    }

    const formattedLine = `        .on_line(Main, ${frameName})`;
    agents[agentName].push(formattedLine);
}

function processAcmdScript(line: string, validAcmdPrefixes: string[], agents: { [key: string]: string[] }) {
    let prefixIndex = -1;
    let prefix = '';
    for (const validPrefix of validAcmdPrefixes) {
        const index = line.indexOf(validPrefix);
        if (index !== -1) {
            prefixIndex = index;
            prefix = validPrefix;
            break;
        }
    }

    if (prefixIndex !== -1) {
        const partsBeforePrefix = line.slice(0, prefixIndex).replace(/_+$/, '');
        const rest = line.slice(prefixIndex + prefix.length + 1);

        const agentName = partsBeforePrefix || 'UNKNOWN';
        if (!agents[agentName]) {
            agents[agentName] = [];
        }

        const formattedLine = `        .${prefix}_acmd("${prefix}_${rest}", ${line}, Default)`;
        agents[agentName].push(formattedLine);
        console.log(`Identified as a ${prefix} ACMD script: ${line.trim()}.`);
    }
}

function generateOutputContent(agents: { [key: string]: string[] }): string {
    let output = '\npub fn install() {\n';
    for (const [agent, commands] of Object.entries(agents)) {
        output += `    Agent::new("${agent}")\n`;
        commands.forEach(command => {
            output += `${command}\n`;
        });
        output += '        .install();\n';
    }
    output += '}\n';
    return output;
}

function capitalizeFirstLetter(string: string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}
