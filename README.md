# Scout

A set of (outdated) tools for players in the online browser MMORPG game [Hordes.io](https://hordes.io).

## Features
- Player stat and item visualisation
- Track player statistics
- UI extension to provide various QOL features: Skill Presets, CC indicator, Chat modification, Additional character panel stats
- Boss fight simulation / data analysis
- Real time item scanner

## Implementation
Users would interact with these tools via the three projects contained in this repo:
- ScoutWeb: Web application developed with [Vue.js](https://vuejs.org/) and [Express.js](https://expressjs.com/), using a [MongoDB](https://www.mongodb.com/) database
- ScoutUI: Custom game UI written in javacript and implemented as a userscript via a browser [userscript manager](https://www.tampermonkey.net/)
- ScoutBH: Discord bot developed via python and the [discord.py](https://github.com/Rapptz/discord.py) library
