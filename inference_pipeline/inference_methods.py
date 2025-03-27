from inference_pipeline import dep
"""
This module defines the dndCharacter class, which is used to create and manage a Dungeons and Dragons character.
Classes:
    dndCharacter: A class to create and manage a Dungeons and Dragons character.
Methods:
    __init__(): Initializes the dndCharacter class with dependencies, abilities, skills, and connects to MongoDB.
    ability_scores(): Generates and returns sorted ability scores for the character.
    get_abilities(class_name, class_context): Retrieves abilities for a given class name and context.
    assign_scores(class_abilities): Assigns ability scores based on class abilities.
    get_race(): Randomly selects and returns a race from the database.
    get_class(): Randomly selects and returns a class from the database.
    get_background(): Randomly selects and returns a background from the database.
    get_class_context(class_name): Retrieves and returns context for a given class name.
    get_race_context(race_name): Retrieves and returns context for a given race name.
    get_background_context(background_name): Retrieves and returns context for a given background name.
    ability_modifier(ability_scores): Calculates and returns ability modifiers based on ability scores.
    proficiency_modifier(): Returns the proficiency modifier.
    saving_throws(class_name, class_context, ability_scores, proficiency_modifier): Calculates and returns saving throw scores.
    get_skills(class_name, background_name, class_context, background_context, ability_scores, proficiency_modifier): Calculates and returns skill scores.
    get_passive_perception(perception): Calculates and returns passive perception.
    get_proficiencies_languages(class_name, background_name, class_context, background_context): Retrieves and returns proficiencies and languages.
    get_equipment_money(class_name, background_name, class_context, background_context): Retrieves and returns equipment and money.
    get_attacks_damage(weapons, dexterity_modifier, strength_modifier, proficiency_modifier): Calculates and returns attack and damage information.
    get_armor_class(armor, dexterity_modifier): Calculates and returns armor class.
    get_speed(race_name, race_context): Retrieves and returns speed based on race.
    get_hit_dice(class_name, class_context): Retrieves and returns hit dice based on class.
    get_point_maximun(hit_dice, constitution_modifier): Calculates and returns maximum hit points.
    get_features(class_name, class_context, background_name, background_context, race_name, race_context): Retrieves and returns features.
    get_traits(class_name, class_context, background_name, background_context, race_name, race_context): Retrieves and returns traits.
    get_character_name(class_name, class_context, background_name, background_context, race_name, race_context): Retrieves and returns character name.
    alignment(traits): Determines and returns alignment based on traits.
"""
import re
import random
import pandas as pd
from training_pipeline import ask_llm

