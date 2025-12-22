import os
from flask import Flask
from flask_cors import CORS
from models.db import db, Vehicle, Location, VehicleType # Yeni importlar
from routes.health import health_bp
from routes.routes_api import routes_bp

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # PostgreSQL Ayarları (Senin şifrenle)
    DB_USER = "postgres"
    DB_PASS = "1234" 
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_NAME = "logistics_db"

    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    app.register_blueprint(health_bp)
    app.register_blueprint(routes_bp)

    @app.route("/")
    def home():
        return "Logistics backend çalışıyor!"

    with app.app_context():
        # Bu satır veritabanindaki tablolari sifirlar
        #db.drop_all()#
        
        db.create_all()
        seed_data()

    return app

def seed_data():
    """Sabit verileri (Araç Tipleri ve Lokasyonlar) ekler"""
    
    # 1. Araç Tiplerini Ekle (Eğer yoksa)
    if not VehicleType.query.first():
        print("Araç tipleri ekleniyor...")
        types = [
            VehicleType(name="Motosiklet", speed_kmh=70, cost_per_km=3.0),
            VehicleType(name="Hafif Ticari", speed_kmh=60, cost_per_km=6.0),
            VehicleType(name="Kamyon", speed_kmh=50, cost_per_km=12.0),
            VehicleType(name="TIR", speed_kmh=40, cost_per_km=18.0)
        ]
        db.session.add_all(types)
        db.session.commit()

        # Örnek Bir Araç Ekle (TIR tipinde)
        tir_type = VehicleType.query.filter_by(name="TIR").first()
        v1 = Vehicle(plate_number="23ELZ123", vehicle_type_id=tir_type.id)
        db.session.add(v1)

    # 2. Lokasyonları Ekle
    if not Location.query.first():
        print("Lokasyonlar ekleniyor...")
        locs = [
            Location(name="Ana Lojistik Merkezi", lat=38.681, lon=39.225, type="depo"),
            Location(name="Çarşı Şube", lat=38.675, lon=39.210, type="sube"),
            Location(name="Sanayi Toplama", lat=38.650, lon=39.250, type="toplama"),
            Location(name="Fırat Üniversitesi", lat=38.680, lon=39.195, type="musteri")
        ]
        db.session.add_all(locs)
    
    db.session.commit()
    print("Veritabanı seed işlemi tamamlandı.")

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)