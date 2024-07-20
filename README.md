# InstallGenerator
Generates an install section for Smashline 2 mods

### Requirements 
Requires Python 3.0 or higher

### IMPORTANT
Currently **only works for acmd** (game, effect, sound, expression) scripts.  
Will **not work properly** for opff, status, hooks, or anything else.  
Also is only meant for **Smashline 2** scripts. Will not work for Smashline 1.  

### Usage
Drag a rs (or any other type for that matter) file onto Smashline2InstallGenerator.py
Here's an example rs:
```rust
unsafe extern "C" fn game_attackdash(agent: &mut L2CAgentBase) {
    ...
}

unsafe extern "C" fn effect_attackdash(agent: &mut L2CAgentBase) {
    ...
}

unsafe extern "C" fn sound_attackdash(agent: &mut L2CAgentBase) {
    ...
}

unsafe extern "C" fn expression_attackdash(agent: &mut L2CAgentBase) {
    ...
}

unsafe extern "C" fn cloud_game_attackhi3(agent: &mut L2CAgentBase) {
    ...
}

unsafe extern "C" fn cloud_effect_attackhi3(agent: &mut L2CAgentBase) {
    ...
}

unsafe extern "C" fn cloud_sound_attackhi3(agent: &mut L2CAgentBase) {
    ...
}

unsafe extern "C" fn cloud_expression_attackhi3(agent: &mut L2CAgentBase) {
    ...
}

unsafe extern "C" fn dolly_fire_effect_regular(agent: &mut L2CAgentBase) {
    ...
}
```
The program will then append an install section to the end of the file. 
Here's what it will output in the case shown above:
```rust
pub fn install() {
    Agent::new("UNKNOWN")
        .game_acmd("game_attackdash", game_attackdash, Default)
        .effect_acmd("effect_attackdash", effect_attackdash, Default)
        .sound_acmd("sound_attackdash", sound_attackdash, Default)
        .expression_acmd("expression_attackdash", expression_attackdash, Default)
        .install();
    Agent::new("cloud")
        .game_acmd("game_attackhi3", cloud_game_attackhi3, Default)
        .effect_acmd("effect_attackhi3", cloud_effect_attackhi3, Default)
        .sound_acmd("sound_attackhi3", cloud_sound_attackhi3, Default)
        .expression_acmd("expression_attackhi3", cloud_expression_attackhi3, Default)
        .install();
    Agent::new("dolly_fire")
        .effect_acmd("effect_regular", dolly_fire_effect_regular, Default)
        .install();
}
```