import os
import networkx as nx
import plotly.graph_objects as go
import osmnx as ox
import numpy as np
import time

def k_shortest_paths(graph, start_node, end_node, k):
    paths = list(nx.all_shortest_paths(graph, source=start_node, target=end_node))
    return paths[:k] if len(paths) >= k else paths

def generate_paths(origin_point, target_point, perimeter, k):
    origin_lat, origin_long = origin_point
    target_lat, target_long = target_point

    north, south = max(origin_lat, target_lat), min(origin_lat, target_lat)
    east, west = max(origin_long, target_long), min(origin_long, target_long)

    mode = 'drive'
    roadgraph = ox.graph_from_bbox(north + perimeter, south - perimeter, east + perimeter, west - perimeter,
                                   network_type=mode, simplify=True)

    origin_coords = (origin_long, origin_lat)
    target_coords = (target_long, target_lat)

    origin_node = ox.distance.nearest_nodes(roadgraph, *origin_coords)
    target_node = ox.distance.nearest_nodes(roadgraph, *target_coords)

    start_time = time.time()
    routes = k_shortest_paths(roadgraph, origin_node, target_node, k)
    elapsed_time = time.time() - start_time
    print(f"Time elapsed for finding {k} shortest paths: {elapsed_time} seconds")

    paths = []
    for i, route in enumerate(routes):
        lat_long = [(roadgraph.nodes[node_id]['y'], roadgraph.nodes[node_id]['x']) for node_id in route]
        lat, long = zip(*lat_long)
        paths.append((long, lat, i))

    return paths

def plot_map(origin_point, target_point, paths, k):
    print("Setting up figure...")
    fig = go.Figure()


    fig.add_trace(go.Scattermapbox(
        mode="markers",
        lon=[origin_point[1]],
        lat=[origin_point[0]],
        marker={'size': 16, 'color': '#CE55FF'},
        name="Origin"
    ))

    fig.add_trace(go.Scattermapbox(
        mode="markers",
        lon=[target_point[1]],
        lat=[target_point[0]],
        marker={'size': 16, 'color': '#CE55FF'},
        name="Destination"
    ))


    colors = ['#FF0000', '#0000FF', '#00FF00'][:k]
    for i, path in enumerate(paths):
        long, lat, color_index = path
        fig.add_trace(go.Scattermapbox(
            mode="lines",
            lon=long,
            lat=lat,
            marker={'size': 10},
            name=f"Path {i + 1}",
            line=dict(width=4.5, color=colors[color_index]),
        ))


    fig.update_layout(
        mapbox_style="mapbox://styles/mapbox/satellite-v9",
        mapbox_accesstoken="YOUR_MAPBOX_API_KEY",
        legend=dict(yanchor="top", y=1, xanchor="left", x=0.83),
        #title=f"<span style='font-size: 32px;'><b>The K Shortest Paths Map ({k} Paths)</b></span>",
        font_family="Times New Roman",
        font_color="#333333",
        title_font_size=32,
        font_size=18,
        width=2000,
        height=1000,
    )


    lat_center = (origin_point[0] + target_point[0]) / 2
    long_center = (origin_point[1] + target_point[1]) / 2

    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        title=dict(yanchor="top", y=.97, xanchor="left", x=0.03),
        mapbox={
            'center': {'lat': lat_center, 'lon': long_center},
            'zoom': 12.2
        }
    )

    print("Saving image to the output folder...")
    fig.write_image(os.path.join(OS_PATH, 'output', f'K_Shortest_Paths_Map1_{k}.jpg'), scale=3)
    print("Generating the map in the browser...")
    fig.show()


OS_PATH = os.path.dirname(os.path.realpath(__file__))
print(OS_PATH)

# User input validation
while True:
    try:
        origin_input = input("Enter the origin geocoordinate (latitude, longitude): ")
        target_input = input("Enter the target geocoordinate (latitude, longitude): ")

        origin_coordinates = origin_input.replace("(", "").replace(")", "").split(",")
        target_coordinates = target_input.replace("(", "").replace(")", "").split(",")

        origin_latitude, origin_longitude = float(origin_coordinates[0].strip()), float(origin_coordinates[1].strip())
        target_latitude, target_longitude = float(target_coordinates[0].strip()), float(target_coordinates[1].strip())

        origin_point = (origin_latitude, origin_longitude)
        target_point = (target_latitude, target_longitude)

        print("Origin Point:", origin_point)
        print("Target Point:", target_point)
        break
    except ValueError:
        print("Invalid input. Please enter valid latitude and longitude.")


perimeter = 0.5

k = 3


print("* * * * * * * * * * * * * Finding Optimal Paths * * * * * * * * * * * * * *")
paths = generate_paths(origin_point, target_point, perimeter, k)
plot_map(origin_point, target_point, paths, k)
