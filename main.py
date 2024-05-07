from src.consoleui import ConsoleUI
from src.world import World
from src.aiengine import AIEngine

# Example usage
if __name__ == "__main__":
    # First, construct all the objects from the world.yaml and scenario.yaml files.
    world = World('game1')

    # Second, construct the AI console which will feed text back to the player or other characters, or change the state of the world
    ai = AIEngine(world)
    
    # Third, construct the console UI which will allow the player to interact with the world
    ui = ConsoleUI(ai)
    ui.write_to_console(1, "Welcome to Console 1 (Player)!")
    # ui.write_to_console(2, "Welcome to Console 2 (World AI)!")
    # ui.write_to_console(3, "Welcome to Console 3 (NPC AI)!")

    # Get the player character
    player_character_name = world.scenario_state["player_character"]
    player_character = world.characters[player_character_name]

    # Feed the scenario introduction to the player's console and into their character's context
    scenario_intro = world.scenario_state["introduction"]
    ui.write_to_console(1, scenario_intro)
    player_character.add_to_context(scenario_intro)

    # room_description = # TODO: Room descriptions

    ui.run()


    