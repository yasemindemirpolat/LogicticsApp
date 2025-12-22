import heapq
from models.graph import load_graph_once

def dijkstra_shortest_path(source_id: str, target_id: str):
    graph = load_graph_once()

    if source_id not in graph.nodes or target_id not in graph.nodes:
        return None

    dist = {source_id: 0.0}
    prev = {}
    visited = set()
    heap = [(0.0, source_id)]

    while heap:
        current_dist, u = heapq.heappop(heap)

        if u in visited:
            continue
        visited.add(u)

        if u == target_id:
            break

        for v, weight, _ in graph.neighbors(u):
            new_dist = current_dist + weight
            if v not in dist or new_dist < dist[v]:
                dist[v] = new_dist
                prev[v] = u
                heapq.heappush(heap, (new_dist, v))

    if target_id not in dist:
        return None

    path_nodes = []
    cur = target_id
    while cur != source_id:
        path_nodes.append(cur)
        cur = prev[cur]
    path_nodes.append(source_id)
    path_nodes.reverse()

    full_coords = []
    for i in range(len(path_nodes) - 1):
        u = path_nodes[i]
        v = path_nodes[i+1]
        u_info = graph.get_coords(u)
        if u_info:
            full_coords.append(u_info)
        
        edge_geometry = []
        for neighbor, weight, geom in graph.neighbors(u):
            if neighbor == v:
                edge_geometry = geom
                break
        
        for point in edge_geometry:
            full_coords.append({"lat": point[0], "lon": point[1]})

    target_info = graph.get_coords(target_id)
    if target_info:
        full_coords.append(target_info)

    distance_m = dist[target_id]

    return {
        "path": path_nodes,
        "path_coords": full_coords,
        "distance_m": distance_m,
        "distance_km": round(distance_m / 1000, 3),
        "node_count": len(path_nodes),
    }

def shortest_path_from_coords(source_lat, source_lon, target_lat, target_lon):
    graph = load_graph_once()
    s_id = graph.find_nearest_node(source_lat, source_lon)
    t_id = graph.find_nearest_node(target_lat, target_lon)

    if s_id is None or t_id is None:
        return None

    return dijkstra_shortest_path(s_id, t_id)

# --- İŞTE EKSİK OLAN FONKSİYON BU ---
def calculate_multi_stop_route(locations, vehicle_speed, vehicle_cost):
    """
    locations: [{'lat': x, 'lon': y}, ...]
    """
    if len(locations) < 2:
        return None

    full_path_coords = []
    total_distance_m = 0
    
    for i in range(len(locations) - 1):
        start = locations[i]
        end = locations[i+1]
        
        segment_result = shortest_path_from_coords(
            start['lat'], start['lon'], 
            end['lat'], end['lon']
        )
        
        if segment_result:
            total_distance_m += segment_result['distance_m']
            full_path_coords.extend(segment_result['path_coords'])
    
    total_km = total_distance_m / 1000
    estimated_time_hours = total_km / vehicle_speed if vehicle_speed > 0 else 0
    total_cost = total_km * vehicle_cost

    return {
        "path_coords": full_path_coords,
        "total_distance_km": round(total_km, 2),
        "estimated_time_min": round(estimated_time_hours * 60),
        "total_cost_tl": round(total_cost, 2)
    }

def calculate_shortest_path(source_id: str, target_id: str):
    return dijkstra_shortest_path(source_id, target_id)