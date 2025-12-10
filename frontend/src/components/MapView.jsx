// src/components/MapView.jsx
import { useState } from "react";
import {
    MapContainer,
    TileLayer,
    Polyline,
    Marker,
    useMapEvents,
} from "react-leaflet";
import L from "leaflet";
import axios from "axios";

// Marker ikonunun görünmesi için (Vite ile gerekli)
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl:
        "https://unpkg.com/leaflet@1.9.3/dist/images/marker-icon-2x.png",
    iconUrl: "https://unpkg.com/leaflet@1.9.3/dist/images/marker-icon.png",
    shadowUrl: "https://unpkg.com/leaflet@1.9.3/dist/images/marker-shadow.png",
});

// Haritaya tıklamaları yakalayan küçük bileşen
function ClickHandler({ onClick }) {
    useMapEvents({
        click(e) {
            onClick(e.latlng);
        },
    });
    return null;
}

export default function MapView() {
    const [source, setSource] = useState(null);
    const [target, setTarget] = useState(null);
    const [pathCoords, setPathCoords] = useState([]);
    const [info, setInfo] = useState(null);

    async function fetchRoute(s, t) {
        if (!s || !t) return;

        try {
            const res = await axios.post(
                "http://127.0.0.1:5000/api/routes/shortest-path-from-coords",
                {
                    source_lat: s.lat,
                    source_lon: s.lng,
                    target_lat: t.lat,
                    target_lon: t.lng,
                }
            );

            const data = res.data;
            setPathCoords(data.path_coords || []);
            setInfo({
                distanceKm: data.distance_km,
                nodeCount: data.node_count,
            });
        } catch (err) {
            console.error("Rota alınamadı:", err);
            setInfo({ error: "Rota alınamadı" });
            setPathCoords([]);
        }
    }

    function handleMapClick(latlng) {
        // 1. tıklama → başlangıç
        if (!source) {
            setSource(latlng);
            setTarget(null);
            setPathCoords([]);
            setInfo(null);
            return;
        }

        // 2. tıklama → hedef + rota hesapla
        if (!target) {
            const newTarget = latlng;
            setTarget(newTarget);
            fetchRoute(source, newTarget);
            return;
        }

        // 3. tıklama → her şeyi sıfırla, yeni başlangıç olsun
        setSource(latlng);
        setTarget(null);
        setPathCoords([]);
        setInfo(null);
    }

    return (
        <div style={{ padding: "1rem" }}>
            <h2>Logistics Route Planner (OSM + Dijkstra)</h2>
            <p>
                1. tıklama: başlangıç noktası • 2. tıklama: hedef • 3. tıklama:
                sıfırlayıp yeniden başla.
            </p>

            {info && !info.error && (
                <p>
                    Toplam mesafe: <b>{info.distanceKm} km</b> – Node sayısı:{" "}
                    <b>{info.nodeCount}</b>
                </p>
            )}
            {info && info.error && <p style={{ color: "red" }}>{info.error}</p>}

            <MapContainer
                center={[38.68, 39.22]} // Elazığ civarı
                zoom={13}
                style={{ height: "600px", width: "100%", borderRadius: "8px" }}
            >
                <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

                <ClickHandler onClick={handleMapClick} />

                {source && <Marker position={source} />}
                {target && <Marker position={target} />}

                {pathCoords.length > 0 && (
                    <Polyline
                        positions={pathCoords.map((p) => [p.lat, p.lon])}
                        weight={5}
                    />
                )}
            </MapContainer>
        </div>
    );
}