class dndCharacter():
    def __init__(self, mongo_client):
        self.client = mongo_client
        self.dep = dep.dependencies()
        self.ask = ask_llm.askLLM()
        self.abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        self.ability_skills = {"dexterity": ["Acrobatics", "Sleight of Hand", "Stealth"], 
                           "intelligence": ["Arcana", "History", "Investigation", "Nature", "Religion"], 
                           "wisdom": ["Animal Handling", "Insight", "Medicine", "Perception", "Survival"], 
                           "charisma": ["Deception", "Intimidation", "Performance", "Persuasion"], 
                           "strength": ["Athletics"], 
                           "constitution": [] }
        self.skills = ["Acrobatics", "Sleight of Hand", "Stealth", "Arcana", "History", "Investigation", "Nature", "Religion",
                       "Animal Handling", "Insight", "Medicine", "Perception", "Survival", "Deception", "Intimidation", "Performance", "Persuasion",
                       "Athletics"]

    def ability_scores(self):
        """
        Generate and return sorted ability scores for a character.

        This method generates six raw ability scores by rolling six dice and dropping the lowest roll for each score.
        The scores are then sorted in descending order and returned as a list.

        Returns:
            list: A list of six sorted ability scores in descending order.
        """
        raw_scores = [self.dep.drop_low_sum(6, 4) for _ in range(6)]
        sorted_raw_scores = sorted(raw_scores, reverse=True)
        return sorted_raw_scores
    
    def get_abilities(self, class_name, class_context):
        """
        Retrieve abilities for a given class.

        Args:
            class_name (str): The name of the class for which abilities are being retrieved.
            class_context (dict): Additional context or parameters related to the class.

        Returns:
            list: A list of abilities associated with the specified class.
        """
        class_abilities = self.ask.get_abilities(class_name, class_context)
        return class_abilities
    
    def assign_scores(self, class_abilities):
        """
        Assigns ability scores to character attributes based on class abilities.

        This method matches the character's abilities with the given class abilities
        and assigns scores to them. Attributes that do not match are shuffled and 
        assigned scores randomly.

        Args:
            class_abilities (str): A string containing the class abilities.

        Returns:
            dict: A dictionary where keys are attributes and values are assigned scores.
        """
        matches = [attr for attr in self.abilities if re.search(rf'\b{attr}\b', class_abilities, re.IGNORECASE)]
        non_matches = [attr for attr in self.abilities if attr not in matches]
        random.shuffle(non_matches)
        scores = self.ability_scores()
        assigned_scores = {
            attr: scores[i] for i, attr in enumerate(matches + non_matches)
        }
        return assigned_scores
    
    def get_race(self):
        """
        Retrieves a random race from the available races in the context collection.

        This method accesses the context collection for races using the dependency
        injection pattern, retrieves all distinct race names, and returns a randomly
        selected race.

        Returns:
            str: A randomly selected race name.
        """
        collection = self.dep.get_context_collection(self.client, "races")
        races = self.dep.get_distinct_names(collection)
        current_choice = random.choice(races)
        return current_choice
    
    def get_class(self):
        """
        Retrieves a random class name from the "classes" collection.

        This method fetches the "classes" collection using the provided client,
        retrieves a list of distinct class names from the collection, and returns
        a randomly selected class name from the list.

        Returns:
            str: A randomly selected class name.
        """
        collection = self.dep.get_context_collection(self.client, "classes")
        classes = self.dep.get_distinct_names(collection)
        current_choice = random.choice(classes)
        return current_choice
    
    def get_background(self):
        """
        Retrieve a random background from the context collection.

        This method fetches the collection of backgrounds from the context,
        retrieves all distinct background names, and returns a randomly
        selected background.

        Returns:
            str: A randomly selected background name.
        """
        collection = self.dep.get_context_collection(self.client, "backgrounds")
        backgrounds = self.dep.get_distinct_names(collection)
        current_choice = random.choice(backgrounds)
        return current_choice

    def get_class_context(self, class_name):
        """
        Retrieves the context information for a given class name.

        Args:
            class_name (str): The name of the class to retrieve context for.

        Returns:
            dict: A dictionary containing the context information for the specified class.
        """
        class_context = self.ask.extract_context("classes", class_name)
        return class_context

    def get_race_context(self, race_name):
        """
        Retrieve the context information for a given race.

        Args:
            race_name (str): The name of the race for which context information is to be retrieved.

        Returns:
            dict: A dictionary containing the context information for the specified race.
        """
        race_context = self.ask.extract_context("races", race_name)
        return race_context

    def get_background_context(self, background_name):
        """
        Retrieve the context information for a given background.

        Args:
            background_name (str): The name of the background to retrieve context for.

        Returns:
            dict: A dictionary containing the context information for the specified background.
        """
        background_context = self.ask.extract_context("backgrounds", background_name)
        return background_context
    
    def ability_modifier(self, ability_scores):
        """
        Calculate the ability modifiers for a given set of ability scores.

        Args:
            ability_scores (dict): A dictionary containing the ability scores with keys 
                                   'strength', 'dexterity', 'constitution', 'intelligence', 
                                   'wisdom', and 'charisma'.

        Returns:
            dict: A dictionary containing the ability modifiers for each ability score.
        """
        ability_modifier = {}
        ability_modifier['strength'] = self.dep.get_ability_modifier(ability_scores["strength"])
        ability_modifier['dexterity'] = self.dep.get_ability_modifier(ability_scores["dexterity"])
        ability_modifier['constitution'] = self.dep.get_ability_modifier(ability_scores["constitution"])
        ability_modifier['intelligence'] = self.dep.get_ability_modifier(ability_scores["intelligence"])
        ability_modifier['wisdom'] = self.dep.get_ability_modifier(ability_scores["wisdom"])
        ability_modifier['charisma'] = self.dep.get_ability_modifier(ability_scores["charisma"])
        return ability_modifier
    
    def proficiency_modifier(self):
        """
        Calculate and return the proficiency modifier.

        Returns:
            dict: A dictionary containing the proficiency modifier with the key 'proficiency_modifier'.
        """
        proficiency = {"proficiency_modifier": 2}
        return proficiency
    
    def saving_throws(self, class_name, class_context, ability_scores, proficiency_modifier):
        """
        Calculate the saving throw scores for a character based on their class, ability scores, and proficiency modifier.

        Args:
            class_name (str): The name of the character's class.
            class_context (str): Additional context or subclass information for the character's class.
            ability_scores (dict): A dictionary containing the character's ability scores, where keys are ability names and values are the scores.
            proficiency_modifier (int): The proficiency modifier to be added to the saving throws for the class-specific abilities.

        Returns:
            dict: A dictionary containing the saving throw scores for each ability, where keys are ability names and values are the calculated saving throw scores.
        """
        saving_throws_scores = {}
        class_saving_throws = self.ask.get_saving_throws(class_name, class_context)
        matches = [attr for attr in self.abilities if re.search(rf'\b{attr}\b', class_saving_throws, re.IGNORECASE)]
        non_matches = [attr for attr in self.abilities if attr not in matches]
        for match in matches:
            saving_throws_scores[match] = ability_scores[match] + proficiency_modifier
        for non_match in non_matches:
            saving_throws_scores[non_match] = ability_scores[non_match]
        return saving_throws_scores
    
    def get_skills(self, class_name, background_name, class_context, background_context, ability_scores, proficiency_modifier):
        """
        Calculate skill scores based on class, background, ability scores, and proficiency modifier.

        Args:
            class_name (str): The name of the character's class.
            background_name (str): The name of the character's background.
            class_context (dict): Additional context or details about the class.
            background_context (dict): Additional context or details about the background.
            ability_scores (dict): A dictionary mapping ability names to their scores.
            proficiency_modifier (int): The proficiency modifier to be added to the skill scores.

        Returns:
            dict: A dictionary mapping skill names to their calculated scores.
        """
        skill_scores = {}
        class_skills = self.ask.get_skills(class_name, background_name, class_context, background_context)
        matches = [attr for attr in self.skills if re.search(rf'\b{attr}\b', class_skills, re.IGNORECASE)]
        for key, value in self.ability_skills.items():
            if any(val in value for val in matches):
                for val in value:
                    skill_scores[val] = ability_scores[key] + proficiency_modifier
            else:
                for val in value:
                    skill_scores[val] = ability_scores[key]
        return skill_scores
    
    def get_passive_perception(self, perception):
        """
        Calculate the passive perception score.

        Passive perception is calculated as 10 plus the perception modifier.

        Args:
            perception (int): The perception modifier of the character.

        Returns:
            int: The passive perception score.
        """
        passive_perception = 10 + perception
        return passive_perception
    
    def get_proficiencies_languages(self, class_name, background_name, class_context, background_context):
        """
        Retrieve the proficiencies and languages for a given class and background.

        Args:
            class_name (str): The name of the class.
            background_name (str): The name of the background.
            class_context (dict): Additional context or details related to the class.
            background_context (dict): Additional context or details related to the background.

        Returns:
            dict: A dictionary containing the proficiencies and languages.
        """
        proficiencies = self.ask.get_proficiencies_languages(class_name, background_name, class_context, background_context)
        return proficiencies
    
    def get_equipment_money(self, class_name, background_name, class_context, background_context):
        """
        Retrieves the equipment and money for a given class and background.

        Args:
            class_name (str): The name of the character's class.
            background_name (str): The name of the character's background.
            class_context (dict): Additional context or attributes related to the class.
            background_context (dict): Additional context or attributes related to the background.

        Returns:
            dict: A dictionary containing the equipment and money information.
        """
        equipment_money = self.ask.get_equipment_money(class_name, background_name, class_context, background_context)
        return equipment_money
    
    def get_attacks_damage(self, weapons, dexterity_modifier, strength_modifier, proficiency_modifier):
        """
        Calculate the attack modifiers and damage for a list of weapons.

        Args:
            weapons (list): List of weapon names.
            dexterity_modifier (int): The character's dexterity modifier.
            strength_modifier (int): The character's strength modifier.
            proficiency_modifier (int): The character's proficiency modifier.

        Returns:
            list: A list of dictionaries, each containing:
                - weapon (str): The name of the weapon.
                - attack_modifier (int): The calculated attack modifier for the weapon.
                - damage (str or None): The calculated damage string for the weapon, or None if damage is not applicable.
        """
        attacks = []
        weapons_df = self.dep.character_weapons(self.client, weapons)
        for i in range(len(weapons_df)):
            weapon = weapons_df.iloc[i]["weapon_name"]
            damage = weapons_df.iloc[i]["damage"]
            weapon_type = weapons_df.iloc[i]["weapons_type"]
            property = weapons_df.iloc[i]["properties"]
            attack_modifier = self.dep.calculate_attack_modifier(weapon_type, dexterity_modifier, strength_modifier, proficiency_modifier, property)
            if pd.isna(damage):
                attacks.append({"weapon": weapon, "attack_modifier": attack_modifier, "damage": None})
                continue
            damage = damage.split(" ")
            damage_score = self.dep.calculate_damage(dexterity_modifier, strength_modifier, weapon_type, property)
            damage = damage[0] + " " + str(damage_score) + " " + damage[1]
            attacks.append({"weapon": weapon, "attack_modifier": attack_modifier, "damage": damage})
        return attacks
    
    def get_armor_class(self, armor, dexterity_modifier):
        """
        Calculate the armor class (AC) for a character based on their armor and dexterity modifier.

        Parameters:
        armor (str): The name of the armor worn by the character. If None, the character is considered unarmored.
        dexterity_modifier (int): The character's dexterity modifier.

        Returns:
        int: The calculated armor class (AC) for the character.

        Notes:
        - If the character is unarmored, the base AC is 10 plus the dexterity modifier.
        - For light armor, the AC is the armor's base AC plus the full dexterity modifier.
        - For medium armor, the AC is the armor's base AC plus the dexterity modifier, up to a maximum of 2.
        - For heavy armor, the AC is the armor's base AC without any dexterity modifier.
        """
        if not armor:
            return 10 + dexterity_modifier
        armor_df = self.dep.character_armor(self.client, armor)
        armor_type = armor_df.iloc[0]["armor_type"]
        armor_class = int(armor_df.iloc[0]["armor_class"][:2])
        if armor_type == 'light':
            return armor_class + dexterity_modifier
        elif armor_type == 'medium':
            return armor_class + min(dexterity_modifier, 2)
        elif armor_type == 'heavy':
            return armor_class

    def get_speed(self, race_name, race_context):
        """
        Retrieve the speed attribute for a given race.

        Args:
            race_name (str): The name of the race.
            race_context (dict): Additional context or attributes related to the race.

        Returns:
            int: The speed value associated with the specified race.
        """
        speed = self.ask.get_speed(race_name, race_context)
        return speed
    
    def get_hit_dice(self, class_name, class_context):
        """
        Retrieve the hit dice for a given class in a specific context.

        Args:
            class_name (str): The name of the class for which to retrieve the hit dice.
            class_context (dict): The context or additional information related to the class.

        Returns:
            int: The hit dice value for the specified class and context.
        """
        hit_dice = self.ask.get_hit_dice(class_name, class_context)
        return hit_dice
    
    def get_point_maximun(self, hit_dice, constitution_modifier):
        """
        Calculate the maximum hit points based on hit dice and constitution modifier.

        Args:
            hit_dice (str): The hit dice string (e.g., "1d8", "2d6").
            constitution_modifier (int): The constitution modifier to be added to the hit dice.

        Returns:
            int: The maximum hit points if the hit dice is valid.
            bool: False if the hit dice is not valid.
        """
        if self.dep.validate_hit_dice(hit_dice):
           return int(hit_dice[2:]) + constitution_modifier
        else:
            return False

    def get_features(self, class_name, class_context, background_name, background_context, race_name, race_context):
        """
        Extracts features based on the provided class, background, and race information.

        Args:
            class_name (str): The name of the class.
            class_context (str): The context or additional information related to the class.
            background_name (str): The name of the background.
            background_context (str): The context or additional information related to the background.
            race_name (str): The name of the race.
            race_context (str): The context or additional information related to the race.

        Returns:
            dict: A dictionary containing the extracted features.
        """
        features = self.ask.get_features(class_name, background_name, race_name, class_context, background_context, race_context)
        return features
    
    def get_traits(self, class_name, class_context, background_name, background_context, race_name, race_context):
        """
        Retrieve traits based on class, background, and race information.

        Args:
            class_name (str): The name of the character's class.
            class_context (str): Additional context or description for the class.
            background_name (str): The name of the character's background.
            background_context (str): Additional context or description for the background.
            race_name (str): The name of the character's race.
            race_context (str): Additional context or description for the race.

        Returns:
            dict: A dictionary containing the traits associated with the given class, background, and race.
        """
        traits = self.ask.get_traits(class_name, background_name, race_name, class_context, background_context, race_context)
        return traits
    
    def get_character_name(self, class_name, class_context, background_name, background_context, race_name, race_context):
        """
        Generates a character name based on the provided class, background, and race information.

        Args:
            class_name (str): The name of the character's class.
            class_context (str): Additional context or description for the character's class.
            background_name (str): The name of the character's background.
            background_context (str): Additional context or description for the character's background.
            race_name (str): The name of the character's race.
            race_context (str): Additional context or description for the character's race.

        Returns:
            str: The generated character name.
        """
        character_name = self.ask.get_character_name(class_name, background_name, race_name, class_context, background_context, race_context)
        return character_name
    
    def get_alignment(self, traits):
        """
        Determine the alignment based on given traits.

        Args:
            traits (dict): A dictionary containing character traits.

        Returns:
            str: The alignment of the character.
        """
        alignment = self.ask.get_alignment(traits)
        return alignment
        



    

