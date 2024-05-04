class thing:
    def __init__(self, name, type="thing", description="", physical_state="", contents=[], parent=None):
        self.name = name
        self.type = type
        self.description = description
        self.physical_state = physical_state
        self.contents = contents
        self.parent = parent

    def change_state(self, new_state):
        self.physical_state = new_state

    # Change the location of the thing
    def change_parent(self, new_parent):
        if self.parent is not None:
            self.parent.contents.remove(self)
        new_parent.contents.append(self)
        self.parent = new_parent

    def change_description(self, new_description):
        self.description = new_description

    def get_full_location(self):
        if self.parent is None:
            return self.name + " is in the world." # We shouldn't need to ask where the top level thing is, it's just in the world
        else:
            return self.get_partial_location()

    def get_partial_location(self):
        location_fragment = self.name
        if self.parent is None:
            return location_fragment

        if self.type == "character":
            location_fragment += ", who is "
        else:
            location_fragment += ", which is "

        if self.parent.type == "character":
            location_fragment += "in the inventory of "
        else:
            location_fragment += "in "

        return location_fragment + self.parent.get_partial_location()
        
        
                
            

    def __str__(self):
        return self.description