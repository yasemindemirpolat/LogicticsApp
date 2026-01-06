import React, { useState } from "react";
import { styles } from "../UI/Styles";

export default function VehiclePanel({
  newVehiclePlate, setNewVehiclePlate, newVehicleTypeId, setNewVehicleTypeId,
  vehicleTypes, vehicles, saveVehicle, deleteVehicle
}) {
  const [showVehicleForm, setShowVehicleForm] = useState(false);

  return (
    <div style={styles.card}>
      <h4>Filoya Araç Ekle</h4>
      <button onClick={() => setShowVehicleForm(!showVehicleForm)} style={styles.btnToggleOff}>
          {showVehicleForm ? "Formu Gizle" : "+ Yeni Araç"}
      </button>
      
      {showVehicleForm && (
        <div style={{marginBottom: "15px", padding:"10px", background:"#eee", borderRadius:"5px"}}>
            <label>Plaka:</label>
            <input type="text" style={styles.input} value={newVehiclePlate} onChange={e=>setNewVehiclePlate(e.target.value)} placeholder="23 ABC 123" />
            <label>Tip:</label>
            <select style={styles.input} value={newVehicleTypeId} onChange={e=>setNewVehicleTypeId(e.target.value)}>
                <option value="">-- Tip Seç --</option>
                {vehicleTypes.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
            </select>
            <button onClick={saveVehicle} style={styles.btnSuccess}>Kaydet</button>
        </div>
      )}
      
      <hr style={{margin: "15px 0", borderTop: "1px solid #eee"}}/>
      <h5>Mevcut Araçlar</h5>
      <ul style={{fontSize:"13px", paddingLeft:"20px", color:"#555"}}>
        {vehicles.map(v => (
            <li key={v.id} style={{marginBottom: "5px"}}>
                <strong>{v.plate_number}</strong> - {v.type_name}
                <button onClick={() => deleteVehicle(v.id)} style={styles.btnDeleteSmall}>Sil</button>
            </li>
        ))}
      </ul>
    </div>
  );
}