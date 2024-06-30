import csv
import numpy as np
import config
import random
import inflect
import networkx as nx
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor

class InitDistribution():
    def init():
        None

    def read_csv_and_pair(self, file_path:str):
        '''
        file_path: path to data file
        returns
            pairs: list[dict, dict]
            random order pairs of data as t-1, t
        '''
        pairs = []
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            for i in range(len(rows) - 1):
                pairs.append((rows[i], rows[i + 1]))

        for pair in pairs:
            for pair_dict in pair:
                for key in pair_dict.keys():
                    if pair_dict[key] == 'True':
                        pair_dict[key] = 1
                    elif pair_dict[key] == 'False':
                        pair_dict[key] = 0

        random.shuffle(pairs)
        return pairs

    def create_parent_dist_predictors(self, data):
        '''
        Matches every ECLSS component with its parent components between
        time t and time t - 1.

        Also, matches a regression model to predict parameter based off of parents
        This approximates P(x_t | x_t-1)

        Returns:
            dict(RandomForestRegressor) : each parameter has its own regression model
        '''
        parent_funcs = {}
        for param in config.PARENTS.keys():
            X = []
            for parent in config.PARENTS[param]:
                if parent == param: # take from prev time step
                    X.append([pair[1][parent] for pair in data])
                else: # take from same time step
                    X.append([pair[0][parent] for pair in data])

            X = np.array(X, dtype=np.float64)
            Y = np.array([pair[0][param] for pair in data], dtype=np.float64)

            clf = RandomForestRegressor()
            parent_funcs[param] = clf.fit(X.T, Y)
        
        return parent_funcs


class KnowledgeGraph:
    def __init__(self):
        self.G = nx.DiGraph()
        for child, parents in config.PARENTS.items():
            for parent in parents:
                self.G.add_edge(parent, child)
        self.node_values = {
                            "Blue Bulb (Compressor)": 0,
                            "Condenser Fan": 0,
                            "Dual Plug Outlet": 0,
                            "Heater Fan": 0,
                            "Red Bulb (Heater)": 0,
                            "Gaze Webcam": 0,
                            "Contactor Relay": 0,
                            "SPST Fan Relay": 0,
                            "Electric Heat Sequencer": 0,
                            "DPDT Switching Relay": 0,
                            "Power Transformer": 0,
                            "Circuit Breaker": 0,
                            "Terminal Block": 0,
                            "Thermostat with Display": 0,
                        }
        # Compute and store the positions of the nodes
        # self.pos = nx.spring_layout(self.G, k=1, iterations=50)
        # # Initialize the plot
        # plt.ion()
        # self.fig, self.ax = plt.subplots()

    def update_nodes(self, estimated_state):
        for idx, key in enumerate(self.node_values):
            self.node_values[key] = round(estimated_state[idx], 2)

    # Function to visualize the graph
    def visualize_graph(self):
        # # Clear the previous plot
        # self.ax.clear()
        # # Add nodes and edges based on the PARENTS dictionary
        # for child, parents in config.PARENTS.items():
        #     for parent in parents:
        #         self.G.add_edge(parent, child)

        # Compute a layout to avoid overlaps
        # Increase k to make nodes further apart
        pos = nx.spring_layout(self.G, k=1, iterations=50)  # Adjust k for more spacing

        # Update labels to include node values
        labels = {node: f"{node}\nValue: {value}" for node, value in self.node_values.items()}

        # Draw the graph using Matplotlib
        plt.figure(figsize=(12, 8))
        nx.draw(self.G, pos, with_labels=True, labels=labels, node_size=3000, node_color="skyblue", font_size=10, font_weight="bold", arrows=True)
        plt.title("Dynamic Bayesian Network Visualization with Node Values")
        # plt.pause(0.1)  # Pause to allow plot to update
        plt.show()

        # # Clear the previous plot
        # self.ax.clear()

        # # # Compute a layout to avoid overlaps
        # # pos = nx.spring_layout(self.G, k=0.3, iterations=50)  # Adjust k for more spacing

        # # Update labels to include node values
        # labels = {node: f"{node}\nValue: {value}" for node, value in self.node_values.items()}

        # # Draw the graph using Matplotlib
        # nx.draw(self.G, self.pos, with_labels=True, labels=labels, ax=self.ax, node_size=3000, node_color="skyblue", font_size=10, font_weight="bold", arrows=True)
        # self.ax.set_title("Dynamic Bayesian Network Visualization with Node Values")
        # plt.pause(0.1)
                        
    def print_graph(self):
        pos = nx.spring_layout(self.graph)  # Position nodes using the spring layout algorithm
        nx.draw(self.graph, pos, with_labels=True, node_size=1000, node_color='skyblue', font_size=12, font_weight='bold')  # Draw nodes with labels
        labels = nx.get_edge_attributes(self.graph, 'weight')  # Get edge weights
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=labels)  # Draw edge labels
        plt.show(block=False)

    def update_edge_weight(self):
        raise NotImplementedError 
    
    def add_node(self, node, attributes):
        # Check if the node passed in exists in the graph
        # Add node to the graph
        # Reset the weights (update the edge matrix)
        raise NotImplementedError 
    
    def node_exists(self, node):
        raise NotImplementedError 
    
    def create_graph_description(self, estimated_state) -> str:
        description = ""
        for idx, key in enumerate(self.node_values):
            description += f"The value for node {key} is {round(estimated_state[idx], 2)}\n"
        return description  


