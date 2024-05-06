# TextBasedGame
Proof of concept for a simple text-based game engine that makes use of LLMs to power the world's logic and NPCs.
The idea is to describe the world, plot and characters in enough details that the LLM can respond correctly to any action taken by the player, and make the characters behave as they should in the game world. Any details not specified in the game scenario can be filled in by the LLM, but these extra details are recorded so that they stay consistent once invented.

The state of the world is controlled in three ways: by the player's actions, by other character's actions, and by the world AI. However, in the end, the world AI is the one which determines how the proposed actions from the player and other characters affect the world.

## Scenario Definition

The game setup is defined across two files, the scenario.yaml file and the world.yaml file.

### Scenario File

The scenario file contains the name of the scenario, an introduction text which will be shown to the player when the game starts, the name of the player's character, the initial location for the player, and a hidden context section which contains information the world AI will need to know to be aware of the overall situation. This file also contains a 'win condition', which describes the action the player's character will need to take to win the game.

### World File

The world file contains a tree structure of locations and things/people in those locations.
Most things (items, rooms and characters) have a name, description, and physical state. Some things have a private description, which only the world AI can see - the world AI uses this private description to give the player more information, if appropriate, when they investigate something more closely.
Most things also have 'contents', whether this is the items and characters inside a room, an item inside another, or a character's inventory.
Locations also have exits to other locations.
Characters also have a psychological state, a backstory, and a current context, which is everything they've directly experienced in the game so far.
