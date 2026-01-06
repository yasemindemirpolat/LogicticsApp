import axios from "axios";

const API_URL = "http://127.0.0.1:5000/api/routes";

export const api = {
  // --- GET ---
  getVehicleTypes: () => axios.get(`${API_URL}/vehicle-types`),
  getVehicles: () => axios.get(`${API_URL}/vehicles`),
  getLocations: () => axios.get(`${API_URL}/locations`),

  // --- POST ---
  addVehicle: (data) => axios.post(`${API_URL}/vehicles`, data),
  addLocation: (data) => axios.post(`${API_URL}/locations`, data),
  
  // --- DELETE ---
  deleteVehicle: (id) => axios.delete(`${API_URL}/vehicles/${id}`),
  deleteLocation: (id) => axios.delete(`${API_URL}/locations/${id}`),

  // --- HESAPLAMALAR ---
  calculateRoute: (segments) => axios.post(`${API_URL}/calculate-mixed`, { segments }),
  optimizeRoute: (stops, lockedIndices) => 
    axios.post(`${API_URL}/optimize-route`, { stops, locked_indices: lockedIndices }),
};