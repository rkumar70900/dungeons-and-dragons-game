# Dungeons and Dragons Game

This project is a Dungeons and Dragons (D&D) game character generator and manager. It provides various functionalities to create, manage, and retrieve character attributes and context using a FastAPI application. The project includes several modules and files organized into different folders.

## Project Structure

### Folders and Files

#### `inference_pipeline/`
This folder contains the core logic for generating and managing character attributes and context.

- **`dep.py`**: This module provides various utility functions and classes for the D&D game. It includes methods for dice rolling, MongoDB connection, data retrieval, and game mechanics calculations.

#### `logger/`
This folder contains the logging functionality for the project.

- **`log_success.py`**: This module defines functions to log successful operations.
- **`log_failure.py`**: This module defines functions to log failed operations.

#### Root Directory
The root directory contains the main application file and the README file.

- **`main.py`**: This module defines a FastAPI application for the D&D game character generator. It includes various endpoints to generate and retrieve character attributes and context. It also includes middleware to clear Redis database when accessing Swagger UI or OpenAPI schema.
- **`README.md`**: This file provides an overview of the project, its structure, and detailed descriptions of the folders and files.

## Detailed File Descriptions

### `inference_pipeline/dep.py`
This module provides various utility functions and classes for the D&D game. It includes the following methods:
- `__init__`: Initializes the dependencies class.
- `roll_dice(total_faces, number_of_dices)`: Rolls a specified number of dice with a given number of faces.
- `drop_low_sum(total_faces, number_of_dices)`: Rolls dice and drops the lowest roll, then returns the sum of the remaining rolls.
- `connect_mongo()`: Connects to a MongoDB instance and returns the client object.
- `get_context_collection(client, collection_name)`: Retrieves a specified collection from the MongoDB context_data database.
- `get_distinct_names(collection)`: Retrieves distinct names from a MongoDB collection.
- `get_ability_modifier(ability_score)`: Calculates the ability modifier based on the given ability score.
- `calculate_attack_modifier(weapon_type, dexterity_modifier, strength_modifier, proficiency_modifier, property)`: Calculates the attack modifier based on weapon type and ability modifiers.
- `calculate_damage(dexterity_modifier, strength_modifier, weapon_type, property)`: Calculates the damage based on weapon type and ability modifiers.
- `get_data(client, collection_name)`: Retrieves data from a specified MongoDB collection and returns it as a pandas DataFrame.
- `lower_case_list(lst)`: Converts all strings in a list to lowercase.
- `filter_dataframe(df, weapon_list, column_name, threshold=80)`: Filters a DataFrame based on a list of weapon names and a similarity threshold.
- `character_weapons(client, weapons)`: Retrieves and filters weapon data for a character, writes failed matches to a file, and returns the filtered DataFrame.
- `character_armor(client, armor)`: Retrieves and filters armor data for a character, writes failed matches to a file, and returns the filtered DataFrame.
- `validate_hit_dice(s)`: Validates if a string matches the hit dice pattern (e.g., '1d6', 'd20').

### `main.py`
This module defines a FastAPI application for the D&D game character generator. It includes various endpoints to generate and retrieve character attributes and context. The endpoints include:
- `/store-output/{endpoint_name}`: Stores output data for a given endpoint in Redis.
- `/get-output/{endpoint_name}/`: Retrieves output data for a given endpoint from Redis.
- `/race`: Generates or retrieves the character's race.
- `/class`: Generates or retrieves the character's class.
- `/background`: Generates or retrieves the character's background.
- `/class_context`: Generates or retrieves the context for the character's class.
- `/race_context`: Generates or retrieves the context for the character's race.
- `/background_context`: Generates or retrieves the context for the character's background.
- `/abilities`: Generates or retrieves the character's abilities.
- `/ability_scores`: Generates or retrieves the character's ability scores.
- `/assign_ability_modifier`: Generates or retrieves the character's ability modifiers.
- `/proficieny_modifier`: Generates or retrieves the character's proficiency modifier.
- `/saving_throws`: Generates or retrieves the character's saving throws.
- `/skills`: Generates or retrieves the character's skills.
- `/passive_perception`: Generates or retrieves the character's passive perception.
- `/proficiencies_languages`: Generates or retrieves the character's proficiencies and languages.
- `/equipment_money`: Generates or retrieves the character's equipment and money.
- `/attacks`: Generates or retrieves the character's attacks.
- `/armor`: Generates or retrieves the character's armor class.
- `/initative`: Generates or retrieves the character's initiative.
- `/speed`: Generates or retrieves the character's speed.
- `/hit_dice`: Generates or retrieves the character's hit dice.
- `/point_maximum`: Generates or retrieves the character's hit point maximum.
- `/current_hit_point`: Generates or retrieves the character's current hit points.
- `/features`: Generates or retrieves the character's features.
- `/traits`: Generates or retrieves the character's traits.
- `/character_name`: Generates or retrieves the character's name.
- `/alignment`: Generates or retrieves the character's alignment.
- `/all`: Generates or retrieves all character attributes and context.

### `logger/log_success.py`
This module defines functions to log successful operations. It includes methods to log various types of successful events and operations.

### `logger/log_failure.py`
This module defines functions to log failed operations. It includes methods to log various types of failed events and operations.

## Dependencies
- **FastAPI**: Web framework for building APIs.
- **pydantic**: Data validation and settings management using Python type annotations.
- **redis**: Redis client for Python.
- **uuid**: UUID generation for unique identifiers.
- **inspect**: Provides introspection capabilities.
- **logger**: Custom logging module.
- **inference_pipeline**: Module containing methods for generating character attributes and context.

## Getting Started
To get started with the project, follow these steps:
1. Clone the repository.
2. Install the required dependencies.
3. Run the FastAPI application using `uvicorn main:app --reload`.
4. Access the API documentation at `http://localhost:8000/docs`.

## License
This project is licensed under the MIT License.

