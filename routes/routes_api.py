from flask import Blueprint, request, jsonify
from models.db import db, Vehicle, Location, VehicleType
from services.route_service import calculate_multi_stop_route

routes_bp = Blueprint("routes", __name__, url_prefix="/api/routes")

# --- ARAÇ TİPLERİ (Dropdown için) ---
@routes_bp.route("/vehicle-types", methods=["GET"])
def get_vehicle_types():
    types = VehicleType.query.all()
    return jsonify([t.to_dict() for t in types])

# --- ARAÇ İŞLEMLERİ ---
@routes_bp.route("/vehicles", methods=["GET"])
def get_vehicles():
    # Sistemdeki kayıtlı araçları listele
    vehicles = Vehicle.query.all()
    return jsonify([v.to_dict() for v in vehicles])

@routes_bp.route("/vehicles", methods=["POST"])
def add_vehicle():
    # Body: { "plate_number": "34MER57", "type_id": 1 }
    data = request.get_json()
    plate = data.get("plate_number")
    type_id = data.get("type_id")

    if not plate or not type_id:
        return jsonify({"error": "Plaka ve Araç Tipi zorunludur"}), 400

    # Aynı plaka var mı kontrol et
    if Vehicle.query.filter_by(plate_number=plate).first():
        return jsonify({"error": "Bu plaka zaten kayıtlı"}), 400

    new_vehicle = Vehicle(plate_number=plate, vehicle_type_id=type_id)
    db.session.add(new_vehicle)
    db.session.commit()

    return jsonify({"message": "Araç başarıyla eklendi", "vehicle": new_vehicle.to_dict()}), 201

# --- LOKASYON İŞLEMLERİ ---
@routes_bp.route("/locations", methods=["GET"])
def get_locations():
    locs = Location.query.all()
    return jsonify([l.to_dict() for l in locs])

@routes_bp.route("/locations", methods=["POST"])
def add_location():
    # Body: { "name": "Yeni Depo", "lat": 38.123, "lon": 39.123, "type": "depo" }
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

# --- ROTA HESAPLAMA ---
@routes_bp.route("/calculate-multi", methods=["POST"])
def calculate_multi():
    data = request.get_json()
    # Body: { "stops": [...], "vehicle_id": 5 } (Buradaki ID, 'Vehicle' tablosundaki ID'dir)
    
    stops = data.get("stops", [])
    vehicle_id = data.get("vehicle_id")
    
    # Seçilen aracı bul
    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        return jsonify({"error": "Araç bulunamadı"}), 400
        
    # Hız ve maliyet bilgilerini aracın "TİPİNDEN" alıyoruz
    speed = vehicle.type.speed_kmh
    cost = vehicle.type.cost_per_km
    
    result = calculate_multi_stop_route(stops, speed, cost)
    
    if not result:
        return jsonify({"error": "Rota hesaplanamadı"}), 400
        
    return jsonify(result)