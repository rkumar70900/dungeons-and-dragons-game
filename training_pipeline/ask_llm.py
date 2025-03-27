import marqo
"""
This module provides a class `askLLM` that interacts with the OpenAI API and Marqo for generating various character attributes for a Dungeons and Dragons game.
Classes:
    askLLM: A class that provides methods to interact with the OpenAI API and Marqo to generate character attributes.
Methods:
    __init__():
        Initializes the askLLM class with OpenAI and Marqo clients, and sets retry parameters.
    extract_context(about, name):
        Extracts context information about a given name from a specified index in Marqo.
    add_brackets(string):
        Adds curly brackets around a string if they are not already present.
    clean_response(response):
        Cleans the response from the OpenAI API by removing unnecessary characters and adding brackets.
    _retry_request(func, *args, **kwargs):
        Retries a function call multiple times if it fails to return a valid JSON response.
    get_abilities(class_name, class_context, model="gpt-3.5-turbo"):
        Retrieves the abilities of a character based on the class name and context.
    get_saving_throws(class_name, class_context, model="gpt-3.5-turbo"):
        Retrieves the saving throws of a character based on the class name and context.
    get_skills(class_name, background_name, class_context, background_context, model="gpt-3.5-turbo"):
        Retrieves the skills of a character based on the class and background names and contexts.
    get_proficiencies_languages(class_name, background_name, class_context, background_context, model="gpt-3.5-turbo"):
        Retrieves the proficiencies and languages of a character based on the class and background names and contexts.
    get_equipment_money(class_name, background_name, class_context, background_context, model="gpt-3.5-turbo"):
        Retrieves the equipment and money of a character based on the class and background names and contexts.
    get_speed(race_name, race_context, model="gpt-3.5-turbo"):
        Retrieves the speed of a character based on the race name and context.
    get_hit_dice(class_name, class_context, model="gpt-3.5-turbo"):
        Retrieves the hit dice of a character based on the class name and context.
    get_features(class_name, background_name, race_name, class_context, background_context, race_context, model="gpt-3.5-turbo"):
        Retrieves the features of a character based on the class, background, and race names and contexts.
    get_traits(class_name, background_name, race_name, class_context, background_context, race_context, model="gpt-3.5-turbo"):
        Retrieves the traits of a character based on the class, background, and race names and contexts.
    get_character_name(class_name, background_name, race_name, class_context, background_context, race_context, model="gpt-3.5-turbo"):
        Generates a unique name for a character based on the class, background, and race names and contexts.
    get_alignment(traits, model="gpt-3.5-turbo"):
        Determines the alignment of a character based on their traits.
"""
from openai import OpenAI
import json
import time

