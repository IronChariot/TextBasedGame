# A class which allows the world AI to query the world, feed text back to the player or other characters, or change the state of the world
# and also where text from the player or characters gets processed by the AI

from consoleui import ConsoleUI
from world import World
from character import Character

class AIConsole:
    def __init__(self, consoleui: ConsoleUI, world: World):
        self.world = world
        self.consoleui = consoleui

    def process_player_input(self, input, player_character: Character):
        # The prompt for the world AI, when the player types in a command, should be:
        # 1. the player's context so far (all the text shown to the player so far)
        # 2. some instructions, which mention the player's inputs
        player_character_context = player_character.current_context
        print(player_character_context)
        prompt = """

"""

    def process_command(self, command: str):
        # This is text output by the AI, in order to do something in the world
        pass