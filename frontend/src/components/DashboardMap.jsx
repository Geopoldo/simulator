import React, { memo } from "react";
import { ComposableMap, Geographies, Geography, Marker, ZoomableGroup } from "react-simple-maps";

const GEO_URL = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json";

const DashboardMap = ({ data }) => {
    // Extract points from data
    const markers = data
        .filter(r => (r.latitude && r.longitude) || (r._Geopoint_latitude && r._Geopoint_longitude) || r._Geopoint_value || r.Geopoint)
        .map((r, i) => {
            // Parse generic ODK Geopoint string "lat lon alt acc" if needed, 
            // but usually converted to columns.
            // If generic "geopoint" column:
            let lat = null, lon = null;

            // Check standard ODK geopoint field often named 'Geopoint' or similar
            const geoStr = r.Geopoint || r.GPS || r._Geopoint_value; // Fallback
            if (geoStr && typeof geoStr === 'string' && geoStr.includes(' ')) {
                const parts = geoStr.split(' ');
                lat = parseFloat(parts[0]);
                lon = parseFloat(parts[1]);
            } else if (r.latitude && r.longitude) {
                lat = parseFloat(r.latitude);
                lon = parseFloat(r.longitude);
            }
            // Simulator generates "geopoint" type field. In simulator.py it returns "lat lon 0 0"
            // Let's look for any field that looks like a geopoint
            if (!lat) {
                const geoField = Object.keys(r).find(k => k.toLowerCase().includes('geo') || k.toLowerCase().includes('gps'));
                if (geoField && typeof r[geoField] === 'string') {
                    const parts = r[geoField].split(' ');
                    if (parts.length >= 2) {
                        lat = parseFloat(parts[0]);
                        lon = parseFloat(parts[1]);
                    }
                }
            }

            return {
                coordinates: [lon, lat],
                fcs: parseFloat(r.FCSStap || 0),
                name: `HH-${i}`
            };
        })
        .filter(m => m.coordinates[0] !== null && !isNaN(m.coordinates[0]));

    // Limit markers for performance
    const displayMarkers = markers.slice(0, 500);

    const getColor = (fcs) => {
        if (fcs < 21) return "#ef4444"; // Poor
        if (fcs < 35) return "#eab308"; // Borderline
        return "#22c55e"; // Acceptable
    };

    return (
        <div className="w-full h-full bg-slate-800 rounded-xl overflow-hidden border border-slate-700 relative">
            <ComposableMap projection="geoMercator" projectionConfig={{ scale: 120 }}>
                <ZoomableGroup center={[0, 20]} zoom={1}>
                    <Geographies geography={GEO_URL}>
                        {({ geographies }) =>
                            geographies.map((geo) => (
                                <Geography
                                    key={geo.rsmKey}
                                    geography={geo}
                                    fill="#334155"
                                    stroke="#1e293b"
                                    strokeWidth={0.5}
                                />
                            ))
                        }
                    </Geographies>
                    {displayMarkers.map((marker, index) => (
                        <Marker key={index} coordinates={marker.coordinates}>
                            <circle r={2} fill={getColor(marker.fcs)} stroke="none" opacity={0.7} />
                        </Marker>
                    ))}
                </ZoomableGroup>
            </ComposableMap>

            {/* Legend Overlay */}
            <div className="absolute bottom-4 left-4 bg-slate-900/90 p-3 rounded-lg border border-slate-700 text-xs text-slate-300">
                <div className="font-bold mb-2 text-white">FCS Status</div>
                <div className="flex items-center gap-2 mb-1">
                    <div className="w-2 h-2 rounded-full bg-green-500"></div> Acceptable
                </div>
                <div className="flex items-center gap-2 mb-1">
                    <div className="w-2 h-2 rounded-full bg-yellow-500"></div> Borderline
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-red-500"></div> Poor
                </div>
            </div>
        </div>
    );
};

export default memo(DashboardMap);
