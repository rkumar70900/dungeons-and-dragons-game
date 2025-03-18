import random
"""
This module provides various utility functions and classes for a Dungeons and Dragons game.
Classes:
    dependencies: A class containing methods for dice rolling, MongoDB connection, data retrieval, and game mechanics calculations.
Methods:
    __init__: Initializes the dependencies class.
    roll_dice(total_faces, number_of_dices): Rolls a specified number of dice with a given number of faces.
    drop_low_sum(total_faces, number_of_dices): Rolls dice and drops the lowest roll, then returns the sum of the remaining rolls.
    connect_mongo(): Connects to a MongoDB instance and returns the client object.
    get_context_collection(client, collection_name): Retrieves a specified collection from the MongoDB context_data database.
    get_distinct_names(collection): Retrieves distinct names from a MongoDB collection.
    get_ability_modifier(ability_score): Calculates the ability modifier based on the given ability score.
    calculate_attack_modifier(weapon_type, dexterity_modifier, strength_modifier, proficiency_modifier, property): Calculates the attack modifier based on weapon type and ability modifiers.
    calculate_damage(dexterity_modifier, strength_modifier, weapon_type, property): Calculates the damage based on weapon type and ability modifiers.
    get_data(client, collection_name): Retrieves data from a specified MongoDB collection and returns it as a pandas DataFrame.
    lower_case_list(lst): Converts all strings in a list to lowercase.
    filter_dataframe(df, weapon_list, column_name, threshold=80): Filters a DataFrame based on a list of weapon names and a similarity threshold.
    character_weapons(client, weapons): Retrieves and filters weapon data for a character, writes failed matches to a file, and returns the filtered DataFrame.
    character_armor(client, armor): Retrieves and filters armor data for a character, writes failed matches to a file, and returns the filtered DataFrame.
    validate_hit_dice(s): Validates if a string matches the hit dice pattern (e.g., '1d6', 'd20').
"""
import re
import json
from pymongo import MongoClient, errors
import pandas as pd
from thefuzz import process

