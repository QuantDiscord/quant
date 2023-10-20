# Commands

You might want to use the handbook generation command (`java -jar grasscutter.jar -handbook`) in a terminal that is in a Grasscutter installation. 
It will generate the handbook (GM Handbook.txt) where you can find IDs for enemies/items/etc.

You may want to use the gacha map generation (`java -jar grasscutter.jar -gachamap`) to generate a mapping file for the gacha record subsystem. 
The file will be generated in `(resources)/gcstatic`. (otherwise, you may only see number IDs on the gacha record page)

There is a dummy user named "Server" in every player's friends list that you can message to use commands. 
Commands also work in other chat rooms, such as private/team chats. to run commands in-game, you need to append a prefix `/` or `!` to your messages. (ex. `/pos`)

### Targeting
 1. For commands that target a player, you can specify a target UID with `@UID` as an argument in any position.
 2. If you message a valid command at another player (instead of at the "Server" virtual player), they will be the set target for that command if you haven't already set the target.
 3. If none of the above apply, it will default to the target you previously set using: `/target <UID>`.
 4. If none of the above *still* apply, you will be the target of the command. If you are entering the command from the server console, **it will not work**!

 Note that performing commands on other players will usually require a permission related to the base permission node. 
(e.g. `player.give` becomes `player.give.others` if used on another player)

You can set an empty target that overrides steps 2-4 by using `@` as an argument. This is currently only useful as a special case of the
`sendmessage` command which sends to *all* players on the server, like the old `broadcast` command.

### Informational commands (no permissions)
| Commands | Description                                                            | Alias | Targeting     | Usage          |
| -------- | ---------------------------------------------------------------------- | ----- | ------------- | -------------- |
| list     | Lists online players.                                                  |       | None          | list           |
| help     | Sends the help message or shows information about a specified command. |       | None          | help [command] |
| position | Sends your current coordinates.                                        | pos   | Online Player | position       |

### Commands for server admins
| Commands    | Description                                                                               | Alias | Targeting     | Usage                                       | Permission node    |
| ----------- | ----------------------------------------------------------------------------------------- | ----- | ------------- | ------------------------------------------- | ------------------ |
| account     | Creates an account with the specified username, and the in-game UID if specified.         |       | Server only   | `account <create\|delete> <username> [UID]` | (can only use on server console) |
| permission  | Grants or removes a permission for a user.                                                |       | Player        | `permission <add\|remove> <permission>`     | permission         |
| kick        | Kicks the specified player from the server.                                               | k     | Online Player | `kick`                                      | server.kick (only for others) |
| ban         | Kicks and bans the specified player from the server.                                      |       | Player        | `ban [timestamp] [reason]`                  | server.ban         |
| unban       | Unbans specified player from the server.                                                  |       | Player        | `unban`                                     | server.ban         |
| sendmessage | Sends a message to a player as the server. If used without a target, message all players. | say   | None          | `say <message>`                             | server.sendmessage |
| reload      | Reloads the server config.                                                                |       | None          | `reload`                                    | server.reload      |
| stop        | Stops the server.                                                                         |       | None          | `stop`                                      | server.stop        |

### Commands that can potentially harm players
| Commands       | Description                                                                                       | Alias              | Targeting     | Usage                                 | Permission node           |
| -------------- | ------------------------------------------------------------------------------------------------- | ------------------ | ------------- | ------------------------------------- | ------------------------- |
| clear          | Deletes all unequipped and unlocked lvl0 artifacts(art)/weapons(wp)/material(mat) from inventory. |                    | Online Player | `clear <all\|wp\|art\|mat>`           | player.clearinv           |
| give           | Gives item(s) to you or the specified player.                                                     | g item giveitem    | Online Player | `give <itemId\|avatarId> [see below]` | player.give               |
| resetconst     | Resets currently selected (or all) character(s) to C0. Relog to see proper effects.               | resetconstellation | Online Player | `resetconst [all]`                    | player.resetconstellation |
| setfetterlevel | Sets the friendship level for your currently selected character.                                  | setfetterlvl       | Online Player | `setfetterlevel <level>`              | player.setfetterlevel     |
| setprop        | Sets accountwide properties.                                                                      | prop               | Online Player | `setprop <prop> <value>`              | player.setprop            |
| talent         | Sets talent level for your currently selected character                                           |                    | Online Player | `talent <talentID> <value>`           | player.settalent          |

### Commands without lasting effects
| Commands     | Description                                                                             | Alias | Targeting     | Usage                                                             | Permission node     |
| ------------ | --------------------------------------------------------------------------------------- | ----- | ------------- | ----------------------------------------------------------------- | ------------------- |
| coop         | Forces someone to join the world of others.                                             |       | Online Player | `coop [host UID (default self)]`                                  | server.coop         |
| tpall        | Teleports all players in your world to your position.                                   |       | Online Player | `tpall`                                                           | player.tpall        |
| heal         | Heals all characters in your current team.                                              | h     | Online Player | `heal`                                                            | player.heal         |
| killall      | Kills all entities in the current scene or specified scene of the corresponding player. |       | Online Player | `killall [sceneId]`                                               | server.killall      |
| setstats     | Sets a stat for your currently selected character.                                      | stats | Online Player | `setstats <stat> <value>`                                         | player.setstats     |
| spawn        | Spawns some entities around you.                                                        |       | Online Player | `spawn <entityId\|itemId> [amount] [level(monster only)]`         | server.spawn        |
| team         | Add, remove, or swap avatars in your current team. Index start from 1.                  |       | Online Player | `team <add\|remove\|set> [avatarId,...] [index\|index-index,...]` | player.team         |
| teleport     | Change the player's position.                                                           | tp    | Online Player | `teleport <x> <y> <z> [sceneId]`                                  | player.teleport     |
| enterdungeon | Enter a dungeon by dungeon ID.                                                          |       | Online Player | `enterdungeon <dungeon id>`                                       | player.enterdungeon |
| weather      | Changes the weather.                                                                    | w     | Online Player | `weather [weatherID] [climate]`                                   | player.weather      |

### Give command
The `give` command now has the functionality of the old `giveall`, `giveart` and `givechar` commands.

`give` has keyword arguments `x<amount>`, `lv<level>`, `r<refinement>` and `c<constellation>` which can be used anywhere in the command, just like `@UID` can be.
`x<amount>` can also be written as `<amount>x`, and `lv<level>` can be `l<level>` or `lvl<level>`, and they can all be chained together without spaces, e.g. `lv90r5x10`.

To give all items, do `give <all|weapons|mats|avatars> [x<amount>]`. The above keyword arguments are all valid for this.

The artifact syntax is `give <artifactId> [mainPropId] [<appendPropId>[,<times>]]...`. `x<amount>` and `lv<level>` work with this, and note that this uses levels of 0-20 to match displayed in-game numbers rather than 1-21, though it won't complain if you feed it `lv21`.

### SetProp command
`prop <godmode|nostamina|unlimitedenergy> <on|off|toggle|1|0>` replaces the old `godmode`, `nostamina`, `unlimitenergy` commands.

`prop <god|ns|ue> <value>` are the shortest aliases for them.

`prop abyss 12` replaces `unlocktower`. Full syntax is `prop <abyss|abyssfloor|ut|tower|towerlevel|unlocktower> <floor to unlock>` 

To set BP level: `prop <bplevel|bp|battlepass> <level>`

And world level: `prop <worldlevel|wl> <level>`

AR: `prop player_level <level>`