class ParticleFilter():
    
    def __init__(self, file_path, num_particles=None):
        self.init_dist = InitDistribution()
        # file path of data
        data = self.init_dist.read_csv_and_pair(file_path)
        self.data = data

        # length of data
        if num_particles:
            self.NUM_PARTICLES = num_particles
        else:
            self.NUM_PARTICLES = len(data)

        # particles only takes the list of data points, not the pairs
        self.particles = np.array([list(pair[0].values()) for pair in data[:self.NUM_PARTICLES]], dtype=np.float32)
        print("Amount of particles is", self.particles.shape)

        # weights are initialized to all be the same
        self.weights = np.repeat(1/self.NUM_PARTICLES, self.NUM_PARTICLES)
        # import pdb; pdb.set_trace()

        # paired = np.array([self.pair_to_array(pair) for pair in data], dtype=np.float32)
        # self.cov_matrix = np.diag(np.tile(STD_DEV, 2) ** 2)  + np.cov(paired.T)

        # X_t = np.array([list(pair[0].values()) for pair in self.data], dtype=np.float32)
        # y_t = np.array([list(pair[1].values()) for pair in self.data], dtype=np.float32)
        # self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        # self.model.fit(X_t, y_t)

        self.parent_funcs = self.init_dist.create_parent_dist_predictors(data)

    
    def pair_to_array(pair):
        '''
        turns list[dict, dict] to list[float] from concatenating the values of dicts
        '''
        return list(pair[0].values()) + list(pair[1].values())

    def update(self, Y_t):
        '''
        Y_t: observation

        uses Y_t and particles to create new set of particles X_ti and weights w_i
        '''
        # Calls regression models for X_ti and evaluates w_i = P(Y_t | X_t)
        X_ti, w_i, fault_params = self.sample_particle(Y_t, self.particles)
        self.particles = X_ti
        self.weights = w_i


        self.weights = self.normalize_weights(self.weights)
        self.resample_particles()

        return self.estimate_state(), fault_params

    def sample_particle(self, Y_t, particles):
        '''
        Y_t: observation
        particle: particle being updated

        Based off of: https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=a6ff8a17100749d068b57322857f65a4c76deffd

        Returns (X_ti, w_i)
            X_ti: new particle as graph
            w_i: weight of new particle
        '''
        # First transition update of particle
        X_ti = np.zeros_like(particles).T
        # Get weight of evidence
        w_i= np.ones_like(self.weights)

        fault_params = set()

        # Doesn't have to iterate through all the particles because of matrix magic
        for node_index in range(len(particles[0])): 
            # iterates by component
            parents = np.array([particles[: ,config.COLUMN_KEY.index(parent)] for parent in config.PARENTS[config.COLUMN_KEY[node_index]]])

            # predicted transition value based off of regression model
            mean = np.array(self.parent_funcs[config.COLUMN_KEY[node_index]].predict(parents.T))

            if not config.COLUMN_KEY[node_index] in Y_t: # no observation
                X_ti[node_index] = mean

            else: # observation exists

                # assumption: we are very confident about observation, should this be changed for fault detection?
                X_ti[node_index] = Y_t[config.COLUMN_KEY[node_index]]

                # update weight of particle
                # w = P(Y_t | X_t), uses a normal distribution which is centered at X_t and has standard deviation of the sensor noise
                w_update = np.exp(-1 * (Y_t[config.COLUMN_KEY[node_index]]-mean)**2/(2*config.STD_DEV[node_index]**2))/np.sqrt(2*np.pi*config.STD_DEV[node_index]**2)


                # If the weight is 0 for all particles
                if w_update.max() == 0:
                    fault_params.add(config.COLUMN_KEY[node_index])

                # prevents all weights going to 0
                w_i *= w_update + 1e-5

        return X_ti.T, w_i, fault_params
  
    def resample_particles(self):
        try:
            self.particles = np.array(random.choices(self.particles, weights=self.weights, k=self.NUM_PARTICLES))

            # reset the weights after resampling
            self.weights = np.repeat(1/self.NUM_PARTICLES, self.NUM_PARTICLES)
        except:
            print("Can't resample", self.weights)

    def normalize_weights(self, weights):
        '''
        normalize the weights of all particles, divide by sum
        '''
        # import pdb; pdb.set_trace()
        return weights / sum(weights)

    def estimate_state(self):
        '''
        estimate current state based on beliefs over particles

        Basically the weighted average particle
        '''
        return np.matmul(self.weights.T, self.particles)
    
    def create_graph_description(self) -> str:
        num_nodes = self.graph.number_of_nodes()
        num_edges = self.graph.number_of_edges()
        description = f"The current graph has {num_nodes} nodes and {num_edges} edges.\n"
        for node, data in self.graph.nodes(data=True):
            node_description = f"Node {node} has attributes "
            attributes = [f'{f"{attr}: {value[0]} distribution with mean of {value[1][0]}" if len(value[1]) == 1 else f"{attr}: {value[1][0]} with a confidence level of {str(value[1][1])}"}' for attr, value in data.items()]
            node_description += ", ".join(attributes) + ".\n"
            description += node_description

        # Commented out now to reduce token size
        # # Add edge descriptions
        # for u, v, data in self.graph.edges(data=True):
        #     description += f"Node {u} is connected to node {v} with a weight of {data['weight']}.\n"

        return description
