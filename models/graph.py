import json
import os
import math

class Graph:
    def __init__(self):
        # adjacency list yapısı değişti: 
        # { node_id: [(neighbor_id, distance, geometry_list), ...], ... }
        self.adj = {}
        # node bilgileri: { node_id: { "lat": .., "lon": .. }, ... }
        self.nodes = {}

    def add_edge(self, u, v, weight, geometry=None):
        """
        Kenar ekler. 
        geometry: [[lat, lon], [lat, lon], ...] şeklindeki ara noktalar listesi.
        """
        if geometry is None:
            geometry = []
            
        # YENİ: Artık tuple içinde 3. eleman olarak geometry'i de saklıyoruz.
        self.adj.setdefault(u, []).append((v, weight, geometry))
        
        # DİKKAT: Tek yönlü yol kurallarını ihlal etmemek için
        # aşağıdaki ters yön ekleme satırını SİLDİK.
        # self.adj.setdefault(v, []).append((u, weight))  <-- SİLİNDİ

    def neighbors(self, u):
        """
        Komşuları döndürür.
        Return format: [(neighbor_id, distance, geometry), ...]
        """
        return self.adj.get(u, [])

    def load_from_json(self, path: str):
        if not os.path.exists(path):
            print(f"[UYARI] '{path}' dosyası bulunamadı. Önce 'tools/build_graph.py' çalıştırın.")
            return

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.nodes = data["nodes"]

        for edge in data["edges"]:
            u = edge["from"]
            v = edge["to"]
            w = edge["distance_m"]
            # YENİ: JSON'dan geometry verisini alıyoruz (varsa)
            geom = edge.get("geometry", []) 
            
            self.add_edge(u, v, w, geom)

    @classmethod
    def from_file(cls, path: str):
        g = cls()
        g.load_from_json(path)
        return g

    # Koordinata en yakın node'u bul (Öklid mesafesi ile)
    def find_nearest_node(self, lat: float, lon: float):
        nearest_id = None
        min_dist = float("inf")

        for node_id, info in self.nodes.items():
            n_lat = info.get("lat")
            n_lon = info.get("lon")
            if n_lat is None or n_lon is None:
                continue

            # Basit Öklid mesafesi
            d = math.sqrt((lat - n_lat) ** 2 + (lon - n_lon) ** 2)

            if d < min_dist:
                min_dist = d
                nearest_id = node_id

        return nearest_id

    # Node ID'den koordinat al
    def get_coords(self, node_id: str):
        info = self.nodes.get(node_id)
        if not info:
            return None
        return {"lat": info["lat"], "lon": info["lon"]}


# Uygulama boyunca bir kere yüklenecek global graph
GRAPH = None

def load_graph_once():
    """
    Graph verisini bir kez yükleyip bellekte tutar (Singleton).
    """
    global GRAPH
    if GRAPH is None:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        graph_path = os.path.join(base_dir, "data", "graph_elazig.json")
        GRAPH = Graph.from_file(graph_path)
    return GRAPH