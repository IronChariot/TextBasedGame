from src.consoleui import ConsoleUI
from src.world import World
from src.aiconsole import AIConsole

# Example usage
if __name__ == "__main__":
    ui = ConsoleUI()
    ui.write_to_console(1, "Welcome to Console 1 (Player)!")
    ui.write_to_console(2, "Welcome to Console 2 (World AI)!")
    ui.write_to_console(3, "Welcome to Console 3 (NPC AI)!")
    ui.run()

    # First, construct all the objects from the world.yaml and scenario.yaml files.
    world = World('game1')

    # Second, construct the AI console which will feed text back to the player or other characters, or change the state of the world
    ai = AIConsole(ui, world)
    ui.set_ai_console(ai)

    # Get the player character
    player_character_name = world.scenario_state["player_character"]
    player_character = world.characters[player_character_name]
    # quick test:
    player_character_context = player_character.current_context
    print(player_character_context)

    # Feed the scenario introduction to the player's console and into their character's context
    scenario_intro = world.scenario_state["introduction"]
    ui.write_to_console(1, scenario_intro)
    