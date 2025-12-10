# routes/routes_api.py
from flask import Blueprint, request, jsonify
from services.route_service import (
    calculate_shortest_path,
    shortest_path_from_coords,
)

routes_bp = Blueprint("routes", __name__, url_prefix="/api/routes")


@routes_bp.route("/shortest-path", methods=["POST"])
def shortest_path():
    """
    Body (JSON):
    {
      "source": "1515064755",
      "target": "1621252010"
    }
    """
    data = request.get_json() or {}
    source = data.get("source")
    target = data.get("target")

    if not source or not target:
        return jsonify({"error": "source ve target zorunlu"}), 400

    result = calculate_shortest_path(str(source), str(target))

    if result is None:
        return jsonify({"error": "Geçerli bir yol bulunamadı veya node id'leri hatalı."}), 404

    return jsonify(result)


# ↓↓↓ YENİ ENDPOINT: Koordinat ile rota hesaplama
@routes_bp.route("/shortest-path-from-coords", methods=["POST"])
def shortest_path_from_coords_endpoint():
    """
    Body (JSON):
    {
      "source_lat": 38.68,
      "source_lon": 39.22,
      "target_lat": 38.70,
      "target_lon": 39.25
    }
    """
    data = request.get_json() or {}

    try:
        s_lat = float(data.get("source_lat"))
        s_lon = float(data.get("source_lon"))
        t_lat = float(data.get("target_lat"))
        t_lon = float(data.get("target_lon"))
    except (TypeError, ValueError):
        return jsonify({"error": "Koordinatlar sayı olmalı"}), 400

    result = shortest_path_from_coords(s_lat, s_lon, t_lat, t_lon)
    if result is None:
        return jsonify({"error": "Rota bulunamadı"}), 404

    return jsonify(result)



