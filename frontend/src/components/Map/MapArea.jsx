import React from "react";
import { MapContainer, TileLayer, Polyline, Marker, Popup, useMapEvents } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// İkon Ayarı
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.3/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.3/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.3/dist/images/marker-shadow.png",
});

// Tıklama Olayı Bileşeni
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

export default function MapArea({ 
    center, zoom, locations, routeStops, routeResult, tempMarker, 
    activeTab, isMapClickActive, onMapClick, deleteLocation 
}) {
  return (
    <div style={{ flex: 1, position: "relative" }}>
        <MapContainer center={center} zoom={zoom} style={{ height: "100%", width: "100%" }}>
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution='&copy; OSM contributors' />
            
            <MapEvents activeTab={activeTab} isMapClickActive={isMapClickActive} onMapClick={onMapClick} />

            {/* Kayıtlı Lokasyonlar */}
            {locations.map(loc => (
                <Marker key={loc.id} position={[loc.lat, loc.lon]} opacity={0.6}>
                    <Popup>
                        <b>{loc.name}</b><br/>
                        Tür: {loc.type}<br/>
                        <button onClick={() => deleteLocation(loc.id)} style={{marginTop: "5px", color: "red", cursor:"pointer"}}>Sil</button>
                    </Popup>
                </Marker>
            ))}

            {/* Geçici Marker */}
            {tempMarker && <Marker position={tempMarker} opacity={1}><Popup>Seçilen Konum</Popup></Marker>}

            {/* Rotadaki Duraklar */}
            {routeStops.map((stop, i) => (
                <Marker key={`stop-${i}`} position={[stop.lat, stop.lon]}>
                   <Popup>{i+1}. {stop.name}</Popup>
                </Marker>
             ))}

            {/* Çizilen Yol */}
            {routeResult && routeResult.path_coords && (
                <Polyline positions={routeResult.path_coords.map(p => [p.lat, p.lon])} color="blue" weight={5} />
            )}
        </MapContainer>
    </div>
  );
}