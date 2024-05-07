# A class which allows the world AI to query the world, feed text back to the player or other characters, or change the state of the world
# and also where text from the player or characters gets processed by the AI

from src.world import World
from src.character import Character
from src.querymodel import chat_completion

class AIEngine:
    def __init__(self, world: World):
        self.world = world
        self.player_character = world.characters[world.scenario_state["player_character"]]
        self.system_prompt = f"""You are the Game Master or World AI for a text based adventure game. 
        You know the state of the world, including the parts that the player doesn't know about. 
        You aid the player in playing the game by allowing them to perform actions in the world, and having the world and other characters react to them appropriately.
        Follow the instructions given to you.
        Do not speak in the first person - you are not a person in this scenario, you are the world, and should only speak in the third person.
        The current game takes place in {world.world_state.description}.
        The description of the setting is as follows:
        {world.scenario_state['setting']}

        Do not divulge information from the setting to the player, only communicate with them what their character knows and observes."""

    def process_player_input(self, input):
        return self.process_character_input(input, self.player_character)

    def process_character_input(self, input, character: Character):
        # The prompt for the world AI, when the player types in a command, should be:
        # 1. the player's context so far (all the text shown to the player so far)
        # 2. some instructions, which mention the player's inputs
        instructions = f"""Above is the context of the game so far. The character (controlling the character '{character.name}') has entered the following text:
        <input>{input}</input>
        Does this text represent something the player's character is saying (for example if there are quotes, or if it is an order to say something, or a description of the player character saying something)? If it is, return the word 'speech' inside <action_type> tags in your response.
        Does this text represent a question that the player has for the world (for example, asking for clarification about the situation, or asking further details about what something looks like)? If it is, return the word 'question' inside <action_type> tags in your response.
        Does this text represent an action that the player is trying to get their character to take (for example, moving to another room, picking up an item, or interacting physically with another character)? If it is, return the word 'action' inside <action_type> tags in your response.
        Does this text represent something else which doesn't fit into the above types (for example, stating what a character other than the player character does, or nonsense text which seems inappropriate as something to type into a text based game)? If it is, return the word 'other' inside <action_type> tags in your response.)

        Think this through carefully, and after having mulled it over, return the appropriate word inside <action_type></action_type> tags in your response."""
        
        prompt = character.current_context + "\n" + instructions
        response, messages = chat_completion(prompt, system_prompt=self.system_prompt)
        # Extract the word between <action_type></action_type> tags from the response
        action_type = response.split("<action_type>")[1].split("</action_type>")[0]
        if action_type in ["speech", "question", "action"]:
            return self.process_action(action_type, input, character)
        else:
            return "Hmm, not sure what to do with that, sorry."

    # Process the action based on the action type
    # Only return text if the player will see it
    def process_action(self, type, input, character: Character):
        if type == "speech":
            instructions = f"""Above is the context of the game so far. The following is a speech action from the character '{character.name}':
            <input>{input}</input>
            The description of the character is:
            {character.private_description}
            Given the game setting, and the character speaking, write the text which describes the character speaking within <speech> tags.
            For example, if the speech action was `i tell her i'm sorry`, and the character speaking is Sherlock Holmes, then your response should be something like:
            <speech>Sherlock Holmes says, "My apologies."</speech>
            If the speech action is direct speech rather than a description of speech, then stay as close as possible to the original wording, though capitalise words as appropriate and fix any spelling errors.
            For example, if the speech action was `"hello there good sir"`, then your response should be something like:
            <speech>Sherlock Holmes says, "Hello there, good sir."</speech>

            If necessary, think through how this line should be fixed and delivered, then put your final description of the action in <speech></speech> tags."""

            prompt = character.current_context + "\n" + instructions
            response, messages = chat_completion(prompt, system_prompt=self.system_prompt)
            # Extract the text between <speech></speech> tags from the response
            speech_text = response.split("<speech>")[1].split("</speech>")[0]
            # Put the speech description into the context of every character in the room:
            characters_in_room = [thingy for thingy in character.parent.contents.values() if isinstance(thingy, Character)]
            for charact in characters_in_room:
                charact.add_to_context(speech_text)
            return speech_text

            # TODO: If the action is something loud, then we need the AI to work out who can hear it and how to describe it to them
            # TODO: Trigger other character's responses to this.

        elif type == "question":
            instructions = f"""Above is the context of the game so far. The following is a question or inspection action from the character '{character.name}':
            <input>{input}</input>
            First, establish if said character can know or see the answer to the query.
            For example, if the text is `What do I know about John Watson?`, then this is something that you can answer, using your best understanding of the context.
            As another example, if the query was `What else do I see in the room?`, this is something that the character can know as long as the room is not completely dark, and the character is not blind or otherwise unable to see the room.
            In order to know whether or not this is the case, and you do not already have the answer in your context, you may have the query the character's info or the room's info. Do this by ending your response with <query> tags surrounding the name of the thing you need to know more about, such as the name of the room or character you wish to know more about.
            You will then get a response with more information.
            If you already have enough information, or you have enough information after receiving the answer to your query, answer the character's question or inspection with a prose description of the answer within <response> tags.
            For example, if the character was Sherlock Holesm and his question was `What colour is the sofa?`, then you might think that you need to find this out from the world state, so you'd include <query>what color is the sofa in the room where Sherlock Holmes is?</query> in your response. Then, after receiving the answer ("The sofa in the living room is blue"), you'd put the answer in tags like this: <response>The sofa is blue.</response>
            
            After thinking about the character's question/inspection action, either <query> the world or give a <response>."""

            prompt = character.current_context + "\n" + instructions
            response, messages = chat_completion(prompt, system_prompt=self.system_prompt)
            times_repeated = 0
            while "<response>" not in response:
                times_repeated += 1
                # Check if the response contains <query></query> tags
                if "<query>" in response and "</query>" in response:
                    # We've got a query for the world state, get the answer
                    query_text = response.split("<query>")[1].split("</query>")[0]
                    query_response = self.query_world_state(query_text)
                    response = chat_completion(query_response, messages=messages, system_prompt=self.system_prompt)
                if times_repeated > 10:
                    break
            # Check if the response contains <response></response> tags
            if "<response>" in response and "</response>" in response:
                # We've got our answer, feed that back to the character
                response_text = response.split("<response>")[1].split("</response>")[0]
                character.add_to_context(response_text)
                return response_text

        elif type == "action":
            instructions = f"""Above is the context of the game so far. The following is a proposed action from the character '{character.name}':
            <input>{input}</input>
            First, establish if said character can perform this action. 
            You may be able to know right away from context (if the character is human, for example, the action `I fly away by flapping my arms really hard` can be rejected without much thought).
            In that case, respond with a sentence rejecting the action in <response> tags with an explanation, for example, <response>Sherlock Holmes can't do that, since he has no wings.</response>
            For actions that require an interaction with an item or another character, you may need to query the world to find out if the item or other character is at hand - do this by asking your question within <query> tags.
            For example, if the action was `I look at the chair carefully with my magnifying glass`, you may want to first query the world to see if the character has a magnifying glass, like so: <query>Does Sherlock Holmes have a magnifying glass on him?</query>.
            Once you receive a response, if it's one that would prevent the action from taking place, then respond with a sentence rejecting the action in <response> tags.
            If the response to your query affirms that the action is possible, then may require follow-up queries, such as <query>What would Sherlock Holmes observe if he looked at the chair with a magnifying glass?</query>
            Once you have enough information to know whether the action can be performed, respond with a sentence describing the action taking place, as well as the result, all within <response> tags.
            For example, <response>Sherlock Holmes takes out his trusty magnifying glass and looks at the chair carefully, noting that there is a lot of blood specifically around where the sitter's nape would be.</response>
            Think about the proposed action carefully step-by-step, and then either <query> the world, or describe the action as prose in <response> tags."""

            prompt = character.current_context + "\n" + instructions
            response, messages = chat_completion(prompt, system_prompt=self.system_prompt)
            # Make a deep copy of the messages list
            messages_copy = messages.copy()
            times_repeated = 0
            while "<response>" not in response:
                times_repeated += 1
                # Check if the response contains <query></query> tags
                if "<query>" in response and "</query>" in response:
                    # We've got a query for the world state, get the answer
                    query_text = response.split("<query>")[1].split("</query>")[0]
                    query_response = self.query_world_state(query_text)
                    response, messages_copy = chat_completion(query_response, messages=messages_copy, system_prompt=self.system_prompt)
                if times_repeated > 10:
                    break
            # Check if the response contains <response></response> tags
            if "<response>" in response and "</response>" in response:
                # We've got our answer, feed that back to the character
                action_text = response.split("<response>")[1].split("</response>")[0]

                new_instructions = f"Given the action '{action_text}', what would a description of the action be when perceived by others in the room? Respond with this new description in <response> tags."


                # Ask the AI what this would look like to others in the room:
                others_perception_response, _ = chat_completion(new_instructions, messages=messages_copy, system_prompt=self.system_prompt)
                # Extract third person perception from the <response> tags
                external_action_text = others_perception_response.split("<response>")[1].split("</response>")[0]

                # Put the speech description into the context of every character in the room:
                other_characters_in_room = [thingy for thingy in character.parent.contents.values() if isinstance(thingy, Character) and thingy != character]
                for other_character in other_characters_in_room:
                    other_character.add_to_context(external_action_text)
                character.add_to_context(action_text)
                return action_text
            else:
                return "Could not perform the action."

            # TODO: Make sure we update the state of any item or character affected directly by the action
            # TODO: If the action is something loud, then we need the AI to work out who can hear it and how to describe it to them
            # TODO: Trigger other character's responses to this.
                
    def query_world_state(self, query_text):
        instructions = f"""The above is the physical state of the game world, showing which items are in which rooms, and the full details of every item and character.
        The world AI has asked: <query>{query_text}</query>
        Using the information in the above XML, answer the query to the best of your ability. 
        If the information isn't there because it cannot have an answer, then reply saying so in <response> tags.
        For example, if the query was `Where is the cellar?` when the house is not described to have a cellar in the xml, then reply with <response>The house doesn't have a cellar.</response>
        If the information should logically exist, but isn't specified in the xml, you will need to construct a command to create the information, either by adding to the private description of an existing item, location or person, or by creating an item to put into the world state.
        Do this by using <update> tags or <create> tags. 
        In the <update> tag, use the name of the thing to update, then a colon, then the detail to add to the private description.
        In the <create> tag, use the name of the item or location which will contain the item (as defined in the xml), then a colon, then the name of the item (always with 'the' in front, unless it belongs to someone, in which case it should have the character's name with a possessive 's in front), followed by another colon, then a description.
        For example, if you had to invent the color for the kitchen floor because the query asked what color it was, you would use:
        <update>the kitchen:The color of the kitchen floor is blue.</update>
        Another example, if you had to create a lightswitch for the kitchen because the query asked if there was one (and it makes sense for there to be one), you would use:
        <create>the kitchen:the lightswitch:A light switch for the kitchen light.</create>

        To be extra clear - descriptions should be purely descriptions of items, not actions. 
        The 'location' in the <create> tag should be the name of the thing containing the new item - for example, if creating a hidden penny in the blue sofa, the response would be <create>the blue sofa:the hidden penny:A penny which was hidden in the blue sofa.</create>

        If there is nothing to update or create, or once you have done so, use a <response> tag to respond to the query with an answer, for example:
        <response>There is a lightswitch in the kitchen to control its light.</response>"""

        prompt = self.world.__str__() + "\n" + instructions

        query_response, query_messages = chat_completion(prompt, system_prompt=self.system_prompt)
        times_repeated = 0
        while True:
            times_repeated += 1
            next_message = ""
            # First, check if we have some <update> tags
            if "<update>" in query_response:
                # We have some <update> tags, so we need to update the world state
                update = query_response.split("<update>")[1].split("</update>")[0]
                update_details = update.split(":")
                assert len(update_details) == 2
                update_name = update_details[0]
                update_desc = update_details[1]
                self.world.update_thing_private_description(update_name, update_desc)
                next_message += f"Updated {update_name} to add '{update_desc}' to private_description. Don't forget to respond with a final answer to the query in <response> tags when ready.\n"

            # Next, check if we have some <create> tags
            if "<create>" in query_response:
                # We have some <create> tags, so we need to create something in the world
                create = query_response.split("<create>")[1].split("</create>")[0]
                create_details = create.split(":")
                assert len(create_details) == 3
                create_location = create_details[0]
                create_name = create_details[1]
                create_desc = create_details[2]
                self.world.create_thing(create_location, create_name, create_desc)
                next_message += f"Created {create_name} in {create_location} with description '{create_desc}'.  Don't forget to respond with a final answer to the query in <response> tags when ready.\n"

            # Finally, check if we have some <response> tags
            if "<response>" in query_response:
                query_response_text = query_response.split("<response>")[1].split("</response>")[0]
                return query_response_text
            
            if times_repeated > 10:
                break

            # If the next_message is still empty, that means there were no relevant tags in the query_response, so we should retry the last chat completion with higher temperature
            if next_message == "":
                query_response, query_messages = chat_completion(prompt, messages=[], temperature=0.7, system_prompt=self.system_prompt)
            else:
                query_response, query_messages = chat_completion(next_message, messages=query_messages, system_prompt=self.system_prompt)

        return "Could not formulate a response - reword the query, or try to do without."