import os
import json
import osmnx as ox
from shapely.geometry import mapping  # <-- Bu gerekli

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

def build_graph_for_city(place_name: str, network_type: str = "drive"):
    print(f"[+] {place_name} için OSM verisi indiriliyor...")
    
    # 1. Grafiği indir
    G = ox.graph_from_place(place_name, network_type=network_type)
    
    nodes = {}
    edges = []

    # Node'ları kaydet
    for node_id, data in G.nodes(data=True):
        nodes[str(node_id)] = {
            "id": str(node_id),
            "lat": data.get("y"),
            "lon": data.get("x"),
        }

    # Edge'leri (Yolları) kaydet
    for u, v, k, data in G.edges(keys=True, data=True):
        distance = data.get("length", None)
        if distance is None:
            continue
        
        # --- YENİ KISIM BAŞLANGIÇ ---
        # Yolun gerçek geometrisini al (varsa)
        coords = []
        if "geometry" in data:
            # Shapely geometry objesini koordinat listesine çevir
            # mapping(data["geometry"]) -> {'type': 'LineString', 'coordinates': [[lon, lat], ...]}
            geo_json = mapping(data["geometry"])
            # GeoJSON koordinatları [lon, lat] şeklindedir, biz [lat, lon] yapacağız
            coords = [[p[1], p[0]] for p in geo_json["coordinates"]]
        # --- YENİ KISIM BİTİŞ ---

        edges.append({
            "from": str(u),
            "to": str(v),
            "distance_m": float(distance),
            "geometry": coords  # <-- Bunu ekledik
        })

    graph_data = {"nodes": nodes, "edges": edges}

    os.makedirs(DATA_DIR, exist_ok=True)
    out_path = os.path.join(DATA_DIR, "graph_elazig.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(graph_data, f, ensure_ascii=False)

    print(f"[+] Graph dosyası kaydedildi: {out_path}")

if __name__ == "__main__":
    build_graph_for_city("Elazig, Turkey")