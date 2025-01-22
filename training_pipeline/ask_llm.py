import marqo
from openai import OpenAI

class askLLM():
    def __init__(self):
        self.mq_client = marqo.Client(url='http://localhost:8882')
        self.client = OpenAI(api_key="")
    
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
        
