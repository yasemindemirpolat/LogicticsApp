export const styles = {
    // Layout
    container: { display: "flex", height: "100vh", width: "100%", overflow: "hidden", fontFamily: "sans-serif" },
    leftPanel: { width: "400px", padding: "20px", background: "#f8f9fa", borderRight: "1px solid #ddd", overflowY: "auto", display: "flex", flexDirection: "column", gap: "15px" },
    header: { margin: "0 0 10px 0", color: "#333", borderBottom: "2px solid #ddd", paddingBottom: "10px" },
    card: { background: "white", padding: "15px", borderRadius: "8px", border: "1px solid #e0e0e0", boxShadow: "0 2px 4px rgba(0,0,0,0.05)" },
    row: { display: "flex", gap: "5px" },
    
    // Form Elements
    input: { width: "100%", padding: "8px", marginBottom: "8px", borderRadius: "4px", border: "1px solid #ccc", boxSizing: "border-box" },
    
    // Buttons
    btnPrimary: { width: "100%", padding: "10px", background: "#007bff", color: "white", border: "none", borderRadius: "4px", cursor: "pointer", marginBottom: "5px" },
    btnSuccess: { width: "100%", padding: "10px", background: "#28a745", color: "white", border: "none", borderRadius: "4px", cursor: "pointer" },
    btnDanger: { background: "none", border: "none", color: "#dc3545", cursor: "pointer", fontSize: "14px", textDecoration: "underline" },
    btnDeleteSmall: { background: "#dc3545", color: "white", border: "none", borderRadius: "4px", padding: "2px 6px", cursor: "pointer", fontSize: "12px", marginLeft: "10px" },
    btnSecondary: { width: "100%", padding: "8px", background: "#6f42c1", color: "white", border: "none", borderRadius: "4px", cursor: "pointer", marginBottom: "10px" },
    
    // Toggles
    btnToggleOn: { width: "100%", padding: "8px", background: "#ffc107", color: "black", border: "none", borderRadius: "4px", cursor: "pointer", fontWeight: "bold", marginBottom: "10px" },
    btnToggleOff: { width: "100%", padding: "8px", background: "#6c757d", color: "white", border: "none", borderRadius: "4px", cursor: "pointer", marginBottom: "10px" },
    
    // Specific
    stopBox: { background: "#e9ecef", padding: "10px", borderRadius: "4px", display: "flex", justifyContent: "space-between", alignItems: "center" },
    resultBox: { marginTop: "15px", padding: "15px", background: "#d1e7dd", borderRadius: "8px", border: "1px solid #badbcc" }
};