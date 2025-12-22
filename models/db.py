from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# 1. Araç Tipi (SABİT VERİLER: TIR, Kamyon vb.)
class VehicleType(db.Model):
    __tablename__ = 'vehicle_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True) # Örn: TIR, Motokurye
    speed_kmh = db.Column(db.Float, nullable=False)   # Sabit Hız
    cost_per_km = db.Column(db.Float, nullable=False) # Sabit Maliyet

    # İlişki: Bu tipten türetilen araçları görmek için
    vehicles = db.relationship('Vehicle', backref='type', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "speed_kmh": self.speed_kmh,
            "cost_per_km": self.cost_per_km
        }

# 2. Filodaki Araçlar (KULLANICI EKLER: Plaka vb.)
class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    plate_number = db.Column(db.String(20), nullable=False, unique=True) # Plaka (34MER5757)
    
    # Hangi tipte olduğu (VehicleType tablosuna bağlanır)
    vehicle_type_id = db.Column(db.Integer, db.ForeignKey('vehicle_types.id'), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "plate_number": self.plate_number,
            "type_name": self.type.name,         # İlişkiden gelen veri
            "speed": self.type.speed_kmh,        # İlişkiden gelen veri
            "cost": self.type.cost_per_km        # İlişkiden gelen veri
        }

# 3. Lokasyon Modeli
class Location(db.Model):
    __tablename__ = 'locations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lon = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20)) # 'depo', 'sube', 'musteri'

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "lat": self.lat,
            "lon": self.lon,
            "type": self.type
        }