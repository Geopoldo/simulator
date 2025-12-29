import React, { memo, useState } from "react";
import { ComposableMap, Geographies, Geography, ZoomableGroup } from "react-simple-maps";

// URL to a valid topojson world map
const GEO_URL = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json";

const CountryMapSelector = ({ selectedCountries = [], availableCountries = [], onToggleCountry }) => {
    const [tooltip, setTooltip] = useState({ show: false, name: "", x: 0, y: 0 });

    const handleMouseEnter = (geo, event) => {
        const countryName = geo.properties.name;
        setTooltip({
            show: true,
            name: countryName,
            x: event.clientX,
            y: event.clientY
        });
    };

    const handleMouseLeave = () => {
        setTooltip({ show: false, name: "", x: 0, y: 0 });
    };

    const handleMouseMove = (event) => {
        if (tooltip.show) {
            setTooltip(prev => ({
                ...prev,
                x: event.clientX,
                y: event.clientY
            }));
        }
    };

    return (
        <div className="w-full h-[400px] bg-slate-50 border border-slate-200 rounded-lg overflow-hidden relative">
            <ComposableMap projection="geoMercator" projectionConfig={{ scale: 100 }}>
                <ZoomableGroup center={[0, 20]} zoom={1}>
                    <Geographies geography={GEO_URL}>
                        {({ geographies }) =>
                            geographies.map((geo) => {
                                const countryName = geo.properties.name;
                                const isSelected = selectedCountries.includes(countryName);
                                const hasContextData = availableCountries.includes(countryName);

                                // Color logic: Selected > Has Data > No Data
                                let fillColor = "#E5E7EB"; // Gray (no data)
                                let hoverColor = "#D1D5DB";

                                if (hasContextData) {
                                    fillColor = "#10B981"; // Green (has context data)
                                    hoverColor = "#059669";
                                }

                                if (isSelected) {
                                    fillColor = "#3B82F6"; // Blue (selected)
                                    hoverColor = "#2563EB";
                                }

                                return (
                                    <Geography
                                        key={geo.rsmKey}
                                        geography={geo}
                                        onClick={() => hasContextData && onToggleCountry(countryName)}
                                        onMouseEnter={(event) => handleMouseEnter(geo, event)}
                                        onMouseLeave={handleMouseLeave}
                                        onMouseMove={handleMouseMove}
                                        style={{
                                            default: {
                                                fill: fillColor,
                                                outline: "none",
                                                stroke: "#ffffff",
                                                strokeWidth: 0.5,
                                                cursor: hasContextData ? "pointer" : "not-allowed",
                                                transition: "fill 0.2s ease",
                                            },
                                            hover: {
                                                fill: hoverColor,
                                                outline: "none",
                                                cursor: hasContextData ? "pointer" : "not-allowed",
                                            },
                                            pressed: {
                                                fill: "#1E40AF",
                                                outline: "none",
                                            },
                                        }}
                                    />
                                );
                            })
                        }
                    </Geographies>
                </ZoomableGroup>
            </ComposableMap>

            {/* Tooltip */}
            {tooltip.show && (
                <div
                    className="fixed bg-slate-900 text-white px-3 py-2 rounded-lg shadow-lg text-sm font-medium pointer-events-none z-50"
                    style={{
                        left: `${tooltip.x + 10}px`,
                        top: `${tooltip.y + 10}px`,
                    }}
                >
                    {tooltip.name}
                </div>
            )}

            {/* Legend / Info Overlay */}
            <div className="absolute bottom-2 left-2 bg-white/95 p-3 text-xs rounded-lg shadow-lg backdrop-blur-sm border border-slate-200">
                <p className="font-semibold text-slate-700 mb-2">Map Legend</p>
                <div className="space-y-1">
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded bg-blue-500"></div>
                        <span>Selected ({selectedCountries.length})</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded bg-green-500"></div>
                        <span>Has Context Data ({availableCountries.length})</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded bg-gray-300"></div>
                        <span>No Data</span>
                    </div>
                </div>
                <p className="text-slate-500 italic mt-2">Click countries with data to select</p>
            </div>
        </div>
    );
};

export default memo(CountryMapSelector);
