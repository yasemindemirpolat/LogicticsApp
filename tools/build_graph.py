import os
import json
import osmnx as ox
import networkx as nx   # YENİ


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

def build_graph_for_city(place_name: str, network_type: str = "drive"):
    print(f"[+] {place_name} için OSM verisi indiriliyor...")
    G = ox.graph_from_place(place_name, network_type=network_type)

    G = G.to_undirected()

    nodes = {}
    edges = []

    for node_id, data in G.nodes(data=True):
        nodes[str(node_id)] = {
            "id": str(node_id),
            "lat": data.get("y"),
            "lon": data.get("x"),
        }

    for u, v, data in G.edges(data=True):
        distance = data.get("length", None)
        if distance is None:
            continue

        edges.append({
            "from": str(u),
            "to": str(v),
            "distance_m": float(distance),
        })

    graph_data = {"nodes": nodes, "edges": edges}

    os.makedirs(DATA_DIR, exist_ok=True)
    out_path = os.path.join(DATA_DIR, "graph_elazig.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(graph_data, f, ensure_ascii=False)

    print(f"[+] Graph dosyası kaydedildi: {out_path}")
    print(f"    Node sayısı: {len(nodes)}")
    print(f"    Edge sayısı: {len(edges)}")


if __name__ == "__main__":
    build_graph_for_city("Elazig, Turkey")
