import models.gpt as gpt
import models.config as config

JSON_FILE = "/Users/tetsu/Documents/School/mental_model/models/data/initialization_demo.json"
input = []
grounding_agent = gpt.GPT(config.GPT_MODEL, config.OUTPUTFILE)

with open(JSON_FILE, 'r') as input_file:
    
    parse_user_input()

def parse_user_input(grounding_agent, user_input, graph_description):
    # Implement this function to parse user input into observation format (dict)
    # Example: {'Condenser Fan': 280, 'Red Bulb (Heater)': 50}
    # GPT prompting portion
    grounding_agent.set_prompt(user_input, graph_description)
    # Prompt GPT API
    response = grounding_agent.ask_gpt()
    return grounding_agent.convert_to_dict(response)