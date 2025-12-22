import { useState, useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  Polyline,
  Marker,
  Popup,
  useMapEvents,
} from "react-leaflet";
import L from "leaflet";
import axios from "axios";
import "leaflet/dist/leaflet.css";

// --- STİLLER (En Başta Tanımlı - Hata Riskini Önler) ---
const styles = {
  container: { display: "flex", height: "100vh", width: "100%", overflow: "hidden", fontFamily: "sans-serif" },
  leftPanel: { width: "400px", padding: "20px", background: "#f8f9fa", borderRight: "1px solid #ddd", overflowY: "auto", display: "flex", flexDirection: "column", gap: "15px" },
  header: { margin: "0 0 10px 0", color: "#333", borderBottom: "2px solid #ddd", paddingBottom: "10px" },
  card: { background: "white", padding: "15px", borderRadius: "8px", border: "1px solid #e0e0e0", boxShadow: "0 2px 4px rgba(0,0,0,0.05)" },
  input: { width: "100%", padding: "8px", marginBottom: "8px", borderRadius: "4px", border: "1px solid #ccc", boxSizing: "border-box" },
  row: { display: "flex", gap: "5px" },
  
  // Butonlar
  tabContainer: { display: "flex", marginBottom: "10px", gap: "5px" },
  tabBtn: { flex: 1, padding: "10px", border: "1px solid #ccc", background: "#eee", cursor: "pointer", borderRadius: "4px" },
  activeTabBtn: { flex: 1, padding: "10px", border: "1px solid #007bff", background: "#007bff", color: "white", cursor: "pointer", fontWeight: "bold", borderRadius: "4px" },
  
  btnPrimary: { width: "100%", padding: "10px", background: "#007bff", color: "white", border: "none", borderRadius: "4px", cursor: "pointer", marginBottom: "5px" },
  btnSuccess: { width: "100%", padding: "10px", background: "#28a745", color: "white", border: "none", borderRadius: "4px", cursor: "pointer" },
  btnDanger: { background: "none", border: "none", color: "#dc3545", cursor: "pointer", fontSize: "14px", textDecoration: "underline" },
  btnToggleOn: { width: "100%", padding: "8px", background: "#ffc107", color: "black", border: "none", borderRadius: "4px", cursor: "pointer", fontWeight: "bold", marginBottom: "10px" },
  btnToggleOff: { width: "100%", padding: "8px", background: "#6c757d", color: "white", border: "none", borderRadius: "4px", cursor: "pointer", marginBottom: "10px" },
  
  resultBox: { marginTop: "15px", padding: "15px", background: "#d1e7dd", borderRadius: "8px", border: "1px solid #badbcc" }
};

// --- İKON DÜZELTMESİ ---
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.3/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.3/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.3/dist/images/marker-shadow.png",
});

const API_URL = "http://127.0.0.1:5000/api/routes";

// --- HARİTA TIKLAMA BİLEŞENİ (Dışarı alındı) ---
const MapEvents = ({ activeTab, isMapClickActive, onMapClick }) => {
  useMapEvents({
    click(e) {
      if (activeTab === "location" && isMapClickActive) {
        onMapClick(e.latlng);
      }
    },
  });
  return null;
};

