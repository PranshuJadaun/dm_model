import streamlit as st

# ---------- Helpers to load data ---------- #
def load_adjacency(file_path='adj.txt'):
    graph = {}
    with open(file_path, 'r') as f:
        for line in f:
            if line.strip():
                state, neighbors = line.split("(")
                state = state.strip()
                neighbors = [n.strip() for n in neighbors.rstrip(")\n").split(",") if n.strip()]
                # Add the state with its neighbors
                if state not in graph:
                    graph[state] = []
                # Add neighbors for the state
                graph[state].extend(neighbors)
                # Since the graph is undirected, add the reverse edge as well
                for neighbor in neighbors:
                    if neighbor not in graph:
                        graph[neighbor] = []
                    if state not in graph[neighbor]:
                        graph[neighbor].append(state)
    return graph

def load_weights(file_path='weight.txt'):
    weights = {}
    with open(file_path, 'r') as f:
        for line in f:
            if line.strip():
                path_part, dist_part = line.strip().split('(')
                dist = int(dist_part.replace(')', '').strip())
                # Split the path into the two nodes and remove extra spaces
                u, v = [node.strip() for node in path_part.split('-')]
                # Store the weight for both directions (undirected graph)
                weights[(u, v)] = dist
                weights[(v, u)] = dist
    return weights

# ---------- Shortest Path Logic (Dijkstra's Algorithm) ---------- #
def dijkstra(graph, weights, start, end):
    import heapq
    heap = [(0, start)]
    visited = set()
    # Initialize distance for all nodes in the graph
    dist = {node: float('inf') for node in graph}
    dist[start] = 0
    prev = {}

    while heap:
        d, current = heapq.heappop(heap)
        if current in visited:
            continue
        visited.add(current)

        for neighbor in graph.get(current, []):
            # Using the weight dictionary; if an edge is missing, use infinity
            weight = weights.get((current, neighbor), float('inf'))
            new_dist = d + weight
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                prev[neighbor] = current
                heapq.heappush(heap, (new_dist, neighbor))

    # Reconstruct the shortest path
    path = []
    current = end
    while current in prev:
        path.append(current)
        current = prev[current]
    if current == start:
        path.append(start)
        path.reverse()
        return path, dist[end]
    else:
        return None, float('inf')

# ---------- Page: Find Shortest Path ---------- #
def page_shortest_path():
    st.title("🔍 Shortest Path Finder (Undirected Graph)")

    graph = load_adjacency()
    weights = load_weights()

    nodes = list(graph.keys())
    start = st.selectbox("Start Vertex", nodes)
    end = st.selectbox("End Vertex", nodes)

    if st.button("Find Shortest Path"):
        path, cost = dijkstra(graph, weights, start, end)
        if path:
            st.success(f"Path: {' → '.join(path)} | Total Distance: {cost} km")
        else:
            st.error("No path found!")

# ---------- Page: Add New Vertex ---------- #
def page_add_vertex():
    st.title("➕ Add Vertex")

    vertex = st.text_input("Vertex Name (e.g., e)")
    neighbors = st.text_input("Neighbors (comma separated, e.g., b,f)")
    distances = st.text_area("Distances (format: e-b(8), e-f(3))")

    if st.button("Add Vertex"):
        if vertex and neighbors and distances:
            # Update adj.txt
            with open("adj.txt", "a") as f:
                f.write(f"\n{vertex}({neighbors})")

            # Update weight.txt
            with open("weight.txt", "a") as f:
                for dist_entry in distances.split(','):
                    f.write(f"\n{dist_entry.strip()}")

            st.success(f"Vertex '{vertex}' added successfully!")
        else:
            st.error("Please fill all fields!")

# ---------- Streamlit Navigation ---------- #
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Find Shortest Path", "Add Vertex"])

if page == "Find Shortest Path":
    page_shortest_path()
elif page == "Add Vertex":
    page_add_vertex()
