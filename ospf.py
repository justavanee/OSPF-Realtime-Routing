import networkx as nx
import matplotlib.pyplot as plt
import random
import heapq

# Creating a predefined network with some edges
def create_initial_network():
    G = nx.Graph()
    G.add_edge('A', 'B', weight=4, latency=10, bandwidth=100)
    G.add_edge('A', 'C', weight=2, latency=5, bandwidth=50)
    G.add_edge('B', 'C', weight=5, latency=8, bandwidth=30)
    G.add_edge('B', 'D', weight=10, latency=15, bandwidth=70)
    G.add_edge('C', 'D', weight=3, latency=7, bandwidth=40)
    G.add_edge('D', 'E', weight=1, latency=4, bandwidth=100)
    G.add_edge('C', 'E', weight=8, latency=12, bandwidth=20)
    return G

# Function to display the network details (edges with bandwidth, weight, and latency)
def display_network_details(G):
    print("\nNetwork Details:")
    for node in G.nodes:
        print(f"Node {node}:")
        for neighbor in G.neighbors(node):
            edge_data = G[node][neighbor]
            print(f"  - Connected to {neighbor}: Weight={edge_data['weight']}, Latency={edge_data['latency']}, Bandwidth={edge_data['bandwidth']}\n")
    print("\n")

# Function to display the network graph with updated weights
def draw_network(G, shortest_paths=None):
    display_network_details(G)  # Print network details before visualization
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=700, node_color="lightblue")
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

    # Highlight the shortest paths
    if shortest_paths:
        for path in shortest_paths.values():
            edges_in_path = list(zip(path, path[1:]))
            nx.draw_networkx_edges(G, pos, edgelist=edges_in_path, edge_color='red', width=2)

    plt.title("OSPF Network Topology")
    plt.show()

# Function to add a new node or link to the network
def add_element(G):
    add_type = input("Do you want to add a (node/link)? ").strip().lower()
    if add_type == "node":
        node = input("Enter the name of the new node: ").strip().upper()
        if G.has_node(node):
            print(f"Node {node} already exists.")
        else:
            G.add_node(node)
            print(f"Node {node} has been added to the network.")
    elif add_type == "link":
        start_node = input("Enter the start node: ").strip().upper()
        end_node = input("Enter the end node: ").strip().upper()
        weight = int(input("Enter the weight of the link: "))
        latency = int(input("Enter the latency of the link: "))
        bandwidth = int(input("Enter the bandwidth of the link: "))
        if G.has_node(start_node) and G.has_node(end_node):
            G.add_edge(start_node, end_node, weight=weight, latency=latency, bandwidth=bandwidth)
            print(f"Link added between {start_node} and {end_node} with weight {weight}, latency {latency}, and bandwidth {bandwidth}\n")
        else:
            print("Error: One or both nodes do not exist in the network.")
    else:
        print("Invalid option. Please choose either 'node' or 'link'.")

# OSPF-inspired function to calculate shortest paths
def ospf_shortest_paths(G, source_node, qos_bandwidth=None):
    distances = {node: float('inf') for node in G.nodes}
    previous_nodes = {node: None for node in G.nodes}
    distances[source_node] = 0

    priority_queue = [(0, source_node)]

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        if current_distance > distances[current_node]:
            continue

        for neighbor in G.neighbors(current_node):
            weight = G[current_node][neighbor]['weight']
            bandwidth = G[current_node][neighbor].get('bandwidth', float('inf'))
            
            # QoS constraint: Ignore links with insufficient bandwidth
            if qos_bandwidth and bandwidth < qos_bandwidth:
                continue

            distance = current_distance + weight

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                heapq.heappush(priority_queue, (distance, neighbor))

    shortest_paths = {}
    for node in G.nodes:
        path = []
        current = node
        while current is not None:
            path.insert(0, current)
            current = previous_nodes[current]
        if distances[node] < float('inf'):
            shortest_paths[node] = path

    return shortest_paths

# Simulate network congestion by changing weights
def simulate_congestion(G):
    for edge in G.edges:
        change = random.randint(-2, 3)
        G[edge[0]][edge[1]]['weight'] = max(1, G[edge[0]][edge[1]]['weight'] + change)
    print("Network weights updated due to simulated congestion.")

# Function to simulate link or node failure
def simulate_failure(G):
    failure_type = input("Simulate (node/link) failure? ").strip().lower()
    if failure_type == "node":
        node = input("Enter the node to fail: ").strip().upper()
        if G.has_node(node):
            G.remove_node(node)
            print(f"Node {node} has been removed.")
        else:
            print("Node does not exist.")
    elif failure_type == "link":
        link = input("Enter the link to fail (e.g., A-B): ").strip().upper()
        nodes = link.split('-')
        if len(nodes) == 2 and G.has_edge(nodes[0], nodes[1]):
            G.remove_edge(nodes[0], nodes[1])
            print(f"Link {link} has been removed.")
        else:
            print("Link does not exist.")
    else:
        print("Invalid option.")

# Function to print routing table for each node
def print_routing_table(G):
    print("\nRouting Tables for All Nodes:")
    for node in G.nodes:
        print(f"\nRouting Table for Node {node}:")
        shortest_paths = ospf_shortest_paths(G, node)
        for destination, path in shortest_paths.items():
            print(f"  Destination: {destination} - Path: {' -> '.join(path)}\n")

# Generate LSA for a node
def generate_lsa(G, node):
    if not G.has_node(node):
        print(f"Node {node} does not exist.")
        return {}
    
    lsa = {}
    for neighbor in G.neighbors(node):
        lsa[neighbor] = G[node][neighbor]
    print(f"LSA for Node {node}: {lsa}\n")
    return lsa

# Main function to run the OSPF simulation
def run_simulation():
    G = create_initial_network()
    print("Initial Network:")
    draw_network(G)

    while True:
        action = input("Choose an action :\nRoute, LSA, Congestion, Add, Failure, Display, Exit\nYour choice : ").strip().lower()
        if action == "route":
            source_node = input("Enter the source node: ").strip().upper()
            if not G.has_node(source_node):
                print(f"Error: Node {source_node} does not exist in the network.")
                continue

            qos_bandwidth = input("Enter QoS minimum bandwidth requirement (or press Enter to skip): ").strip()
            qos_bandwidth = int(qos_bandwidth) if qos_bandwidth else None

            shortest_paths = ospf_shortest_paths(G, source_node, qos_bandwidth=qos_bandwidth)
            print(f"\nOSPF Shortest Paths from Node {source_node}:")
            for destination, path in shortest_paths.items():
                print(f"  To {destination}: {' -> '.join(path)}")
            draw_network(G, shortest_paths={destination: path for destination, path in shortest_paths.items() if len(path) > 1})
        
        elif action == "lsa":
            node = input("Enter the node to generate LSA: ").strip().upper()
            generate_lsa(G, node)

        elif action == "congestion":
            simulate_congestion(G)

        elif action == "failure":
            simulate_failure(G)

        elif action == "display":
            print("Displaying current network graph...")
            draw_network(G)

        elif action == "add":
            add_element(G)

        elif action == "exit":
            print("Exiting the simulation.")
            break

        else:
            print("Invalid action.")

if __name__ == "__main__":
    run_simulation()