from flask import Blueprint, request, jsonify
from models.db import db, Vehicle, Location, VehicleType
from services.route_service import calculate_mixed_vehicle_route, optimize_stop_order

routes_bp = Blueprint("routes", __name__, url_prefix="/api/routes")

# --- ARAÇ TİPLERİ ---
@routes_bp.route("/vehicle-types", methods=["GET"])
def get_vehicle_types():
    types = VehicleType.query.all()
    return jsonify([t.to_dict() for t in types])

# --- ARAÇ İŞLEMLERİ ---
@routes_bp.route("/vehicles", methods=["GET"])
def get_vehicles():
    vehicles = Vehicle.query.all()
    return jsonify([v.to_dict() for v in vehicles])

@routes_bp.route("/vehicles", methods=["POST"])
def add_vehicle():
    data = request.get_json()
    plate = data.get("plate_number")
    type_id = data.get("type_id")

    if not plate or not type_id:
        return jsonify({"error": "Eksik bilgi"}), 400

    if Vehicle.query.filter_by(plate_number=plate).first():
        return jsonify({"error": "Plaka zaten mevcut"}), 400

    new_vehicle = Vehicle(plate_number=plate, vehicle_type_id=type_id)
    db.session.add(new_vehicle)
    db.session.commit()

    return jsonify({"message": "Araç eklendi", "vehicle": new_vehicle.to_dict()}), 201

# YENİ: Araç Silme
@routes_bp.route("/vehicles/<int:id>", methods=["DELETE"])
def delete_vehicle(id):
    vehicle = Vehicle.query.get(id)
    if not vehicle:
        return jsonify({"error": "Araç bulunamadı"}), 404
    
    db.session.delete(vehicle)
    db.session.commit()
    return jsonify({"message": "Araç silindi"}), 200

# --- LOKASYON İŞLEMLERİ ---
@routes_bp.route("/locations", methods=["GET"])
def get_locations():
    locs = Location.query.all()
    return jsonify([l.to_dict() for l in locs])

@routes_bp.route("/locations", methods=["POST"])
def add_location():
    data = request.get_json()
    try:
        new_loc = Location(
            name=data["name"],
            lat=float(data["lat"]),
            lon=float(data["lon"]),
            type=data.get("type", "musteri")
        )
        db.session.add(new_loc)
        db.session.commit()
        return jsonify({"message": "Lokasyon eklendi", "location": new_loc.to_dict()}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# YENİ: Lokasyon Silme
@routes_bp.route("/locations/<int:id>", methods=["DELETE"])
def delete_location(id):
    location = Location.query.get(id)
    if not location:
        return jsonify({"error": "Lokasyon bulunamadı"}), 404
    
    db.session.delete(location)
    db.session.commit()
    return jsonify({"message": "Lokasyon silindi"}), 200

# --- ROTA HESAPLAMA ---
@routes_bp.route("/calculate-mixed", methods=["POST"])
def calculate_mixed():
    data = request.get_json()
    segments = data.get("segments", [])

    if not segments:
        return jsonify({"error": "Rota verisi eksik"}), 400

    result = calculate_mixed_vehicle_route(segments)
    
    if not result:
        return jsonify({"error": "Rota hesaplanamadı"}), 400
        
    return jsonify(result)

# --- ROTA OPTİMİZASYONU ---
@routes_bp.route("/optimize-route", methods=["POST"])
def optimize_route():
    data = request.get_json()
    stops = data.get("stops", [])
    locked_indices = data.get("locked_indices", [])

    if len(stops) < 3:
        return jsonify(stops)

    try:
        fixed_indices = [int(i) for i in locked_indices]
        optimized_stops = optimize_stop_order(stops, fixed_indices)
        return jsonify(optimized_stops)
    except Exception as e:
        print(f"Optimizasyon Hatası: {e}")
        return jsonify({"error": str(e)}), 500