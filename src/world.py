import yaml
import os
from src.thing import Thing
from src.location import Location
from src.character import Character

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
        self.world_state = self.load_yaml_data(world_file_path)
        self.scenario_state = yaml.safe_load(scenario_file_path)

    def create_object(self, data, parent=None):
        global items
        global locations
        global characters

        if isinstance(data, dict):
            obj_type = data.get('type', 'thing')
            if obj_type == 'location':
                obj = Location(
                    name=data['name'],
                    description=data.get('description', ''),
                    private_description=data.get('private_description', ''),
                    physical_state=data.get('physical_state', ''),
                    exits=data.get('exits', []),
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

    def load_yaml_data(self, file_path):
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)

        # Assume there is just one root object
        root_object = self.create_object(data[0])

        return root_object

    def get_item_names(self):
        return list(self.items.keys())
    
    def get_location_names(self):
        return list(self.locations.keys())
    
    def get_character_names(self):
        return list(self.characters.keys())