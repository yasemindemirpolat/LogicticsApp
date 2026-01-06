import React from "react";
import { styles } from "../UI/Styles";  

export default function RoutePanel({ 
  locations, routeStops, vehicles, segmentVehicles, routeResult, 
  selectedLocationId, setSelectedLocationId, 
  addStop, removeStop, toggleLock, lockedIndices, 
  setSegmentVehicles, handleOptimizeRoute, calculateRoute 
}) {
  return (
    <div style={styles.card}>
      <h4>Rota Planlayıcı</h4>
      
      <div style={styles.row}>
        <select style={styles.input} onChange={(e) => setSelectedLocationId(e.target.value)} value={selectedLocationId}>
          <option value="">-- Durak Seç --</option>
          {locations.map(l => <option key={l.id} value={l.id}>{l.name}</option>)}
        </select>
        <button onClick={addStop} style={{...styles.btnPrimary, width: "auto"}}>Ekle</button>
      </div>

      <div style={{maxHeight: "400px", overflowY: "auto", border: "1px solid #eee", padding: "5px", marginBottom: "10px"}}>
        {routeStops.map((stop, i) => {
            const isLocked = lockedIndices.includes(i);
            return (
            <div key={i} style={{marginBottom: "10px"}}>
                <div style={styles.stopBox}>
                    <div style={{display: "flex", alignItems: "center", gap: "10px"}}>
                        <button 
                            onClick={() => toggleLock(i)}
                            style={{background: "none", border: "none", cursor: "pointer", fontSize: "16px", opacity: isLocked ? 1 : 0.3}}
                            title="Sırayı Kilitle/Aç"
                        >
                            {isLocked ? "🔒" : "🔓"}
                        </button>
                        <span>{i+1}. {stop.name}</span>
                    </div>
                    <button onClick={() => removeStop(i)} style={styles.btnDanger}>Çıkar</button>
                </div>
                
                {i < routeStops.length - 1 && (
                    <div style={{textAlign: "center", padding: "5px"}}>
                        <div style={{fontSize:"12px", color:"#666"}}>⬇</div>
                        <select 
                            style={{...styles.input, borderColor: "#007bff", color: "#0056b3", fontSize: "12px", padding: "4px"}}
                            onChange={(e) => setSegmentVehicles({...segmentVehicles, [i]: e.target.value})}
                            value={segmentVehicles[i] || ""}
                        >
                            <option value="">-- Araç Seç --</option>
                            {vehicles.map(v => <option key={v.id} value={v.id}>{v.name} ({v.type_name})</option>)}
                        </select>
                    </div>
                )}
            </div>
        )})}
        {routeStops.length === 0 && <small style={{display:"block", textAlign:"center", color:"#999"}}>Henüz durak yok.</small>}
      </div>

      {routeStops.length > 2 && (
          <button onClick={handleOptimizeRoute} style={styles.btnSecondary}>⚡ Rotayı Optimize Et</button>
      )}

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
  );
}