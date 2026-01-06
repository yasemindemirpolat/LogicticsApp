import React from "react";
import { styles } from "../UI/Styles";

export default function LocationPanel({
  newLocName, setNewLocName, newLocLat, setNewLocLat, newLocLon, setNewLocLon,
  newLocType, setNewLocType, isMapClickActive, setIsMapClickActive,
  saveLocation, locations, deleteLocation
}) {
  return (
    <div style={styles.card}>
      <h4>Yeni Lokasyon Ekle</h4>
      <button 
        onClick={() => setIsMapClickActive(!isMapClickActive)}
        style={isMapClickActive ? styles.btnToggleOn : styles.btnToggleOff}
      >
        {isMapClickActive ? "Seçim Aktif (İptal)" : "🖱️ Haritadan Seç"}
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

      <hr style={{margin: "15px 0", borderTop: "1px solid #eee"}}/>
      <h5>Kayıtlı Lokasyonlar</h5>
      <ul style={{fontSize:"13px", paddingLeft:"20px", color:"#555"}}>
        {locations.map(l => (
            <li key={l.id} style={{marginBottom: "5px"}}>
                <strong>{l.name}</strong> ({l.type})
                <button onClick={() => deleteLocation(l.id)} style={styles.btnDeleteSmall}>Sil</button>
            </li>
        ))}
      </ul>
    </div>
  );
}