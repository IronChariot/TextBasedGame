from src.consoleui import ConsoleUI

# Example usage
if __name__ == "__main__":
    ui = ConsoleUI()
    ui.write_to_console(1, "Welcome to Console 1!")
    ui.write_to_console(2, "Welcome to Console 2!")
    ui.write_to_console(3, "Welcome to Console 3!")
    ui.run()