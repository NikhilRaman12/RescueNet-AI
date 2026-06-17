import { useState } from "react";
import "./style.css";

const API_BASE = "https://notebooks.amd.com/jupyter-hack-team-460-260613172454-7ef4aaf3/proxy/8030";

export default function App() {
  const [location, setLocation] = useState("Hyderabad");
  const [output, setOutput] = useState(null);
  const [loading, setLoading] = useState(false);

  const CITY_LIST = [
    "Hyderabad","Chennai","Bangalore","Mumbai","Delhi","Kolkata",
    "Pune","Ahmedabad","Jaipur","Lucknow","Bhopal","Patna",
    "Nagpur","Indore","Coimbatore","Kochi","Surat","Chandigarh",
    "Vijayawada","Visakhapatnam"
  ];

  const runMission = async () => {
    setLoading(true);
    setOutput(null);

    try {
      const res = await fetch(`${API_BASE}/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          location,
          disaster_type: "flood",
          query: "Flood alert near river zone"
        })
      });

      const data = await res.json();
      setOutput(data);
    } catch (err) {
      setOutput({ error: "Failed to connect backend" });
    }

    setLoading(false);
  };

  return (
    <div className="container">
      <h1>RescueNet AI</h1>

      <div className="section">
        <label>Select Location</label>
        <select value={location} onChange={(e) => setLocation(e.target.value)}>
          {CITY_LIST.map(city => (
            <option key={city} value={city}>{city}</option>
          ))}
        </select>

        <button onClick={runMission}>
          {loading ? "Running..." : "Run Multi-Agent Rescue"}
        </button>
      </div>

      <div className="output">
        <h2>Mission Output</h2>
        {output ? (
          <pre>{JSON.stringify(output, null, 2)}</pre>
        ) : (
          <p>No output yet</p>
        )}
      </div>
    </div>
  );
}
