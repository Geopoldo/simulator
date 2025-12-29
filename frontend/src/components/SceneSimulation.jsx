import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { AgGridReact } from 'ag-grid-react';
import { AllCommunityModule, ModuleRegistry } from 'ag-grid-community';

// Register all Community features
ModuleRegistry.registerModules([AllCommunityModule]);

import CountryMapSelector from './CountryMapSelector';

const SceneSimulation = ({
    structure,
    selectedCountries,
    setSelectedCountries,
    simulationData,
    setSimulationData,
    simParams,
    setSimParams
}) => {
    const [availableCountries, setAvailableCountries] = useState([]);
    // Local loading/error state is fine
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // ODK Field Order for correct CSV export
    const [odkFieldOrder, setOdkFieldOrder] = useState([]);
    // Order verification panel state
    const [showOrderVerification, setShowOrderVerification] = useState(false);
    const [orderComparison, setOrderComparison] = useState({ odk: [], csv: [], matches: true });

    // Fetch available countries and ODK field order on mount
    useEffect(() => {
        const fetchInitialData = async () => {
            try {
                const host = window.location.hostname;
                const [countriesRes, orderRes] = await Promise.all([
                    axios.get(`http://${host}:9005/countries`),
                    axios.get(`http://${host}:9005/field-order`).catch(() => ({ data: { field_order: [] } }))
                ]);
                setAvailableCountries(countriesRes.data);
                setOdkFieldOrder(orderRes.data.field_order || []);
            } catch (err) {
                console.error("Failed to fetch initial data:", err);
            }
        };
        fetchInitialData();
    }, []);

    const toggleCountry = (country) => {
        setSelectedCountries(prev =>
            prev.includes(country) ? prev.filter(c => c !== country) : [...prev, country]
        );
    };

    const runSimulation = async () => {
        if (selectedCountries.length === 0) {
            alert("Please select at least one country on the map!");
            return;
        }

        setLoading(true);
        setError(null);
        try {
            const payload = {
                odk_structure: structure,
                countries: selectedCountries,
                start_year: parseInt(simParams.startYear),
                end_year: parseInt(simParams.endYear),
                count_per_country_year: parseInt(simParams.countPerYear)
            };

            console.log("Sending Simulation Payload:", payload);
            const host = window.location.hostname;
            const response = await axios.post(`http://${host}:9005/simulate`, payload);

            setSimulationData(response.data);
        } catch (err) {
            console.error("Simulation failed", err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    // Verify order and show comparison panel before exporting
    const verifyAndExport = () => {
        if (simulationData.length === 0) return;

        // Get all unique keys from simulation data
        const allKeys = new Set();
        simulationData.forEach(row => {
            Object.keys(row).forEach(key => allKeys.add(key));
        });

        // Build ordered headers: ODK fields first (in order), then any extra fields
        const orderedHeaders = [];
        const usedKeys = new Set();

        // First: ODK fields in order
        odkFieldOrder.forEach(field => {
            if (allKeys.has(field)) {
                orderedHeaders.push(field);
                usedKeys.add(field);
            }
        });

        // Then: any remaining fields (internal ones like latitude, longitude, _events_summary)
        allKeys.forEach(key => {
            if (!usedKeys.has(key)) {
                orderedHeaders.push(key);
            }
        });

        // Compare: first N fields should match ODK order
        const odkFieldsInData = odkFieldOrder.filter(f => allKeys.has(f));
        const csvFieldsOrdered = orderedHeaders.slice(0, odkFieldsInData.length);

        const matches = odkFieldsInData.every((field, idx) => csvFieldsOrdered[idx] === field);

        setOrderComparison({
            odk: odkFieldsInData,
            csv: csvFieldsOrdered,
            matches: matches
        });
        setShowOrderVerification(true);
    };

    // CSV Export - Client-side conversion (uses ODK order)
    const exportToCSV = () => {
        if (simulationData.length === 0) return;

        // Get all unique keys from simulation data
        const allKeys = new Set();
        simulationData.forEach(row => {
            Object.keys(row).forEach(key => allKeys.add(key));
        });

        // Build ordered headers: ODK fields first (in order), then any extra fields
        const orderedHeaders = [];
        const usedKeys = new Set();

        // First: ODK fields in order
        odkFieldOrder.forEach(field => {
            if (allKeys.has(field)) {
                orderedHeaders.push(field);
                usedKeys.add(field);
            }
        });

        // Then: any remaining fields (internal ones like latitude, longitude, _events_summary)
        allKeys.forEach(key => {
            if (!usedKeys.has(key)) {
                orderedHeaders.push(key);
            }
        });

        // Create CSV content with correct order
        let csvContent = orderedHeaders.join(',') + '\n';

        simulationData.forEach(row => {
            const values = orderedHeaders.map(header => {
                const value = row[header];
                // Handle values that might contain commas or quotes
                if (value === null || value === undefined) return '';
                const stringValue = String(value);
                if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
                    return `"${stringValue.replace(/"/g, '""')}"`;
                }
                return stringValue;
            });
            csvContent += values.join(',') + '\n';
        });

        // Create download
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `simulation_results_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        // Close verification panel after export
        setShowOrderVerification(false);
    };

    // Auto-column definition
    const columnDefs = simulationData.length > 0
        ? Object.keys(simulationData[0]).map(key => ({ field: key, filter: true, sortable: true }))
        : [];

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-8">
            <header>
                <h2 className="text-3xl font-bold text-slate-800">Scene 2: Contextual Simulation</h2>
                <p className="text-slate-600">Select countries and timeframe to generate synthetic data.</p>
            </header>

            {/* Controls Area */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                {/* Left: Map */}
                <div className="lg:col-span-2 space-y-2">
                    <h3 className="font-semibold text-slate-700">1. Geographic Selection</h3>
                    <CountryMapSelector
                        selectedCountries={selectedCountries}
                        availableCountries={availableCountries}
                        onToggleCountry={toggleCountry}
                    />
                    <div className="text-sm text-slate-500">
                        Selected: {selectedCountries.join(", ") || "(None)"}
                    </div>
                </div>

                {/* Right: Params & Action */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 space-y-6 h-fit">
                    <h3 className="font-semibold text-slate-700">2. Time & Volume</h3>

                    <div className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-xs font-medium text-slate-500 uppercase">Start Year</label>
                                <input
                                    type="number"
                                    className="w-full mt-1 p-2 border border-slate-300 rounded focus:ring-2 focus:ring-blue-500 outline-none"
                                    value={simParams.startYear}
                                    onChange={(e) => setSimParams({ ...simParams, startYear: e.target.value })}
                                />
                            </div>
                            <div>
                                <label className="block text-xs font-medium text-slate-500 uppercase">End Year</label>
                                <input
                                    type="number"
                                    className="w-full mt-1 p-2 border border-slate-300 rounded focus:ring-2 focus:ring-blue-500 outline-none"
                                    value={simParams.endYear}
                                    onChange={(e) => setSimParams({ ...simParams, endYear: e.target.value })}
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-xs font-medium text-slate-500 uppercase">Records per Country/Year</label>
                            <input
                                type="number"
                                className="w-full mt-1 p-2 border border-slate-300 rounded focus:ring-2 focus:ring-blue-500 outline-none"
                                value={simParams.countPerYear}
                                onChange={(e) => setSimParams({ ...simParams, countPerYear: e.target.value })}
                            />
                            <p className="text-xs text-slate-400 mt-1">
                                Total: {selectedCountries.length} countries × {(simParams.endYear - simParams.startYear + 1)} years × {simParams.countPerYear} = {selectedCountries.length * (simParams.endYear - simParams.startYear + 1) * simParams.countPerYear} rows
                            </p>
                        </div>
                    </div>

                    <div className="pt-4 border-t border-slate-100">
                        <button
                            onClick={runSimulation}
                            disabled={loading || selectedCountries.length === 0}
                            className={`w-full py-4 text-center rounded-lg font-bold text-white shadow transition-all
                        ${loading || selectedCountries.length === 0 ? 'bg-slate-300 cursor-not-allowed' : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:shadow-lg hover:scale-[1.02]'}
                    `}
                        >
                            {loading ? "Simulating..." : "Generate Synthetic Data"}
                        </button>
                    </div>

                    {error && (
                        <div className="p-3 bg-red-50 text-red-600 text-sm rounded border border-red-100">
                            Error: {error}
                        </div>
                    )}
                </div>
            </div>

            {/* Results Table */}
            {simulationData.length > 0 && (
                <div className="space-y-4">
                    <div className="flex justify-between items-center">
                        <h3 className="font-semibold text-slate-700">Simulation Output ({simulationData.length} rows)</h3>
                        <div className="flex gap-2">
                            <button
                                onClick={verifyAndExport}
                                className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg shadow transition-all hover:shadow-lg flex items-center gap-2"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                </svg>
                                Verificar Orden y Exportar
                            </button>
                            <button
                                onClick={exportToCSV}
                                className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg shadow transition-all hover:shadow-lg flex items-center gap-2"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                    <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                                </svg>
                                Exportar CSV Directo
                            </button>
                        </div>
                    </div>
                    <div className="ag-theme-quartz h-[600px] w-full shadow-lg rounded-xl overflow-hidden border border-slate-200">
                        <AgGridReact
                            rowData={simulationData}
                            columnDefs={columnDefs}
                            pagination={true}
                            paginationPageSize={20}
                        />
                    </div>
                </div>
            )}

            {/* Order Verification Modal */}
            {showOrderVerification && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[80vh] overflow-hidden">
                        {/* Header */}
                        <div className={`px-6 py-4 flex items-center justify-between ${orderComparison.matches ? 'bg-green-50' : 'bg-amber-50'}`}>
                            <div className="flex items-center gap-3">
                                {orderComparison.matches ? (
                                    <div className="w-10 h-10 rounded-full bg-green-500 flex items-center justify-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" viewBox="0 0 20 20" fill="currentColor">
                                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                        </svg>
                                    </div>
                                ) : (
                                    <div className="w-10 h-10 rounded-full bg-amber-500 flex items-center justify-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" viewBox="0 0 20 20" fill="currentColor">
                                            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                                        </svg>
                                    </div>
                                )}
                                <div>
                                    <h3 className="text-lg font-bold text-slate-800">
                                        {orderComparison.matches
                                            ? '✅ Orden de Columnas Verificado'
                                            : '⚠️ Verificación de Orden de Columnas'}
                                    </h3>
                                    <p className="text-sm text-slate-600">
                                        {orderComparison.matches
                                            ? 'Las columnas del CSV están en el orden correcto del ODK'
                                            : 'Revisa el orden de las columnas antes de exportar'}
                                    </p>
                                </div>
                            </div>
                            <button
                                onClick={() => setShowOrderVerification(false)}
                                className="text-slate-400 hover:text-slate-600"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" viewBox="0 0 20 20" fill="currentColor">
                                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                                </svg>
                            </button>
                        </div>

                        {/* Content - Side by Side Comparison */}
                        <div className="p-6 overflow-auto max-h-[50vh]">
                            <div className="grid grid-cols-2 gap-4">
                                {/* ODK Order Column */}
                                <div>
                                    <h4 className="font-bold text-slate-700 mb-3 flex items-center gap-2">
                                        <span className="w-3 h-3 rounded-full bg-blue-500"></span>
                                        Orden ODK Original ({orderComparison.odk.length} campos)
                                    </h4>
                                    <div className="border border-slate-200 rounded-lg overflow-hidden">
                                        <div className="max-h-64 overflow-y-auto">
                                            {orderComparison.odk.map((field, idx) => (
                                                <div
                                                    key={idx}
                                                    className={`px-3 py-2 text-sm font-mono border-b border-slate-100 flex items-center gap-2
                                                        ${orderComparison.csv[idx] === field ? 'bg-green-50' : 'bg-red-50'}`}
                                                >
                                                    <span className="text-slate-400 w-8">{idx + 1}.</span>
                                                    <span className={orderComparison.csv[idx] === field ? 'text-green-700' : 'text-red-700'}>
                                                        {field}
                                                    </span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </div>

                                {/* CSV Order Column */}
                                <div>
                                    <h4 className="font-bold text-slate-700 mb-3 flex items-center gap-2">
                                        <span className="w-3 h-3 rounded-full bg-green-500"></span>
                                        Orden en CSV a Exportar ({orderComparison.csv.length} campos)
                                    </h4>
                                    <div className="border border-slate-200 rounded-lg overflow-hidden">
                                        <div className="max-h-64 overflow-y-auto">
                                            {orderComparison.csv.map((field, idx) => (
                                                <div
                                                    key={idx}
                                                    className={`px-3 py-2 text-sm font-mono border-b border-slate-100 flex items-center gap-2
                                                        ${orderComparison.odk[idx] === field ? 'bg-green-50' : 'bg-red-50'}`}
                                                >
                                                    <span className="text-slate-400 w-8">{idx + 1}.</span>
                                                    <span className={orderComparison.odk[idx] === field ? 'text-green-700' : 'text-red-700'}>
                                                        {field}
                                                    </span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Footer */}
                        <div className="px-6 py-4 bg-slate-50 border-t border-slate-200 flex justify-end gap-3">
                            <button
                                onClick={() => setShowOrderVerification(false)}
                                className="px-4 py-2 text-slate-600 hover:text-slate-800 font-medium"
                            >
                                Cancelar
                            </button>
                            <button
                                onClick={exportToCSV}
                                className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg shadow transition-all flex items-center gap-2"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                    <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                                </svg>
                                Confirmar y Exportar CSV
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default SceneSimulation;
