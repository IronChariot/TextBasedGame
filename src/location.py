# Based on the thing class
from thing import thing

class location(thing):
    def __init__(self, name, type="location", description="", physical_state="", contents=[], parent=None, exits=[]):
        super().__init__(name, type, description, physical_state, contents, parent)
        self.exits = exits

    def __str__(self):
        return self.description