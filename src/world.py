import yaml
import os
import json
import jsonpickle
from dicttoxml import dicttoxml
from src.thing import Thing
from src.location import Location
from src.character import Character
from dicttoxml import dicttoxml
import re

class World:
    def __init__(self, scenario_folder):
        self.items = {}
        self.locations = {}
        self.characters = {}
        self.world_state = None
        self.scenario_state = None

        # Get the files for the world and scenario from the scenario folder
        world_file_path = os.path.join(os.getcwd(), 'assets', scenario_folder, 'world.yaml')
        scenario_file_path = os.path.join(os.getcwd(), 'assets', scenario_folder, 'scenario.yaml')

        # Load the YAML data
        self.world_state = self.load_world_yaml_data(world_file_path)
        self.scenario_state = self.load_scenario_yaml_data(scenario_file_path)

    def create_object(self, data, parent=None):
        if isinstance(data, dict):
            obj_type = data.get('type', 'thing')
            if obj_type == 'location':
                obj = Location(
                    name=data['name'],
                    description=data.get('description', ''),
                    private_description=data.get('private_description', ''),
                    physical_state=data.get('physical_state', ''),
                    exits=data.get('exits', {}),
                    parent=parent,
                    contents={}
                )
            elif obj_type == 'character':
                obj = Character(
                    name=data['name'],
                    description=data.get('description', ''),
                    physical_state=data.get('physical_state', ''),
                    private_description=data.get('private_description', ''),
                    psychological_state=data.get('psychological_state', ''),
                    backstory=data.get('backstory', ''),
                    current_context=data.get('current_context', ''),
                    relationships=data.get('relationships', {}),
                    parent=parent,
                    contents={}
                )
            else:
                obj = Thing(
                    name=data['name'],
                    type=obj_type,
                    description=data.get('description', ''),
                    private_description=data.get('private_description', ''),
                    physical_state=data.get('physical_state', ''),
                    parent=parent,
                    contents={}
                )

            contents = data.get('contents', {})
            for content_data in contents:
                content_obj = self.create_object(content_data, parent=obj)
                obj.contents[content_obj.name] = content_obj

            # Store the object in the appropriate dictionary as well
            if obj_type == 'location':
                self.locations[obj.name] = obj
            elif obj_type == 'character':
                self.characters[obj.name] = obj
            else:
                self.items[obj.name] = obj

            return obj
        else:
            raise ValueError(f"Invalid data type: {type(data)}")

    def load_world_yaml_data(self, file_path):
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
        # Assume there is just one root object
        root_object = self.create_object(data[0])
        return root_object
    
    def load_scenario_yaml_data(self, file_path):
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
        return data["player_scenario"]

    def get_item_names(self):
        return list(self.items.keys())
    
    def get_location_names(self):
        return list(self.locations.keys())
    
    def get_character_names(self):
        return list(self.characters.keys())
    
    def update_thing_private_description(self, thing_name, thing_description):
        # First, find the thing in the world - it'll either be in the items, locations, or characters dictionaries
        thing = None
        if thing_name in self.items:
            thing = self.items[thing_name]
        elif thing_name in self.locations:
            thing = self.locations[thing_name]
        elif thing_name in self.characters:
            thing = self.characters[thing_name]

        # Update the private_description of the thing
        thing.private_description += thing_description

    def create_thing(self, location_name, thing_name, thing_description):
        # First, find the location in the world - it'll either be in the items, locations, or characters dictionaries
        location = None
        if location_name in self.items:
            location = self.items[location_name]
        elif location_name in self.locations:
            location = self.locations[location_name]
        elif location_name in self.characters:
            location = self.characters[location_name]

        # Create the thing in its parent's contents, and also store it in the items dictionary
        location.contents[thing_name] = Thing(thing_name, description=thing_description, parent=location)
        self.items[thing_name] = location.contents[thing_name]
    
    def __str__(self):
        world_json = jsonpickle.encode(self.world_state)
        world_json = world_json.replace('"py/object": "src.thing.Thing", ', "")
        world_json = world_json.replace('"py/object": "src.thing.Location", ', "")
        world_json = world_json.replace('"py/object": "src.thing.Character", ', "")
        world_dict = json.loads(world_json)
        world_xml = dicttoxml(world_dict, custom_root="world", xml_declaration=False, attr_type=False, include_encoding=False, ids=False)
        
        world_xml_str = str(world_xml)
        # Use regex to remove all <parent></parent> blocks (and the content in between them):
        world_xml_str = re.sub(r'<parent>.*?</parent>', '', world_xml_str, flags=re.DOTALL) # TODO: Check that this doesn't remove too much
        # Remove the b' at the start of the string
        world_xml_str = world_xml_str[2:]
        # Remove the last ' at the end of the string
        world_xml_str = world_xml_str[:-1]
        # Replace all &apos; with '
        world_xml_str = world_xml_str.replace("&apos;", "'")

        return world_xml_str
    
if __name__ == "__main__":
    world = World('game1')
    print(world)