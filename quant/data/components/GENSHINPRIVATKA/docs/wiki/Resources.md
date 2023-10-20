# MongoDB Tutorial

## Prerequisites
-[MongoDB](https://www.mongodb.com/try/download/community)<br/>
-[MongoDB Compass](https://www.mongodb.com/try/download/compass) (Optional)

## Running MongoDB Server
1. Download The MongoDB installation Package, and install like usual
2. After installing MongoDB, open MongoDB Compass. Then Write `mongodb://localhost:27017` At URL
3. Grasscutter will automatically create the data on start

## Solution Fix
Q1: How To Fix MongoDB Server Not Activated?<br/>
A1: Go to Your MongoDB installation folder. The default path is `C:\Program Files\MongoDB\Server\<version>\bin`. Find mongod.exe and run it. 


# Redirecting Text Blocks

## Fiddler Classic JScript
```js
import System;
import System.Windows.Forms;
import Fiddler;
import System.Text.RegularExpressions;

class Handlers
{
    static function OnBeforeRequest(oS: Session) {
        if (oS.host.Equals("overseauspider.yuanshen.com:8888")) {
            oS.oRequest.FailSession(404, "Not Found", "Not Found");
        }
        else if(oS.host.EndsWith(".yuanshen.com") || oS.host.EndsWith(".hoyoverse.com") || oS.host.EndsWith(".mihoyo.com")) {
            oS.host = "localhost"; // This can also be replaced with another IP address.
        }
    }
};
```

## Hosts File
```
127.0.0.1 dispatchosglobal.yuanshen.com
127.0.0.1 dispatchcnglobal.yuanshen.com
127.0.0.1 osusadispatch.yuanshen.com
127.0.0.1 oseurodispatch.yuanshen.com
127.0.0.1 osasiadispatch.yuanshen.com

127.0.0.1 hk4e-api-os-static.mihoyo.com
127.0.0.1 hk4e-api-static.mihoyo.com
127.0.0.1 hk4e-api-os.mihoyo.com
127.0.0.1 hk4e-api.mihoyo.com
127.0.0.1 hk4e-sdk-os.mihoyo.com
127.0.0.1 hk4e-sdk.mihoyo.com

127.0.0.1 account.mihoyo.com
127.0.0.1 api-os-takumi.mihoyo.com
127.0.0.1 api-takumi.mihoyo.com
127.0.0.1 sdk-os-static.mihoyo.com
127.0.0.1 sdk-static.mihoyo.com
127.0.0.1 webstatic-sea.mihoyo.com
127.0.0.1 webstatic.mihoyo.com
127.0.0.1 uploadstatic-sea.mihoyo.com
127.0.0.1 uploadstatic.mihoyo.com

127.0.0.1 api-os-takumi.hoyoverse.com
127.0.0.1 sdk-os-static.hoyoverse.com
127.0.0.1 sdk-os.hoyoverse.com
127.0.0.1 webstatic-sea.hoyoverse.com
127.0.0.1 uploadstatic-sea.hoyoverse.com
127.0.0.1 api-takumi.hoyoverse.com
127.0.0.1 sdk-static.hoyoverse.com
127.0.0.1 sdk.hoyoverse.com
127.0.0.1 webstatic.hoyoverse.com
127.0.0.1 uploadstatic.hoyoverse.com
127.0.0.1 account.hoyoverse.com
127.0.0.1 api-account-os.hoyoverse.com
127.0.0.1 api-account.hoyoverse.com

127.0.0.1 hk4e-api-os.hoyoverse.com
127.0.0.1 hk4e-api-os-static.hoyoverse.com
127.0.0.1 hk4e-sdk-os.hoyoverse.com
127.0.0.1 hk4e-sdk-os-static.hoyoverse.com
127.0.0.1 hk4e-api.hoyoverse.com
127.0.0.1 hk4e-api-static.hoyoverse.com
127.0.0.1 hk4e-sdk.hoyoverse.com
127.0.0.1 hk4e-sdk-static.hoyoverse.com

0.0.0.0 log-upload.mihoyo.com
0.0.0.0 log-upload-os.mihoyo.com
0.0.0.0 log-upload-os.hoyoverse.com
0.0.0.0 devlog-upload.mihoyo.com
0.0.0.0 overseauspider.yuanshen.com
```

# Fun

## Colored nickname and signature :peacock: ([written by](https://github.com/actuallyeunha))
Unity supports colored text by default (See [Unity Manual](https://docs.unity3d.com/Packages/com.unity.ugui@1.0/manual/StyledText.html) for more info)

By replacing them with `<color=color>text</color>` or `<color=#HEXCODE>text</color>` you can change most, if not all, strings' colors.

**It's not possible to do this directly in game, you have to edit the db using something like MongoDBCompass!**

1. Open MongoDBCompass and connect to your db
2. Go to `grasscutter/players`
3. Make your changes. *Change it inside `playerProfile` too!* <br>
        e.g  `nickname: "<color=#ff9ec6>na.na</color>"`; <br>
        `signature: "Running on <color=green>Grasscutter</color>!"`
4. Update the document
5. Relog to see changes

Enjoy your colorful name :sparkles:

## Avatar/Character ([written by](https://github.com/junu128))
This guide is recommended if you have the character/weapon. If you want to get a character at Level Z, then use !givechar [avatarID] [level]
### Changing Level/Ascension/Talents
> Make sure you have created an account with the avatars/characters.
1. Open **MongoDBCompass**
2. Connect to the host (default URI is `mongodb://localhost:27017`)
3. Navigate to Databases > `grasscutter` > `avatars`
4. (Optional) Set **View** to `JSON View`
5. In the **Filter** field, type `{ avatarId: X }` where `X` is the Avatar ID that you are trying to modify. **Avatar IDs are 8-digits.**
6. Click the **Find** next to the field. 
7. After the documents have been filtered, edit the document
	1. To change character **level**, change the value next to `"level"`
	2. To change character **ascension**, change the value next to `"promoteLevel"`
		 Check [Wiki](https://genshin-impact.fandom.com/wiki/Characters#:~:text=one%20Acquaint%20Fate.-,Ascension%20Phase,-Max%20Char.%20Level) for ascension values
	3. To change **talents**, expand `"proudSkillList"`
		1. To unlock the avatar's **1st Ascension Passive**, add XX2101 inside `"proudSkillList"`, where **XX is the last 2 digits of the Avatar ID**. **Make sure to add a `,` for each line.** 
		2. To unlock the avatar's **4th Ascension Passive**, do the same as before, but replace `2101` with `2201`.
8. After editing, you can now **Replace**.
### Example
A document in JSON view that has the Avatar ID 10000058, level 90, ascension phase 6, all talents unlocked.

<a href="https://imgur.com/ZJf6L3K"><img src="https://i.imgur.com/ZJf6L3K.png" title="source: imgur.com" /></a>


### Notes
- On the last line of `"proudSkillList"`, a `,` is no longer needed. 
- After replacing the document, make sure to restart the server for changes to take effect. 


## Weapons
> Make sure you have created an account with the weapons.
1. Open **MongoDBCompass**
2. Connect to the host (default URI is `mongodb://localhost:27017`)
3. Navigate to Databases > `grasscutter` > `items`
4. (Optional) Set **View** to `JSON View`
5. In the **Filter** field, type `{ itemId: Y }` where `Y` is the Item/Weapon ID that you are trying to modify. **Weapon IDs are 5 digits.**
6. Click the **Find** next to the field. 
7. After the documents have been filtered, edit the document
	1. To change weapon **level**, change the value next to `"level"`
	2. To change weapon **ascension**, change the value next to `"promoteLevel"`
		 Check [Wiki](https://genshin-impact.fandom.com/wiki/Weapons#:~:text=reaching%202nd%20Ascension.-,Ascension%20Phase,-Max%20Weapon%20Level) for ascension values
	3. To change **refinement**, change the value next to `"refinement"`
		* Refinement Rank 1 = 0
		* Refinement Rank 2 = 1
		* Refinement Rank 3 = 2
		* Refinement Rank 4 = 3
		* Refinement Rank 5 = 4
8. After editing, you can now **Replace**.
### Example
A document in JSON view that has the Weapon ID 12503, level 90, ascension phase 6, refinement rank 5.

<a href="https://imgur.com/b8yW79b"><img src="https://i.imgur.com/b8yW79b.png" title="source: imgur.com" /></a>

# Connectivity

## Client connection & auth flowchart
<a href="https://media.discordapp.net/attachments/965619953900326973/1047883910366908447/unknown.png?width=737&height=676"><img src="https://media.discordapp.net/attachments/965619953900326973/1047883910366908447/unknown.png?width=737&height=676" title="Flowchart" /></a>

# In-Game

## Teleporting
  - When you want to teleport to somewhere, use the in-game marking function on Map.
    - Mark a point on the map using the fish hook marking (the last one.)
    - (optional) rename the map marker to a number to override the default Y coordinate (height, default 300.)
    - Confirm and close the map.
    - You will see your character falling from a very high destination, exact location that you marked.