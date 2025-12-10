# models/graph.py
import json
import os
import math


class Graph:
    def __init__(self):
        # adjacency list: { node_id: [(neighbor_id, distance), ...], ... }
        self.adj = {}
        # node bilgileri: { node_id: { "lat": .., "lon": .. }, ... }
        self.nodes = {}

    def add_edge(self, u, v, weight):
        self.adj.setdefault(u, []).append((v, weight))
        self.adj.setdefault(v, []).append((u, weight))  # çift yönlü yol

    def neighbors(self, u):
        # (komşu node, mesafe_metre)
        return self.adj.get(u, [])

    def load_from_json(self, path: str):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.nodes = data["nodes"]

        for edge in data["edges"]:
            u = edge["from"]
            v = edge["to"]
            w = edge["distance_m"]
            self.add_edge(u, v, w)

    @classmethod
    def from_file(cls, path: str):
        g = cls()
        g.load_from_json(path)
        return g

    # ↓↓↓ YENİ: Koordinata en yakın node'u bul
    def find_nearest_node(self, lat: float, lon: float):
        nearest_id = None
        min_dist = float("inf")

        for node_id, info in self.nodes.items():
            n_lat = info.get("lat")
            n_lon = info.get("lon")
            if n_lat is None or n_lon is None:
                continue

            # Basit Öklid mesafesi (küçük alanlar için yeterli)
            d = math.sqrt((lat - n_lat) ** 2 + (lon - n_lon) ** 2)

            if d < min_dist:
                min_dist = d
                nearest_id = node_id

        return nearest_id

    # ↓↓↓ YENİ: Node ID'den koordinat al
    def get_coords(self, node_id: str):
        info = self.nodes.get(node_id)
        if not info:
            return None
        return {"lat": info["lat"], "lon": info["lon"]}


# Uygulama boyunca bir kere yüklenecek global graph
GRAPH = None


def load_graph_once():
    """
    graph_elazig.json dosyasını ilk çağrıda okuyup belleğe alır.
    Sonraki çağrılarda tekrar dosya okunmaz.
    """
    global GRAPH
    if GRAPH is None:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        graph_path = os.path.join(base_dir, "data", "graph_elazig.json")
        GRAPH = Graph.from_file(graph_path)
    return GRAPH