class dependencies():
    def __init__(self):
        pass
    
    def roll_dice(self, total_faces, number_of_dices):
        """
        Rolls a specified number of dice with a given number of faces.

        Args:
            total_faces (int): The number of faces on each die.
            number_of_dices (int): The number of dice to roll.

        Returns:
            list: A list of integers representing the result of each die roll.
        """
        rolls = [random.randint(1, total_faces) for _ in range(number_of_dices)]
        return rolls
    
    def drop_low_sum(self, total_faces, number_of_dices):
        """
        Rolls a specified number of dice with a given number of faces, drops the lowest roll, and returns the sum of the remaining rolls.

        Args:
            total_faces (int): The number of faces on each die.
            number_of_dices (int): The number of dice to roll.

        Returns:
            int: The sum of the rolls after dropping the lowest roll.
        """
        rolls = self.roll_dice(total_faces, number_of_dices)
        rolls.remove(min(rolls))
        total = sum(rolls)
        return total
    
    def connect_mongo(self):
        """
        Connect to a MongoDB instance.

        This method attempts to establish a connection to a MongoDB server running on localhost at port 27017.
        It sets a server selection timeout of 5000 milliseconds and performs a ping command to verify the connection.

        Returns:
            MongoClient: A MongoClient instance if the connection is successful.

        Raises:
            ServerSelectionTimeoutError: If the connection to MongoDB cannot be established within the timeout period.
        """
        try:
            # Attempt connection
            client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
            # Force connection check
            client.admin.command("ping")
            print("Connected to MongoDB!")
            return client
        except errors.ServerSelectionTimeoutError as err:
            print("Error: Could not connect to MongoDB")
            print(err)
    
    def get_context_collection(self, client, collection_name):
        """
        Retrieve a specific collection from the 'context_data' database.

        Args:
            client (pymongo.MongoClient): The MongoDB client instance.
            collection_name (str): The name of the collection to retrieve.

        Returns:
            pymongo.collection.Collection: The MongoDB collection object.
        """
        db = client["context_data"]
        collection = db[collection_name]
        return collection
    
    def get_distinct_names(self, collection):
        """
        Retrieve distinct names from a given collection.

        Args:
            collection: The collection from which to retrieve distinct names. 
                        It should have a method `distinct` that accepts a field name.

        Returns:
            A list of distinct names from the specified collection.
        """
        distinct_names = collection.distinct("name")
        return distinct_names
    
    def get_ability_modifier(self, ability_score):
        """
        Calculate the ability modifier based on the given ability score.

        Args:
            ability_score (int): The ability score, which must be between 2 and 21 inclusive.

        Returns:
            int: The corresponding ability modifier.

        Raises:
            ValueError: If the ability score is not between 2 and 21.
        """
        if 2 <= ability_score <= 3:
            return -4
        elif 4 <= ability_score <= 5:
            return -3
        elif 6 <= ability_score <= 7:
            return -2
        elif 8 <= ability_score <= 9:
            return -1
        elif 10 <= ability_score <= 11:
            return 0
        elif 12 <= ability_score <= 13:
            return 1
        elif 14 <= ability_score <= 15:
            return 2
        elif 16 <= ability_score <= 17:
            return 3
        elif 18 <= ability_score <= 19:
            return 4
        elif 20 <= ability_score <= 21:
            return 5
        else:
            raise ValueError("Ability score must be between 2 and 21.")
    
    def calculate_attack_modifier(self, weapon_type, dexterity_modifier, strength_modifier, proficiency_modifier, property):
        """
        Calculate the attack modifier based on weapon type and character modifiers.

        Parameters:
        weapon_type (str): The type of weapon being used ("ranged" or "melee").
        dexterity_modifier (int): The character's dexterity modifier.
        strength_modifier (int): The character's strength modifier.
        proficiency_modifier (int): The character's proficiency modifier.
        property (str): The property of the weapon (e.g., "finesse").

        Returns:
        int: The calculated attack modifier.
        """
        if "finesse" in str(property):
            attack_modifier = max(dexterity_modifier, strength_modifier) + proficiency_modifier
            return attack_modifier
        if weapon_type == "ranged":
            attack_modifier = dexterity_modifier + proficiency_modifier
            return attack_modifier
        if weapon_type == "melee":
            attack_modifier = strength_modifier + proficiency_modifier
            return attack_modifier
    
    def calculate_damage(self, dexterity_modifier, strength_modifier, weapon_type, property):
        """
        Calculate the damage based on the given modifiers and weapon properties.

        Parameters:
        dexterity_modifier (int): The modifier for dexterity.
        strength_modifier (int): The modifier for strength.
        weapon_type (str): The type of weapon, either "ranged" or "melee".
        property (str): The property of the weapon, such as "finesse".

        Returns:
        int: The calculated damage based on the highest modifier or weapon type.
        """
        if "finesse" in str(property):
            damage = max(dexterity_modifier, strength_modifier)
            return damage
        if weapon_type == "ranged":
            return dexterity_modifier
        if weapon_type == "melee":
            return strength_modifier
    
    def get_data(self, client, collection_name):
        """
        Retrieve data from a specified MongoDB collection and return it as a pandas DataFrame.

        Parameters:
        client (pymongo.MongoClient): The MongoDB client instance.
        collection_name (str): The name of the collection to retrieve data from.

        Returns:
        pd.DataFrame: A DataFrame containing the data from the specified collection, with all values as strings.
        """
        db = client["context_data"]
        collection = db[collection_name]
        df = pd.DataFrame(list(collection.find()), dtype=str)
        return df
    
    def lower_case_list(self, lst):
        """
        Converts all strings in the given list to lowercase.

        Args:
            lst (list of str): The list of strings to be converted to lowercase.

        Returns:
            list of str: A new list with all strings converted to lowercase.
        """
        return [item.lower() for item in lst]

    def filter_dataframe(self, df, weapon_list, column_name, threshold=80):
        """
        Filters a DataFrame based on a list of weapon names and a similarity threshold.

        Args:
            df (pd.DataFrame): The DataFrame to filter.
            weapon_list (list): A list of weapon names to match against the DataFrame column.
            column_name (str): The name of the column in the DataFrame to search for weapon names.
            threshold (int, optional): The similarity score threshold for matching weapon names. Defaults to 80.

        Returns:
            pd.DataFrame or None: A DataFrame containing rows with matched weapon names, or None if no matches are found.
        """
        matched_weapons = set()
        for weapon in weapon_list:
            result = process.extractOne(weapon, df[column_name].tolist(), score_cutoff=threshold)
            if result: 
                best_match, score = result
                matched_weapons.add(best_match)
        filtered_df = df[df[column_name].isin(matched_weapons)]
        if filtered_df.empty:
            return None
        return filtered_df

    def character_weapons(self, client, weapons):
        """
        Retrieves and filters character weapons data.

        This method fetches the weapons data from the specified client, filters it based on the provided weapons list,
        and returns the filtered DataFrame. If no matching weapons are found, it logs the failed weapons to a file
        and returns a random sample of 2 weapons from the original DataFrame.

        Args:
            client (object): The client object used to fetch the weapons data.
            weapons (list): A list of weapon names to filter the weapons data.

        Returns:
            DataFrame: A DataFrame containing the filtered weapons data. If no matches are found, a random sample of 2 weapons is returned.
        """
        weapons_df = self.get_data(client, "weapons")
        filtered_df = self.filter_dataframe(weapons_df, weapons, "weapon_name")
        if filtered_df is None:
            with open("failed_weapons.txt", "a") as f:
                f.write(f"{weapons}\n")
            filtered_df = weapons_df.sample(n=2)
        return filtered_df
    
    def character_armor(self, client, armor):
        """
        Retrieves and filters armor data for a character.

        This method fetches armor data from a specified client, filters it based on the provided armor name,
        and returns the filtered DataFrame. If no matching armor is found, it logs the failed armor name
        to a file and returns a random sample of 2 rows from the armor data.

        Args:
            client (object): The client object used to fetch data.
            armor (str): The name of the armor to filter.

        Returns:
            DataFrame: A DataFrame containing the filtered armor data. If no match is found, a random sample
            of 2 rows from the armor data is returned.
        """
        armor_df = self.get_data(client, "armor")
        filtered_df = self.filter_dataframe(armor_df, armor, "armor")
        if filtered_df is None:
            with open("failed_armor.txt", "a") as f:
                f.write(f"{armor}\n")
            filtered_df = armor_df.sample(n=2)
        return filtered_df
    
    def validate_hit_dice(self, s):
        """
        Validates if the given string represents a valid hit dice notation.

        A valid hit dice notation can be in the form of 'dX' or 'YdX', where X and Y are integers.
        Examples of valid notations: 'd6', '2d8', '10d10'.

        Args:
            s (str): The string to validate.

        Returns:
            bool: True if the string is a valid hit dice notation, False otherwise.
        """
        pattern = r'^\d+d\d+$'
        pattern_2 = r'^d\d+$'
        if re.match(pattern_2, s) or re.match(pattern, s):
            print("Valid hit dice")
            return True
        else:
            return False



