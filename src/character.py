# Based on the thing class
from thing import thing

class character(thing):
    def __init__(self, name, type="character", description="", physical_state="", contents=[], parent=None, psychological_state="", backstory="", current_context="", relationships={}):
        super().__init__(name, type, description, physical_state, contents, parent)
        self.psychological_state = psychological_state
        self.backstory = backstory
        self.current_context = current_context
        self.relationships = relationships

    def change_psychological_state(self, new_state):
        self.physical_state = new_state

    def add_to_context(self, new_context):
        self.current_context += "\n" + new_context

    def change_relationship(self, character_name, relationship):
        self.relationships[character_name] = relationship

    def __str__(self):
        return self.description