class askLLM():
    def __init__(self):
        self.mq_client = marqo.Client(url='http://localhost:8882')
        self.client = OpenAI(api_key="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")
        self.max_retries = 5
        self.retry_delay = 2

    def extract_context(self, about, name):
        """
        Extracts context information about a given name from a specified index.
        Args:
            about (str): The index to search within.
            name (str): The name to search for information about.
        Returns:
            str: A string containing the concatenated content of the search hits.
        """

        classes = self.mq_client.index(about).search(
            q=f"information about {name}", search_method='LEXICAL', limit=1
        )

        context = " ".join(hit["content"] for hit in classes.get("hits", []))

        return context
    
    def add_brackets(self, string):
        """
        Adds curly brackets around a given string if they are not already present.

        Args:
            string (str): The input string to be modified.

        Returns:
            str: The modified string with curly brackets added if they were not already present.
        """
        string = string.strip()
        if string[0] != '{' and string != '}':
            return "{" + string + "}"
        return string
    
    def clean_response(self, response):
        """
        Cleans and formats the response from the language model.

        This method processes the response by removing specific markdown formatting
        and newlines, then adds brackets to the cleaned response.

        Args:
            response (object): The response object from the language model, expected
                               to have a 'choices' attribute with a list containing
                               a 'message' attribute that has 'content'.

        Returns:
            str: The cleaned and formatted response string.
        """
        response = (response.choices[0].message.content).replace("```json", "").replace("```", "").replace('\n', '')
        response = self.add_brackets(response)
        return response
    
    def _retry_request(self, func, *args, **kwargs):
        """
        Attempts to execute a function that makes a request, retrying if it fails to return a valid JSON response.

        Args:
            func (callable): The function to execute, which should return a JSON response.
            *args: Variable length argument list to pass to the function.
            **kwargs: Arbitrary keyword arguments to pass to the function.

        Returns:
            dict: The JSON response parsed into a dictionary.

        Raises:
            ValueError: If the function fails to return a valid JSON response after the maximum number of retries.
        """
        retries = 0
        while retries < self.max_retries:
            try:
                response = func(*args, **kwargs)
                return json.loads(response)
            except (json.JSONDecodeError, KeyError):
                retries += 1
                time.sleep(self.retry_delay)
        raise ValueError("Failed to get a valid JSON response after multiple retries")

    def get_abilities(self, class_name, class_context, model="gpt-3.5-turbo"):
        """
        Retrieves the two primary abilities for a character based on their class.
        Args:
            class_name (str): The name of the character's class.
            class_context (str): Additional context or description of the class.
            model (str, optional): The model to use for generating the response. Defaults to "gpt-3.5-turbo".
        Returns:
            str: The names of the two primary abilities for the character.
        """

        user_query = f'which two abilities out of strength, dexterity, constitution, \
                        intelligence, wisdom and charisma does the character belonging \
                        to {class_name} have. do your thinking and give me only the ability names.'
        
        messages = [
            {"role": "system", "content": "You are a creative assistant, well versed in mythology and writes amazing stories."},
            {"role": "user", "content": f"class_context: {class_context}"},
            {"role": "user", "content": f"Question: {user_query}"}
        ]
        
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7
        )
        
        response = str(response.choices[0].message.content).replace("```json", "").replace("```", "")
        return response
    
    def get_saving_throws(self, class_name, class_context, model="gpt-3.5-turbo"):
        """
        Retrieves the saving throw abilities for a given character class using an AI model.
        Args:
            class_name (str): The name of the character class (e.g., "wizard", "fighter").
            class_context (str): Additional context or description of the character class.
            model (str, optional): The AI model to use for generating the response. Defaults to "gpt-3.5-turbo".
        Returns:
            str: The names of the two abilities that the character class has for saving throws.
        """

        user_query = f'which two abilities out of strength, dexterity, constitution, \
                        intelligence, wisdom and charisma does the character belonging \
                        to {class_name} have for saving throws. do your thinking and give me only the ability names.'
        
        messages = [
            {"role": "system", "content": "You are a creative assistant, well versed in mythology and writes amazing stories."},
            {"role": "user", "content": f"class_context: {class_context}"},
            {"role": "user", "content": f"Question: {user_query}"}
        ]
        
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7
        )
        
        response = str(response.choices[0].message.content).replace("```json", "").replace("```", "")
        return response
    
    def get_skills(self, class_name, background_name, class_context, background_context, model="gpt-3.5-turbo"):
        """
        Retrieves the skills for a character based on their class and background using a language model.
        Args:
            class_name (str): The name of the character's class.
            background_name (str): The name of the character's background.
            class_context (str): Additional context or description for the character's class.
            background_context (str): Additional context or description for the character's background.
            model (str, optional): The language model to use for generating the response. Defaults to "gpt-3.5-turbo".
        Returns:
            str: A string containing the skill names that the character possesses.
        """

        user_query = f'which skills out of actrobatics, animal handling, arcana, athletics, \
                        deception, history, insight, intimidation, investigation, medicine, \
                        nature, perception, performance, persuasion, religion, sleight of hand, \
                        stealth, survival does the character belonging \
                        to {class_name} and {background_name} have. do your thinking and give me only the skill names.'
        
        messages = [
            {"role": "system", "content": "You are a creative assistant, well versed in mythology and writes amazing stories."},
            {"role": "user", "content": f"class_context: {class_context}"},
            {"role": "user", "content": f"background_context: {background_context}"},
            {"role": "user", "content": f"Question: {user_query}"}
        ]
        
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7
        )
        
        response = str(response.choices[0].message.content).replace("```json", "").replace("```", "")
        return response

    def get_proficiencies_languages(self, class_name, background_name, class_context, background_context, model="gpt-3.5-turbo"):
        """
        Retrieves the proficiencies and languages for a character based on their class and background.
        Args:
            class_name (str): The name of the character's class.
            background_name (str): The name of the character's background.
            class_context (str): Contextual information about the character's class.
            background_context (str): Contextual information about the character's background.
            model (str, optional): The model to use for generating the response. Defaults to "gpt-3.5-turbo".
        Returns:
            dict: A dictionary containing lists of proficiencies and languages, as well as bonuses for specific items.
        """

        user_query = f'which armor, weapons, kits, instruments, languages does the character belonging \
                        to {class_name} and {background_name} have. Consider both the class and background and give me only one list. \
                             Along with this, for every armor, weapon name (not the type), kit and instrument give me a bonus associated with them when used in the game \
                             do your thinking before answering. do not get confused between these categories. items from category should not be another. \
                            I need the output in a json formatted string in this way \
                                "armor": [list here], "weapons": [list here], "kits": [list here], "instruments": [list here], "languages": [list here], \
                                    "bonus": item_name: bonus_value'
        
        messages = [
            {"role": "system", "content": "You are a creative assistant, well versed in mythology and writes amazing stories."},
            {"role": "user", "content": f"class_context: {class_context}"},
            {"role": "user", "content": f"background_context: {background_context}"},
            {"role": "user", "content": f"Question: {user_query}"}
        ]
        
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7
        )        
        response = self.clean_response(response)
        return self._retry_request(lambda: response)
    
    def get_equipment_money(self, class_name, background_name, class_context, background_context, model="gpt-3.5-turbo"):
        """
        Retrieves the equipment and starting money for a character based on their class and background.
        Args:
            class_name (str): The name of the character's class.
            background_name (str): The name of the character's background.
            class_context (str): Contextual information about the character's class.
            background_context (str): Contextual information about the character's background.
            model (str, optional): The model to use for generating the response. Defaults to "gpt-3.5-turbo".
        Returns:
            dict: A dictionary containing the equipment list and starting money in JSON format.
        """

        user_query = f'which equipment does the character belonging to {class_name} and {background_name} have. \
                        Consider both the class and background and give me only one list. \
                        The class will have a list of starting items and the background contains some additional items. \
                            The class contains the starting wealth for the character.\
                                Give me the output in a json formatted string in this way \
                                    "equipment": [list here], "money": amount here'
        
        messages = [
            {"role": "system", "content": "You are a creative assistant, well versed in mythology and writes amazing stories."},
            {"role": "user", "content": f"class_context: {class_context}"},
            {"role": "user", "content": f"background_context: {background_context}"},
            {"role": "user", "content": f"Question: {user_query}"}
        ]
        
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7
        )
        response = self.clean_response(response)
        return self._retry_request(lambda: response)
    
    def get_speed(self, race_name, race_context, model="gpt-3.5-turbo"):
        """
        Retrieves the speed value for a character of a given race using a language model.
        Args:
            race_name (str): The name of the race for which the speed is being queried.
            race_context (str): Additional context or description about the race.
            model (str, optional): The language model to use for generating the response. Defaults to "gpt-3.5-turbo".
        Returns:
            dict: A dictionary containing the speed value in the format {"speed": <speed_value>}.
        """

        user_query = f'I need the speed for the character belonging to {race_name}. \
                        Speed means how far the character can move with a single movement. do your thinking before answering. \
                            and give me only the speed value in JSON formatted string this way \
                            "speed": <speed_value>'
        
        messages = [
            {"role": "system", "content": "You are a creative assistant, well versed in mythology and writes amazing stories."},
            {"role": "user", "content": f"race_context: {race_context}"},
            {"role": "user", "content": f"Question: {user_query}"}
        ]
        
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7
        )
        response = self.clean_response(response)
        return self._retry_request(lambda: response)
    
    def get_hit_dice(self, class_name, class_context, model="gpt-3.5-turbo"):
        """
        Retrieves the hit dice value for a character based on their class name and context using a language model.
        Args:
            class_name (str): The name of the character's class.
            class_context (str): Additional context or description of the character's class.
            model (str, optional): The language model to use for generating the response. Defaults to "gpt-3.5-turbo".
        Returns:
            str: The hit dice value in JSON formatted string.
        """

        user_query = f'I need the hit dice for the character belonging to {class_name}. \
                        Hit dice means how many times the character can be healed. do your thinking before answering. \
                            and give me only the hit dice value in JSON formatted string this way \
                            "hit_dice": <hit_dice_value>'
        
        messages = [
            {"role": "system", "content": "You are a creative assistant, well versed in mythology and writes amazing stories."},
            {"role": "user", "content": f"class_context: {class_context}"},
            {"role": "user", "content": f"Question: {user_query}"}
        ]
        
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7
        )
        response = self.clean_response(response)
        return self._retry_request(lambda: response)
    
    def get_features(self, class_name, background_name, race_name, class_context, background_context, race_context, model="gpt-3.5-turbo"):
        """
        Generates a JSON formatted string containing features of a character based on class, background, and race.
        Args:
            class_name (str): The name of the character's class.
            background_name (str): The name of the character's background.
            race_name (str): The name of the character's race.
            class_context (str): Contextual information about the character's class.
            background_context (str): Contextual information about the character's background.
            race_context (str): Contextual information about the character's race.
            model (str, optional): The model to use for generating the response. Defaults to "gpt-3.5-turbo".
        Returns:
            str: A JSON formatted string containing the features of the character.
        """

        user_query = f'The features block is a place to list all remaining features of your class, race, and background. \
                        Any additional skills, passive benefits, or relevant bonuses from background can be listed here. \
                         which features does the character belonging to {class_name}, {background_name} and \
                        {race_name} have. Consider all the three and give me only in a json format like this \
                            "feature_name": <a description of the feature> \
                            do your thinking before answering.'
        messages = [
            {"role": "system", "content": "You are a creative assistant, well versed in mythology and writes amazing stories."},
            {"role": "user", "content": f"class_context: {class_context}"},
            {"role": "user", "content": f"background_context: {background_context}"},
            {"role": "user", "content": f"race_context: {race_context}"},
            {"role": "user", "content": f"Question: {user_query}"}
        ]
        
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7
        )
        response = self.clean_response(response)
        return self._retry_request(lambda: response)
    
    def get_traits(self, class_name, background_name, race_name, class_context, background_context, race_context, model="gpt-3.5-turbo"):
        """
        Generates character traits based on the given class, background, and race contexts using a language model.
        Args:
            class_name (str): The name of the character's class.
            background_name (str): The name of the character's background.
            race_name (str): The name of the character's race.
            class_context (str): Contextual information about the character's class.
            background_context (str): Contextual information about the character's background.
            race_context (str): Contextual information about the character's race.
            model (str, optional): The language model to use for generating the traits. Defaults to "gpt-3.5-turbo".
        Returns:
            dict: A dictionary containing the character's traits in JSON format with keys:
                - "personal_traits": A description of the character's personal traits.
                - "ideals": A description of the character's ideals.
                - "bonds": A description of the character's bonds.
                - "flaws": A description of the character's flaws.
        """

        user_query = f'Traits are descriptions of your character’s personality, These traits directly feed the role-playing aspect of the role-playing game. \
                        which traits does the character belonging to {class_name}, {background_name} and \
                        {race_name}. I need four different traits for the character. \
                        Personal traits: General descriptions about your character, that help differentiate different characters from each other. \
                        Ideals: Ideals are the things that your character believes strongly in. \
                        Bonds: How your character is tied to the world of the game. Can be a person, place or event. \
                        Flaws: Flaws are the things that your character is bad at. A vice, compulsion, fear, or weakness.\
                        Do your thinking before answering. If you do not find anything, make something up for the character you think will be good. \
                              give me only one json format for the character. just consider the context. Do not use \
                              class name or background name or race name in the descriptions. just tell the character. \
                            "personal_traits": <a description of the trait>, "ideals": <a description of the trait>, \
                                "bonds": <a description of the trait>, "flaws": <a description of the trait>'
        messages = [
            {"role": "system", "content": "You are a creative assistant, well versed in mythology and writes amazing stories."},
            {"role": "user", "content": f"class_context: {class_context}"},
            {"role": "user", "content": f"background_context: {background_context}"},
            {"role": "user", "content": f"race_context: {race_context}"},
            {"role": "user", "content": f"Question: {user_query}"}
        ]
        
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7
        )
        response = self.clean_response(response)
        return self._retry_request(lambda: response)
    
    def get_character_name(self, class_name, background_name, race_name, class_context, background_context, race_context, model="gpt-3.5-turbo"):
        """
        Generates a unique fantasy name for a character based on the provided class, background, and race contexts.
        Args:
            class_name (str): The class of the character (e.g., wizard, warrior).
            background_name (str): The background of the character (e.g., noble, soldier).
            race_name (str): The race of the character (e.g., elf, dwarf).
            class_context (str): Additional context or description for the character's class.
            background_context (str): Additional context or description for the character's background.
            race_context (str): Additional context or description for the character's race.
            model (str, optional): The model to use for generating the name. Defaults to "gpt-3.5-turbo".
        Returns:
            str: A unique fantasy name for the character in JSON format.
        Raises:
            Exception: If the request to the model fails or if the response is invalid.
        """
        
        user_query = f'Give me a name for the character belonging to {class_name}, {background_name} and \
                        {race_name}. The name should be unique and should not be common. \
                        The name should be a fantasy name and should be suitable for the character. \
                        do your thinking before answering. \
                            give me only the name in a json format \
                            "name": <character name>'
        messages = [
            {"role": "system", "content": "You are a creative assistant, well versed in mythology and writes amazing stories."},
            {"role": "user", "content": f"class_context: {class_context}"},
            {"role": "user", "content": f"background_context: {background_context}"},
            {"role": "user", "content": f"race_context: {race_context}"},
            {"role": "user", "content": f"Question: {user_query}"}
        ]
        
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7
        )
        response = self.clean_response(response)
        return self._retry_request(lambda: response)
    
    def get_alignment(self, traits, model="gpt-3.5-turbo"):
        """
        Determines the alignment of a character based on their traits using a language model.
        Args:
            traits (dict): A dictionary containing the character's traits, including 'ideals', 'personal_traits', 'bonds', and 'flaws'.
            model (str, optional): The language model to use for generating the response. Defaults to "gpt-3.5-turbo".
        Returns:
            dict: A dictionary containing the alignment of the character in the format {"alignment": <alignment_value>}.
        """

        user_query = f'Alignment is your general temperament to others and the world around you. \
                        It is a combination of your personal traits, ideals, bonds, and flaws. \
                            which alignment does the character have among these \
                            "Lawful Good", "Neutral Good", "Chaotic Good", "Lawful Neutral", "True Neutral", "Chaotic Neutral", "Lawful Evil", "Neutral Evil", "Chaotic Evil" \
                                do your thinking before answering. \
                                    give me only the alignment in a json format like this \
                                    "alignment": <alignment_value>'
        messages = [
            {"role": "system", "content": "You are a creative assistant, well versed in mythology and writes amazing stories."},
            {"role": "user", "content": f"ideals: {traits['ideals']}"},
            {"role": "user", "content": f"personal_traits: {traits['personal_traits']}"},
            {"role": "user", "content": f"bonds: {traits['bonds']}"},
            {"role": "user", "content": f"flaws: {traits['flaws']}"},
            {"role": "user", "content": f"Question: {user_query}"}
        ]
        
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7
        )
        response = self.clean_response(response)
        return self._retry_request(lambda: response)