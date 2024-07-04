import dbn
import gpt
import teleoperation
import config
import random
import matplotlib.pyplot as plt
import threading
import time
import numpy as np
from tqdm import tqdm
from scipy.spatial.distance import euclidean


def parse_user_input(grounding_agent, user_input, graph_description):
    # Implement this function to parse user input into observation format (dict)
    # Example: {'Condenser Fan': 280, 'Red Bulb (Heater)': 50}
    # GPT prompting portion
    grounding_agent.set_prompt(user_input, graph_description)
    # Prompt GPT API
    response = grounding_agent.ask_gpt()
    return grounding_agent.convert_to_dict(response)


def main():
    # Initialize KnowledgeGraph with initial distribution
    knowledge_graph = dbn.KnowledgeGraph()
    # Initialize ParticleFilter with initial distribution
    particle_filter = dbn.ParticleFilter(file_path='data.csv', num_particles=100)
    # while True:
    #     estimated_state, fault_params = particle_filter.update({})
    #     print(knowledge_graph.create_graph_description(estimated_state))
    #     knowledge_graph.update_nodes(estimated_state)
    #     knowledge_graph.visualize_graph()
    # Initialize GPT module
    grounding_agent = gpt.GPT(config.GPT_MODEL, config.OUTPUTFILE)

    estimated_state, fault_params = particle_filter.update({})
    knowledge_graph.update_nodes(estimated_state)
    knowledge_graph.visualize_graph()
    user_input = input("Enter observation (press Enter to stop): ")
    
    observation = parse_user_input(grounding_agent, user_input, knowledge_graph.create_graph_description(estimated_state))  # Parse user input into observation format
    estimated_state, fault_params = particle_filter.update(observation)
    # print("Estimated State:", estimated_state)
    print(knowledge_graph.create_graph_description(estimated_state))
    knowledge_graph.update_nodes(estimated_state)
    knowledge_graph.visualize_graph()

if __name__ == "__main__":
    main()

    