export default function MapView() {
  const [activeTab, setActiveTab] = useState("route"); // route, location, vehicle
  
  // Veriler
  const [vehicles, setVehicles] = useState([]);
  const [vehicleTypes, setVehicleTypes] = useState([]);
  const [locations, setLocations] = useState([]);

  // Rota State'leri
  const [routeStops, setRouteStops] = useState([]);
  const [segmentVehicles, setSegmentVehicles] = useState({});
  const [routeResult, setRouteResult] = useState(null);
  const [selectedLocationId, setSelectedLocationId] = useState("");

  // Lokasyon Ekleme State'leri
  const [newLocName, setNewLocName] = useState("");
  const [newLocLat, setNewLocLat] = useState("");
  const [newLocLon, setNewLocLon] = useState("");
  const [newLocType, setNewLocType] = useState("musteri");
  const [tempMarker, setTempMarker] = useState(null);
  const [isMapClickActive, setIsMapClickActive] = useState(false);

  // Araç Ekleme State'leri
  const [newVehiclePlate, setNewVehiclePlate] = useState("");
  const [newVehicleTypeId, setNewVehicleTypeId] = useState("");

  // --- VERİ YÜKLEME ---
  useEffect(() => {
    refreshData();
  }, []);

  const refreshData = () => {
    axios.get(`${API_URL}/vehicle-types`).then((res) => setVehicleTypes(res.data));
    axios.get(`${API_URL}/vehicles`).then((res) => setVehicles(res.data));
    axios.get(`${API_URL}/locations`).then((res) => setLocations(res.data));
  };

  // --- HARİTA TIKLAMA İŞLEVİ ---
  const handleMapClick = (latlng) => {
    setNewLocLat(latlng.lat);
    setNewLocLon(latlng.lng);
    setTempMarker(latlng);
    setIsMapClickActive(false); // Seçimden sonra modu kapat
  };

  // --- ROTA İŞLEMLERİ ---
  const addStop = () => {
    if (!selectedLocationId) return;
    const loc = locations.find(l => l.id == selectedLocationId);
    if (loc) setRouteStops([...routeStops, loc]);
  };

  const removeStop = (index) => {
    const newStops = routeStops.filter((_, i) => i !== index);
    setRouteStops(newStops);
    // Segmentleri de temizle
    const newSegments = { ...segmentVehicles };
    delete newSegments[index];
    setSegmentVehicles(newSegments);
  };

  const calculateRoute = async () => {
    if (routeStops.length < 2) {
        alert("En az 2 durak eklemelisiniz!");
        return;
    }

    const segments = [];
    for (let i = 0; i < routeStops.length - 1; i++) {
        const vId = segmentVehicles[i];
        if (!vId) {
            alert(`${i+1}. yolculuk için araç seçilmedi!`);
            return;
        }
        segments.push({
            start: { lat: routeStops[i].lat, lon: routeStops[i].lon },
            end: { lat: routeStops[i+1].lat, lon: routeStops[i+1].lon },
            vehicle_id: vId
        });
    }

    try {
        const res = await axios.post(`${API_URL}/calculate-mixed`, { segments });
        setRouteResult(res.data);
    } catch (err) {
        alert("Hata: " + (err.response?.data?.error || err.message));
    }
  };

  // --- KAYIT İŞLEMLERİ ---
  const saveLocation = async () => {
      if (!newLocName || !newLocLat || !newLocLon) {
          alert("Tüm alanları doldurun."); return;
      }
      try {
          await axios.post(`${API_URL}/locations`, {
              name: newLocName, lat: parseFloat(newLocLat), lon: parseFloat(newLocLon), type: newLocType
          });
          alert("Lokasyon Kaydedildi.");
          setNewLocName(""); setNewLocLat(""); setNewLocLon(""); setTempMarker(null);
          refreshData();
      } catch(e) { alert("Hata: " + e.message); }
  };

  const saveVehicle = async () => {
      if(!newVehiclePlate || !newVehicleTypeId) { alert("Eksik bilgi"); return; }
      try {
          await axios.post(`${API_URL}/vehicles`, { plate_number: newVehiclePlate, type_id: newVehicleTypeId });
          alert("Araç Eklendi.");
          setNewVehiclePlate(""); setNewVehicleTypeId(""); refreshData();
      } catch(e) { alert("Hata: " + e.message); }
  };

  return (
    <div style={styles.container}>
      
      {/* SOL PANEL */}
      <div style={styles.leftPanel}>
        <h2 style={styles.header}>Lojistik Panel v2</h2>

        {/* Sekmeler */}
        <div style={styles.tabContainer}>
            <button onClick={() => setActiveTab("route")} style={activeTab === "route" ? styles.activeTabBtn : styles.tabBtn}>🗺️ Rota</button>
            <button onClick={() => setActiveTab("location")} style={activeTab === "location" ? styles.activeTabBtn : styles.tabBtn}>📍 Lokasyon</button>
            <button onClick={() => setActiveTab("vehicle")} style={activeTab === "vehicle" ? styles.activeTabBtn : styles.tabBtn}>🚛 Araç</button>
        </div>

        {/* --- TAB 1: ROTA --- */}
        {activeTab === "route" && (
            <div style={styles.card}>
                <h4>Rota Planlayıcı</h4>
                
                <div style={styles.row}>
                    <select style={styles.input} onChange={(e) => setSelectedLocationId(e.target.value)} value={selectedLocationId}>
                        <option value="">-- Durak Seç --</option>
                        {locations.map(l => <option key={l.id} value={l.id}>{l.name}</option>)}
                    </select>
                    <button onClick={addStop} style={{...styles.btnPrimary, width: "auto"}}>Ekle</button>
                </div>

                <div style={{maxHeight: "300px", overflowY: "auto", border: "1px solid #eee", padding: "5px", marginBottom: "10px"}}>
                    {routeStops.map((stop, i) => (
                        <div key={i} style={{marginBottom: "10px"}}>
                            <div style={{display:"flex", justifyContent:"space-between", background:"#eee", padding:"5px", borderRadius:"4px"}}>
                                <span>{i+1}. {stop.name}</span>
                                <button onClick={() => removeStop(i)} style={styles.btnDanger}>Sil</button>
                            </div>
                            
                            {/* Segment Aracı Seçimi */}
                            {i < routeStops.length - 1 && (
                                <div style={{textAlign: "center", padding: "5px"}}>
                                    <div style={{fontSize:"12px", color:"#666"}}>⬇ Bu arası hangi araçla? ⬇</div>
                                    <select 
                                        style={{...styles.input, borderColor: "#007bff", color: "#0056b3"}}
                                        onChange={(e) => setSegmentVehicles({...segmentVehicles, [i]: e.target.value})}
                                        value={segmentVehicles[i] || ""}
                                    >
                                        <option value="">-- Araç Seç --</option>
                                        {vehicles.map(v => <option key={v.id} value={v.id}>{v.name} ({v.type_name})</option>)}
                                    </select>
                                </div>
                            )}
                        </div>
                    ))}
                    {routeStops.length === 0 && <small style={{display:"block", textAlign:"center", color:"#999"}}>Henüz durak yok.</small>}
                </div>

                <button onClick={calculateRoute} style={styles.btnSuccess}>ROTAYI HESAPLA 🚀</button>

                {routeResult && (
                    <div style={styles.resultBox}>
                        <h4 style={{margin:"0 0 10px 0"}}>Sonuçlar</h4>
                        <div>🛣️ Mesafe: <strong>{routeResult.total_distance_km} km</strong></div>
                        <div>⏱️ Süre: <strong>{routeResult.estimated_time_min} dk</strong></div>
                        <div>💰 Maliyet: <strong>{routeResult.total_cost_tl} TL</strong></div>
                    </div>
                )}
            </div>
        )}

        {/* --- TAB 2: LOKASYON --- */}
        {activeTab === "location" && (
            <div style={styles.card}>
                <h4>Yeni Lokasyon Ekle</h4>
                
                <button 
                    onClick={() => setIsMapClickActive(!isMapClickActive)}
                    style={isMapClickActive ? styles.btnToggleOn : styles.btnToggleOff}
                >
                    {isMapClickActive ? "Harita Seçimi Aktif (İptal et)" : "🖱️ Haritadan Seçmek İçin Tıkla"}
                </button>

                <label>Lokasyon Adı:</label>
                <input type="text" style={styles.input} value={newLocName} onChange={e=>setNewLocName(e.target.value)} placeholder="Örn: Kuzey Depo" />
                
                <div style={styles.row}>
                    <div><label>Enlem:</label><input type="number" style={styles.input} value={newLocLat} onChange={e=>setNewLocLat(e.target.value)} /></div>
                    <div><label>Boylam:</label><input type="number" style={styles.input} value={newLocLon} onChange={e=>setNewLocLon(e.target.value)} /></div>
                </div>

                <label>Tip:</label>
                <select style={styles.input} value={newLocType} onChange={e=>setNewLocType(e.target.value)}>
                    <option value="musteri">Müşteri</option>
                    <option value="depo">Depo</option>
                    <option value="sube">Şube</option>
                    <option value="toplama">Toplama Merkezi</option>
                </select>

                <button onClick={saveLocation} style={styles.btnPrimary}>Kaydet</button>
            </div>
        )}

        {/* --- TAB 3: ARAÇ --- */}
        {activeTab === "vehicle" && (
            <div style={styles.card}>
                <h4>Filoya Araç Ekle</h4>
                <label>Plaka:</label>
                <input type="text" style={styles.input} value={newVehiclePlate} onChange={e=>setNewVehiclePlate(e.target.value)} placeholder="23 ABC 123" />
                
                <label>Araç Tipi:</label>
                <select style={styles.input} value={newVehicleTypeId} onChange={e=>setNewVehicleTypeId(e.target.value)}>
                    <option value="">-- Tip Seç --</option>
                    {vehicleTypes.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
                </select>
                
                <button onClick={saveVehicle} style={styles.btnSuccess}>Aracı Kaydet</button>
                
                <hr style={{margin: "15px 0", borderTop: "1px solid #eee"}}/>
                <h5>Mevcut Araçlar</h5>
                <ul style={{fontSize:"13px", paddingLeft:"20px", color:"#555"}}>
                    {vehicles.map(v => <li key={v.id}><strong>{v.plate_number}</strong> - {v.type_name}</li>)}
                </ul>
            </div>
        )}
      </div>

      {/* SAĞ PANEL: HARİTA */}
      <div style={{ flex: 1, position: "relative" }}>
        <MapContainer center={[38.68, 39.22]} zoom={13} style={{ height: "100%", width: "100%" }}>
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution='&copy; OSM contributors' />
            
            <MapEvents activeTab={activeTab} isMapClickActive={isMapClickActive} onMapClick={handleMapClick} />

            {/* Kayıtlı Yerler */}
            {locations.map(loc => (
                <Marker key={loc.id} position={[loc.lat, loc.lon]} opacity={0.6}>
                    <Popup><b>{loc.name}</b><br/>{loc.type}</Popup>
                </Marker>
            ))}

            {/* Geçici Yer (Kırmızı) */}
            {tempMarker && <Marker position={tempMarker} opacity={1}><Popup>Seçilen Konum</Popup></Marker>}

            {/* Rota */}
            {routeResult && routeResult.path_coords && (
                <Polyline positions={routeResult.path_coords.map(p => [p.lat, p.lon])} color="blue" weight={5} />
            )}
        </MapContainer>
      </div>
    </div>
  );
}