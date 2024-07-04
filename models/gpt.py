# For GPT prompting
import openai
import warnings
from datetime import datetime

# For graph manipulation
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

# For distributions
from scipy.stats import norm, bernoulli

# General
import ast # For converting string to list
import sys # For exiting with error code
import math
import config
import utils

class GPT:
    def __init__(self, model: str, output_file, keep_history=False):
        # Set OpenAI API key
        openai.api_key = utils.get_gpt_apikey()
        self.model = model
        self.messages = [{"role": "system", "content": config.SYSTEM_PROMPT}]
        self.keep_history = keep_history
        self.output_file = output_file

    def __warning(self, missing: str):
        while True:
            user_input = input(f"Missing {missing} prompt. Do you want to continue? (y/n): ").strip().lower()
            if user_input in ['y', 'n']:
                return user_input == 'y'
            else:
                print("Please enter 'y' or 'n'.")

    def set_prompt(self, prompt: str, graph_description: str) -> None:
        message = {"role": "user", "content": config.GRAPH_DESCRIPTION+graph_description+config.USER_PROMPT+prompt}
        if self.keep_history:
            self.messages.append(message)
        else:
            self.messages = [{"role": "system", "content": config.SYSTEM_PROMPT}]
            self.messages.append(message)

    # Function to interact with the GPT API
    def ask_gpt(self):
        # Check if system and prompts have been set
        system_count = 0
        prompt_count = 0
        for message in self.messages:
            if message["role"] == "system":
                system_count += 1
            if message["role"] == "user":
                prompt_count += 1

        # Throw a warning if not set
        missing = []
        if system_count == 0:
            warnings.warn("System prompt has not been set", Warning)
            missing.append("System")
        if system_count == 0:
            warnings.warn("User prompt has not been set", Warning)
            missing.append("User")

        # Ask whether the user wants to continue
        if len(missing) != 0:
            if self.__warning(missing):
                print("Continuing with the prompting...")
                response = openai.chat.completions.create(
                    model= self.model,
                    messages=self.messages
                    )
                self.record_interaction(self.output_file, response.choices[0].message)
                return response.choices[0].message.content
            else:
                print("Prompting aborted.")
                sys.exit(1)
        else:
            response = openai.chat.completions.create(
                model= self.model,
                messages=self.messages
                )
            self.record_interaction(self.output_file, response.choices[0].message.content)
            return response.choices[0].message.content
        
    # Function to record the interaction
    def record_interaction(self, file_path: str, response) -> None:
        # Get the current time
        current_time = datetime.now()
        with open(file_path, 'a') as file:
            file.write(f"Time: {current_time}\n")
            file.write(f"model: {self.model}\n")
            file.write(f"Prompt: {self.messages}\n")
            file.write(f"Response: {response}\n")
            file.write("-------------------------------------------------------------------------------------------\n")

    def convert_to_dict(self, response):
        dictionary = ast.literal_eval(response)
        return dictionary