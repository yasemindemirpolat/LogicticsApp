# services/route_service.py
import heapq
from models.graph import load_graph_once


def dijkstra_shortest_path(source_id: str, target_id: str):
    graph = load_graph_once()

    # Node var mı kontrol et
    if source_id not in graph.nodes or target_id not in graph.nodes:
        return None

    dist = {source_id: 0.0}
    prev = {}
    visited = set()

    # (mesafe, node_id) min-heap
    heap = [(0.0, source_id)]

    while heap:
        current_dist, u = heapq.heappop(heap)

        if u in visited:
            continue
        visited.add(u)

        if u == target_id:
            break

        # GÜNCELLEME 1: neighbors artık (v, weight, geometry) dönüyor
        # Geometry hesaplamada lazım değil, o yüzden _ ile yoksayıyoruz (ya da geometry değişkenine alıyoruz)
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

    # GÜNCELLEME 2: Detaylı geometriyi (kıvrımları) oluştur
    full_coords = []
    
    for i in range(len(path_nodes) - 1):
        u = path_nodes[i]
        v = path_nodes[i+1]

        # Başlangıç düğümünün koordinatını ekle
        u_info = graph.get_coords(u)
        if u_info:
            full_coords.append(u_info)

        # u -> v arasındaki kenarı bulup geometrisini (kıvrımlarını) ekle
        edge_geometry = []
        for neighbor, weight, geom in graph.neighbors(u):
            if neighbor == v:
                edge_geometry = geom
                break
        
        # Geometri noktalarını listeye ekle
        # geom verisi [[lat, lon], [lat, lon], ...] formatındadır
        for point in edge_geometry:
            full_coords.append({"lat": point[0], "lon": point[1]})

    # En son hedef düğümü de ekle
    target_info = graph.get_coords(target_id)
    if target_info:
        full_coords.append(target_info)

    distance_m = dist[target_id]

    return {
        "path": path_nodes,          # Sadece node ID'leri (debug veya mantıksal işlemler için)
        "path_coords": full_coords,  # Haritada çizilecek tam detaylı koordinatlar
        "distance_m": distance_m,
        "distance_km": round(distance_m / 1000, 3),
        "node_count": len(path_nodes),
    }


def calculate_shortest_path(source_id: str, target_id: str):
    """
    Node ID'leri ile en kısa yol
    """
    return dijkstra_shortest_path(source_id, target_id)


def shortest_path_from_coords(source_lat, source_lon, target_lat, target_lon):
    """
    Koordinat alır, en yakın node'ları bulup Dijkstra çalıştırır.
    """
    graph = load_graph_once()

    s_id = graph.find_nearest_node(source_lat, source_lon)
    t_id = graph.find_nearest_node(target_lat, target_lon)

    if s_id is None or t_id is None:
        return None
    
    # Dijkstra fonksiyonu artık path_coords'u detaylı dolduruyor
    result = dijkstra_shortest_path(s_id, t_id)
    
    if result:
        result["source_node_id"] = s_id
        result["target_node_id"] = t_id

    return result