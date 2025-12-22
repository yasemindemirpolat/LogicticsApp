# services/route_service.py
import heapq
from models.graph import load_graph_once
from models.db import Vehicle

# --- DIJKSTRA ALGORİTMASI ---
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

        # neighbors -> (v, weight, geometry)
        for v, weight, _ in graph.neighbors(u):
            new_dist = current_dist + weight
            if v not in dist or new_dist < dist[v]:
                dist[v] = new_dist
                prev[v] = u
                heapq.heappush(heap, (new_dist, v))

    if target_id not in dist:
        return None

    # Path'i (Node ID listesi) geri kur
    path_nodes = []
    cur = target_id
    while cur != source_id:
        path_nodes.append(cur)
        cur = prev[cur]
    path_nodes.append(source_id)
    path_nodes.reverse()

    # Geometriyi (Kıvrımları) oluştur
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


# --- ÇOKLU ARAÇLI ROTA HESAPLAMA ---
def calculate_mixed_vehicle_route(segments):
    print("--- Rota Hesaplama Başladı ---")
    print(f"Gelen Segment Sayısı: {len(segments)}")

    total_distance_m = 0
    total_time_h = 0
    total_cost = 0
    all_path_coords = []

    # Veritabanından araçları çek (dictionary olarak sakla)
    all_vehicles = {v.id: v for v in Vehicle.query.all()}
    
    for i, seg in enumerate(segments):
        print(f"\n[Segment {i+1}] İşleniyor...")
        
        try:
            v_id = int(seg['vehicle_id'])
        except (ValueError, TypeError):
            print(f"HATA: Geçersiz Vehicle ID: {seg.get('vehicle_id')}")
            return None

        vehicle = all_vehicles.get(v_id)
        if not vehicle:
            print(f"HATA: Araç bulunamadı! ID: {v_id}")
            return None
        
        # --- DÜZELTME BURADA YAPILDI ---
        # vehicle.name YOK! vehicle.type.name VAR.
        # Hız ve maliyet bilgileri de vehicle.type içinde.
        vehicle_type_name = vehicle.type.name
        vehicle_speed = vehicle.type.speed_kmh
        vehicle_cost_per_km = vehicle.type.cost_per_km
        
        print(f"  - Araç: {vehicle.plate_number} (Tip: {vehicle_type_name}, Hız: {vehicle_speed})")
        
        # Koordinatları al
        s_lat, s_lon = seg['start']['lat'], seg['start']['lon']
        t_lat, t_lon = seg['end']['lat'], seg['end']['lon']

        # En yakın node'ları bul
        graph = load_graph_once()
        s_id = graph.find_nearest_node(s_lat, s_lon)
        t_id = graph.find_nearest_node(t_lat, t_lon)

        if not s_id or not t_id:
            print("HATA: Koordinatlara uygun Node bulunamadı!")
            continue

        # Dijkstra çalıştır
        path_data = dijkstra_shortest_path(s_id, t_id)
        
        if not path_data:
            print(f"HATA: {s_id} -> {t_id} yol bulunamadı!")
            return None 

        print(f"  - Yol Bulundu! Mesafe: {path_data['distance_m']} metre")

        dist_m = path_data['distance_m']
        coords = path_data['path_coords']

        # Hesaplamalar (Artık vehicle.type üzerinden alınan verileri kullanıyoruz)
        dist_km = dist_m / 1000.0
        time_h = dist_km / vehicle_speed if vehicle_speed > 0 else 0
        cost = dist_km * vehicle_cost_per_km

        total_distance_m += dist_m
        total_time_h += time_h
        total_cost += cost
        all_path_coords.extend(coords)

    print("\n--- Rota Hesaplama Başarılı ---")
    return {
        "path_coords": all_path_coords,
        "total_distance_km": round(total_distance_m / 1000, 2),
        "total_time_min": round(total_time_h * 60),
        "total_cost_tl": round(total_cost, 2)
    }

def calculate_shortest_path(source_id: str, target_id: str):
    return dijkstra_shortest_path(source_id, target_id)