import React, { useState, useEffect } from "react";
import { api } from "../services/api";
import { styles } from "../components/UI/styles";

// Bileşenler
import RoutePanel from "../components/Panels/RoutePanel";
import LocationPanel from "../components/Panels/LocationPanel";
import VehiclePanel from "../components/Panels/VehiclePanel";
import MapArea from "../components/Map/MapArea";

export default function Dashboard() {
  // --- STATE'LER ---
  const [activeTab, setActiveTab] = useState("route");
  
  // Veriler
  const [vehicles, setVehicles] = useState([]);
  const [vehicleTypes, setVehicleTypes] = useState([]);
  const [locations, setLocations] = useState([]);

  // Rota Logic
  const [routeStops, setRouteStops] = useState([]);
  const [segmentVehicles, setSegmentVehicles] = useState({});
  const [routeResult, setRouteResult] = useState(null);
  const [selectedLocationId, setSelectedLocationId] = useState("");
  const [lockedIndices, setLockedIndices] = useState([0]);

  // Formlar
  const [newLocName, setNewLocName] = useState("");
  const [newLocLat, setNewLocLat] = useState("");
  const [newLocLon, setNewLocLon] = useState("");
  const [newLocType, setNewLocType] = useState("musteri");
  const [tempMarker, setTempMarker] = useState(null);
  const [isMapClickActive, setIsMapClickActive] = useState(false);

  const [newVehiclePlate, setNewVehiclePlate] = useState("");
  const [newVehicleTypeId, setNewVehicleTypeId] = useState("");

  // --- API İŞLEMLERİ ---
  useEffect(() => {
    refreshData();
  }, []);

  const refreshData = () => {
    api.getVehicleTypes().then(res => setVehicleTypes(res.data));
    api.getVehicles().then(res => setVehicles(res.data));
    api.getLocations().then(res => setLocations(res.data));
  };

  // --- LOGIC: ROTA ---
  const addStop = () => {
    if (!selectedLocationId) return;
    const loc = locations.find(l => l.id == selectedLocationId);
    if (loc) setRouteStops([...routeStops, loc]);
  };

  const removeStop = (index) => {
    const newStops = routeStops.filter((_, i) => i !== index);
    setRouteStops(newStops);
    const newSegments = { ...segmentVehicles };
    delete newSegments[index];
    setSegmentVehicles(newSegments);
    setLockedIndices(lockedIndices.filter(i => i < newStops.length));
  };

  const toggleLock = (index) => {
    if (lockedIndices.includes(index)) {
        setLockedIndices(lockedIndices.filter(i => i !== index));
    } else {
        setLockedIndices([...lockedIndices, index]);
    }
  };

  const handleOptimizeRoute = async () => {
    if (routeStops.length < 3) { alert("En az 3 durak gerekli."); return; }
    try {
      const res = await api.optimizeRoute(routeStops, lockedIndices);
      setRouteStops(res.data);
      setSegmentVehicles({}); 
      alert("Rota optimize edildi!");
    } catch (err) { alert("Hata: " + err.message); }
  };

  const calculateRoute = async () => {
    if (routeStops.length < 2) { alert("En az 2 durak gerekli."); return; }
    const segments = [];
    for (let i = 0; i < routeStops.length - 1; i++) {
        const vId = segmentVehicles[i];
        if (!vId) { alert(`${i+1}. yolculuk için araç seçilmedi!`); return; }
        segments.push({
            start: { lat: routeStops[i].lat, lon: routeStops[i].lon },
            end: { lat: routeStops[i+1].lat, lon: routeStops[i+1].lon },
            vehicle_id: vId
        });
    }
    try {
        const res = await api.calculateRoute(segments);
        setRouteResult(res.data);
    } catch (err) { alert("Hata: " + (err.response?.data?.error || err.message)); }
  };

  // --- LOGIC: KAYIT/SILME ---
  const saveLocation = async () => {
      if (!newLocName || !newLocLat || !newLocLon) { alert("Eksik bilgi"); return; }
      try {
          await api.addLocation({ name: newLocName, lat: parseFloat(newLocLat), lon: parseFloat(newLocLon), type: newLocType });
          alert("Kaydedildi."); setNewLocName(""); setNewLocLat(""); setNewLocLon(""); setTempMarker(null); refreshData();
      } catch(e) { alert("Hata"); }
  };

  const deleteLocation = async (id) => {
    if(!window.confirm("Silmek istediğine emin misin?")) return;
    try { await api.deleteLocation(id); setRouteStops(routeStops.filter(s => s.id !== id)); refreshData(); } catch(e) { alert(e.message); }
  };

  const saveVehicle = async () => {
      if(!newVehiclePlate || !newVehicleTypeId) { alert("Eksik bilgi"); return; }
      try {
          await api.addVehicle({ plate_number: newVehiclePlate, type_id: newVehicleTypeId });
          alert("Eklendi."); setNewVehiclePlate(""); setNewVehicleTypeId(""); refreshData();
      } catch(e) { alert(e.message); }
  };

  const deleteVehicle = async (id) => {
    if(!window.confirm("Silmek istediğine emin misin?")) return;
    try { await api.deleteVehicle(id); refreshData(); } catch(e) { alert(e.message); }
  };

  const handleMapClick = (latlng) => {
    setNewLocLat(latlng.lat);
    setNewLocLon(latlng.lng);
    setTempMarker(latlng);
    setIsMapClickActive(false);
  };

  // --- RENDER ---
  return (
    <div style={styles.container}>
      {/* SOL MENÜ */}
      <div style={styles.leftPanel}>
        <h2 style={styles.header}>Lojistik Panel v5</h2>

        {/* Sekme Butonları */}
        <div style={{ display: "flex", marginBottom: "10px", gap: "5px" }}>
            <button onClick={() => setActiveTab("route")} style={activeTab === "route" ? {...styles.btnPrimary, background:"#0056b3"} : styles.btnSecondary}>🗺️ Rota</button>
            <button onClick={() => setActiveTab("location")} style={activeTab === "location" ? {...styles.btnPrimary, background:"#0056b3"} : styles.btnSecondary}>📍 Lokasyon</button>
            <button onClick={() => setActiveTab("vehicle")} style={activeTab === "vehicle" ? {...styles.btnPrimary, background:"#0056b3"} : styles.btnSecondary}>🚛 Araç</button>
        </div>

        {/* Sekme İçerikleri */}
        {activeTab === "route" && (
            <RoutePanel 
                locations={locations} routeStops={routeStops} vehicles={vehicles} 
                segmentVehicles={segmentVehicles} routeResult={routeResult}
                selectedLocationId={selectedLocationId} setSelectedLocationId={setSelectedLocationId}
                addStop={addStop} removeStop={removeStop} toggleLock={toggleLock} lockedIndices={lockedIndices}
                setSegmentVehicles={setSegmentVehicles} handleOptimizeRoute={handleOptimizeRoute} calculateRoute={calculateRoute}
            />
        )}

        {activeTab === "location" && (
            <LocationPanel 
                newLocName={newLocName} setNewLocName={setNewLocName}
                newLocLat={newLocLat} setNewLocLat={setNewLocLat}
                newLocLon={newLocLon} setNewLocLon={setNewLocLon}
                newLocType={newLocType} setNewLocType={setNewLocType}
                isMapClickActive={isMapClickActive} setIsMapClickActive={setIsMapClickActive}
                saveLocation={saveLocation} locations={locations} deleteLocation={deleteLocation}
            />
        )}

        {activeTab === "vehicle" && (
            <VehiclePanel 
                newVehiclePlate={newVehiclePlate} setNewVehiclePlate={setNewVehiclePlate}
                newVehicleTypeId={newVehicleTypeId} setNewVehicleTypeId={setNewVehicleTypeId}
                vehicleTypes={vehicleTypes} vehicles={vehicles}
                saveVehicle={saveVehicle} deleteVehicle={deleteVehicle}
            />
        )}
      </div>

      {/* HARİTA */}
      <MapArea 
        center={[38.68, 39.22]} zoom={13}
        locations={locations} routeStops={routeStops} routeResult={routeResult} tempMarker={tempMarker}
        activeTab={activeTab} isMapClickActive={isMapClickActive} onMapClick={handleMapClick} deleteLocation={deleteLocation}
      />
    </div>
  );
}