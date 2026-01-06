import heapq
from models.graph import load_graph_once
from models.db import Vehicle

# --- TEMEL ROTA ALGORİTMASI (DIJKSTRA) ---
def dijkstra_shortest_path(source_id: str, target_id: str):
    graph = load_graph_once()

    if str(source_id) not in graph.nodes or str(target_id) not in graph.nodes:
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

        # neighbors -> (v, weight, geometry)
        for v, weight, _ in graph.neighbors(u):
            new_dist = current_dist + weight
            if v not in dist or new_dist < dist[v]:
                dist[v] = new_dist
                prev[v] = u
                heapq.heappush(heap, (new_dist, v))

    if target_id not in dist:
        return None

    # Path'i geri kur
    path_nodes = []
    cur = target_id
    while cur != source_id:
        path_nodes.append(cur)
        cur = prev[cur]
    path_nodes.append(source_id)
    path_nodes.reverse()

    # Geometriyi oluştur
    full_coords = []
    for i in range(len(path_nodes) - 1):
        u = path_nodes[i]
        v = path_nodes[i+1]
        
        u_info = graph.get_coords(u)
        if u_info: full_coords.append(u_info)
        
        edge_geometry = []
        for neighbor, weight, geom in graph.neighbors(u):
            if neighbor == v:
                edge_geometry = geom
                break
        
        for point in edge_geometry:
            full_coords.append({"lat": point[0], "lon": point[1]})

    target_info = graph.get_coords(target_id)
    if target_info: full_coords.append(target_info)

    return {
        "path_coords": full_coords,
        "distance_m": dist[target_id]
    }

def shortest_path_from_coords(source_lat, source_lon, target_lat, target_lon):
    graph = load_graph_once()
    s_id = graph.find_nearest_node(source_lat, source_lon)
    t_id = graph.find_nearest_node(target_lat, target_lon)

    if s_id is None or t_id is None:
        return None

    return dijkstra_shortest_path(s_id, t_id)


# --- ÇOKLU ARAÇLI ROTA HESAPLAMA ---
def calculate_mixed_vehicle_route(segments):
    print("--- Rota Hesaplama Başladı ---")
    
    total_distance_m = 0
    total_time_h = 0
    total_cost = 0
    all_path_coords = []

    all_vehicles = {v.id: v for v in Vehicle.query.all()}

    for i, seg in enumerate(segments):
        try:
            v_id = int(seg['vehicle_id'])
        except (ValueError, TypeError):
            continue

        vehicle = all_vehicles.get(v_id)
        if not vehicle:
            continue
        
        # Aracın bilgilerini al
        vehicle_speed = vehicle.type.speed_kmh
        vehicle_cost_per_km = vehicle.type.cost_per_km
        
        s_lat, s_lon = seg['start']['lat'], seg['start']['lon']
        t_lat, t_lon = seg['end']['lat'], seg['end']['lon']

        graph = load_graph_once()
        s_id = graph.find_nearest_node(s_lat, s_lon)
        t_id = graph.find_nearest_node(t_lat, t_lon)

        if not s_id or not t_id:
            continue

        path_data = dijkstra_shortest_path(s_id, t_id)
        if not path_data:
            continue

        dist_m = path_data['distance_m']
        coords = path_data['path_coords']

        # Hesaplamalar
        dist_km = dist_m / 1000.0
        time_h = dist_km / vehicle_speed if vehicle_speed > 0 else 0
        cost = dist_km * vehicle_cost_per_km

        total_distance_m += dist_m
        total_time_h += time_h
        total_cost += cost
        all_path_coords.extend(coords)

    return {
        "path_coords": all_path_coords,
        "total_distance_km": round(total_distance_m / 1000, 2),
        "total_time_min": round(total_time_h * 60),
        "total_cost_tl": round(total_cost, 2)
    }


# --- OPTİMİZASYON ALGORİTMALARI (YENİ) ---

def get_distance_matrix(locations):
    """Lokasyonlar arası mesafe matrisi oluşturur"""
    matrix = {}
    graph = load_graph_once()
    
    # Her nokta çifti için en kısa mesafeyi bul (Dijkstra ile)
    for i in range(len(locations)):
        for j in range(len(locations)):
            if i == j: continue
            
            loc_a = locations[i]
            loc_b = locations[j]
            
            node_a = graph.find_nearest_node(loc_a['lat'], loc_a['lon'])
            node_b = graph.find_nearest_node(loc_b['lat'], loc_b['lon'])
            
            if node_a and node_b:
                path_data = dijkstra_shortest_path(node_a, node_b)
                dist = path_data['distance_m'] if path_data else float('inf')
                matrix[(loc_a['id'], loc_b['id'])] = dist
                
    return matrix

def solve_tsp_with_constraints(stops, fixed_indices):
    """
    Sabit durakları koruyarak diğerlerini en yakın komşu mantığıyla dizer.
    """
    n = len(stops)
    if n < 3: return stops

    result_route = [None] * n
    free_stops = []

    # 1. Sabitleri yerleştir, serbestleri ayır
    for i in range(n):
        if i in fixed_indices:
            result_route[i] = stops[i]
        else:
            free_stops.append(stops[i])

    graph = load_graph_once()

    # 2. Boşlukları doldur
    for i in range(n):
        if result_route[i] is not None:
            continue
        
        # Bir önceki durağı bul
        prev_stop = result_route[i-1] if i > 0 else None
        
        # Eğer başlangıç bile boşsa, serbestlerden ilkini al
        if not prev_stop:
            best_stop = free_stops.pop(0)
            result_route[i] = best_stop
            continue

        # En yakın serbest durağı bul
        best_stop = None
        min_dist = float('inf')
        best_index_in_free = -1

        s_node = graph.find_nearest_node(prev_stop['lat'], prev_stop['lon'])

        for idx, candidate in enumerate(free_stops):
            t_node = graph.find_nearest_node(candidate['lat'], candidate['lon'])
            
            if s_node and t_node:
                # Basitlik için burada kuş uçuşu (Öklid) bakabiliriz hız için
                # Ama doğrusu Dijkstra'dır, şimdilik graph üzerinden yaklaşık bakalım:
                # Performans için burada graph fonksiyonunu çağırmak yerine
                # get_distance_matrix kullanabilirdik ama dinamik çözüm için:
                path_data = dijkstra_shortest_path(s_node, t_node)
                dist = path_data['distance_m'] if path_data else float('inf')
                
                if dist < min_dist:
                    min_dist = dist
                    best_stop = candidate
                    best_index_in_free = idx
        
        if best_stop:
            result_route[i] = best_stop
            free_stops.pop(best_index_in_free)
        else:
            result_route[i] = free_stops.pop(0)

    return result_route

def optimize_stop_order(stops, fixed_indices):
    return solve_tsp_with_constraints(stops, fixed_indices)