import numpy as np
'''
COLUMN_KEY: List of parameters in the system. Indexing is important and must align with
the columns in the data and test_data files. 

This should be sorted topologically. 
'''
COLUMN_KEY = ["Blue Bulb (Compressor)", "Condenser Fan", "Dual Plug Outlet", "Heater Fan", 
              "Red Bulb (Heater)", "Gaze Webcam", "Contactor Relay", "SPST Fan Relay", 
              "Electric Heat Sequencer", "DPDT Switching Relay", "Power Transformer", 
              "Circuit Breaker", "Terminal Block", "Thermostat with Display"]
PARENTS = {
    "Blue Bulb (Compressor)": ["Blue Bulb (Compressor)", "Dual Plug Outlet"],
    "Condenser Fan": ["Condenser Fan", "Dual Plug Outlet", "SPST Fan Relay"],
    "Dual Plug Outlet": ["Dual Plug Outlet", "Condenser Fan"],
    "Heater Fan": ["Heater Fan", "Electric Heat Sequencer", "DPDT Switching Relay"],
    "Red Bulb (Heater)": ["Red Bulb (Heater)", "DPDT Switching Relay"],
    "Gaze Webcam": ["Gaze Webcam", "Dual Plug Outlet"],
    "Contactor Relay": ["Contactor Relay", "Terminal Block"],
    "SPST Fan Relay": ["SPST Fan Relay", "Condenser Fan", "Electric Heat Sequencer"],
    "Electric Heat Sequencer": ["Electric Heat Sequencer", "SPST Fan Relay", "Heater Fan"],
    "DPDT Switching Relay": ["DPDT Switching Relay", "Heater Fan", "Red Bulb (Heater)", "Terminal Block"],
    "Power Transformer": ["Power Transformer", "Circuit Breaker"],
    "Circuit Breaker": ["Circuit Breaker", "Power Transformer", "Terminal Block"],
    "Terminal Block": ["Terminal Block", "Contactor Relay", "Circuit Breaker", "DPDT Switching Relay", "Thermostat with Display"],
    "Thermostat with Display": ["Thermostat with Display", "Terminal Block"],
}

OUTPUTFILE = "gpt-interaction.txt"
GPT_MODEL = "gpt-3.5-turbo"

GRAPH_DESCRIPTION = "The following is the descrioption of the current knowledge graph: "
USER_PROMPT = "Please provide instructions on how you would like to update the graph based on the following user input: "
SYSTEM_PROMPT = f"""
You're provided with a description of a graph which represents the mental model of a physical system. 
The nodes in the graph are {COLUMN_KEY}, and the parent node of each node is listed in the following dictionary: {PARENTS}.
The nodes in the graph represent the components in the system and the edges between them represent the relationship between the components. 
Crucially, this is not a graph that represents the actual system but what a human that you will interact with believes the system is.
You will be provided an input, which is the description of the current knowledge graph and a statement that a user who is interacting with the physical system provides. 
YOUR JOB IS TO IDENTIFY EXACTLY WHICH NODE(S) OUT OF THE NODES IN THE GRAPH THE STATEMENT IS OBSERVING, AND WHAT VALUE WE CAN INFER FROM THE STATEMENT. 
Return the information in a python dictionary of nodes and their observed values. The value should always be a float.
For example if the node name was "node1" and the value observed is 50, you should return: {{"node name": 50, }}. 
If there are multiple nodes to update, you should return: {{"node name 1":50, "node name 2": 100}}.
YOU MUST ONLY RETURN THE DICTIONARY NOTHING ELSE.
"""


'''
STD_DEV: Standard deviation of each of the columns. Indeces should align with COLUMN_KEY
This is taken from ECLSS.py where the ECLSS params are created. Parameters with 0 standard
deviation is adjusted to 0.1
'''
STD_DEV = np.array([0.1, 0.1, 0.1, 0.1,
                    0.1, 0.1, 0.1, 0.1,
                    0.1, 0.1, 0.1,
                    0.1, 0.1, 0.1])

''' 
PARENTS: Represents the parents of each parameter according to the knowledge graph. Order
does not matter really.

TODO: need to differentiate parents from time t, vs time t-1
'''
# TODO: are the parents actually correct? I don't know the dependencies of each component. Should Root node with no parents exist?
"""
On cycles:
In a Dynamic Bayesian Network (DBN): 
- Temporal Slices: 
DBNs are constructed by stacking multiple "slices" of Bayesian networks, 
each representing the state of the system at a different time step. Each slice (or time step) is acyclic. 
- Temporal Dependencies: 
Arrows can connect nodes from one time slice to the next, allowing the representation of dependencies across time. 
- No Cycles within a Slice: 
Within any given time slice, the network remains acyclic. 
However, the entire DBN can model cycles over time when viewed across multiple slices. 
Even though each time slice (the relationships within a single time point) remains acyclic, 
the connections across time steps can form cycles in a broader sense, representing feedback loops and dynamic processes.
"""


# Example node values dictionary
INIT_NODE_VALUES = {
    "Blue Bulb (Compressor)": 10,
    "Condenser Fan": 15,
    "Dual Plug Outlet": 20,
    "Heater Fan": 25,
    "Red Bulb (Heater)": 30,
    "Gaze Webcam": 35,
    "Contactor Relay": 40,
    "SPST Fan Relay": 45,
    "Electric Heat Sequencer": 50,
    "DPDT Switching Relay": 55,
    "Power Transformer": 60,
    "Circuit Breaker": 65,
    "Terminal Block": 70,
    "Thermostat with Display": 75,
}
