# Based on the thing class
from src.thing import Thing

class Location(Thing):
    def __init__(self, name, type="location", description="", private_description="",physical_state="", contents={}, parent=None, exits={}):
        super().__init__(name, type, description, private_description, physical_state, contents, parent)
        self.exits = exits