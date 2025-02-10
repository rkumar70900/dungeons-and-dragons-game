import marqo
from openai import OpenAI
import json

class askLLM():
    def __init__(self):
        self.mq_client = marqo.Client(url='http://localhost:8882')
        self.client = OpenAI(api_key="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")
    
    def extract_context(self, about, name):

        classes = self.mq_client.index(about).search(
            q=f"information about {name}", search_method='LEXICAL', limit=1
        )

        context = " ".join(hit["content"] for hit in classes.get("hits", []))

        return context

    def get_abilities(self, class_name, class_context, model="gpt-3.5-turbo"):

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
        
        return response.choices[0].message.content
    
    def get_saving_throws(self, class_name, class_context, model="gpt-3.5-turbo"):

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
        
        return response.choices[0].message.content
    
    def get_skills(self, class_name, background_name, class_context, background_context, model="gpt-3.5-turbo"):

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
        
        return response.choices[0].message.content

    def get_proficiencies_languages(self, class_name, background_name, class_context, background_context, model="gpt-3.5-turbo"):

        user_query = f'which armor, weapons, kits, instruments, languages does the character belonging \
                        to {class_name} and {background_name} have. Consider both the class and background and give me only one list. \
                             Along with this, for every armor, weapon, kit and instrument give me a bonus associated with them when used in the game \
                             do your thinking before answering. \
                            I need the output in a json formatted string in this way \
                                "armor": [list here], "weapons": [list here], "kits": [list here], "instruments": [list here], "languages": [list here]'
        
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
        
        return json.loads(response.choices[0].message.content)
    
    def get_equipment_money(self, class_name, background_name, class_context, background_context, model="gpt-3.5-turbo"):

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
        return json.loads(response.choices[0].message.content)
        
