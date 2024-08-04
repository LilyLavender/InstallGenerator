# InstallGenerator
**Generates an install section for Smashline 2 mods.**  
Three different versions exist for VSCode, Notepad++, and just a .py file.  
For documentation on each one, see the [Wiki](https://github.com/LilyLavender/InstallGenerator/wiki)

## What types of scripts does it work for?
Works for:
- ACMD (game, effect, sound, expression)
- OPFF & OPWF
- Statuses

## Installation & Usage
See [Wiki](https://github.com/LilyLavender/InstallGenerator/wiki)

## Example
This input:
```rs
unsafe extern "C" fn mario_game_attackairn(agent: &mut L2CAgentBase) {}

unsafe extern "C" fn luigi_fireball_effect_regular(agent: &mut L2CAgentBase) {}

unsafe extern "C" fn kamui_sound_attackdash(agent: &mut L2CAgentBase) {}

unsafe extern "C" fn expression_attack11(agent: &mut L2CAgentBase) {}

unsafe extern "C" fn mario_frame(fighter: &mut L2CFighterCommon) {}

unsafe extern "C" fn global_fighter_frame(fighter: &mut L2CFighterCommon) {}

unsafe extern "C" fn rosetta_tico_frame(weapon: &mut L2CWeaponCommon) {}

unsafe extern "C" fn luigi_fireball_start_main(weapon: &mut L2CWeaponCommon) -> L2CValue {}

unsafe extern "C" fn mario_specialhi_pre(fighter: &mut L2CFighterCommon) -> L2CValue {}
```
Will result in this install being generated:
```rs
pub fn install() {
    Agent::new("mario")
        .game_acmd("game_attackairn", mario_game_attackairn, Default)
        .on_line(Main, mario_frame)
        .status(Pre, *UNKNOWN_STATUS, mario_specialhi_pre)
        .install();
    Agent::new("luigi_fireball")
        .effect_acmd("effect_regular", luigi_fireball_effect_regular, Default)
        .status(Main, *UNKNOWN_STATUS, luigi_fireball_start_main)
        .install();
    Agent::new("kamui")
        .sound_acmd("sound_attackdash", kamui_sound_attackdash, Default)
        .install();
    Agent::new("UNKNOWN")
        .expression_acmd("expression_attack11", expression_attack11, Default)
        .install();
    Agent::new("fighter")
        .on_line(Main, global_fighter_frame)
        .install();
    Agent::new("rosetta_tico")
        .on_line(Main, rosetta_tico_frame)
        .install();
}
```