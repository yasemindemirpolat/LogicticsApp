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

        for v, weight in graph.neighbors(u):
            new_dist = current_dist + weight
            if v not in dist or new_dist < dist[v]:
                dist[v] = new_dist
                prev[v] = u
                heapq.heappush(heap, (new_dist, v))

    if target_id not in dist:
        return None

    # Path'i geri kur
    path = []
    cur = target_id
    while cur != source_id:
        path.append(cur)
        cur = prev[cur]
    path.append(source_id)
    path.reverse()

    distance_m = dist[target_id]

    return {
        "path": path,
        "distance_m": distance_m,
        "distance_km": round(distance_m / 1000, 3),
        "node_count": len(path),
    }


def calculate_shortest_path(source_id: str, target_id: str):
    """
    Node ID'leri ile en kısa yol (mevcut endpoint'in kullandığı fonksiyon)
    """
    return dijkstra_shortest_path(source_id, target_id)


# ↓↓↓ YENİ: Koordinattan rota hesaplayan fonksiyon
def shortest_path_from_coords(source_lat, source_lon, target_lat, target_lon):
    """
    4 koordinat alır, en yakın node'ları bulup Dijkstra çalıştırır.
    Sonuçta path'e ek olarak path_coords (lat/lon listesi) döner.
    """
    graph = load_graph_once()

    s_id = graph.find_nearest_node(source_lat, source_lon)
    t_id = graph.find_nearest_node(target_lat, target_lon)

    if s_id is None or t_id is None:
        return None

    base_result = dijkstra_shortest_path(s_id, t_id)
    if base_result is None:
        return None

    # path'teki her node için koordinat listesi oluştur
    coords = []
    for node_id in base_result["path"]:
        info = graph.get_coords(node_id)
        if info:
            coords.append(info)

    # Orijinal sonucu genişleterek döndürelim
    base_result["path_coords"] = coords
    base_result["source_node_id"] = s_id
    base_result["target_node_id"] = t_id

    return base_result


