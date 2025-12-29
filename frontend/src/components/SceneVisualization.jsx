
import React, { useEffect, useState, useMemo } from 'react';
import axios from 'axios';
import { AgGridReact } from 'ag-grid-react';
import { AllCommunityModule, ModuleRegistry } from 'ag-grid-community';

// Register all Community features
ModuleRegistry.registerModules([AllCommunityModule]);

import DashboardMap from './DashboardMap';
import DashboardCharts from './DashboardCharts';
import DashboardInsights from './DashboardInsights';
import { Download } from 'lucide-react';

const SceneVisualization = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [colDefs, setColDefs] = useState([]);
    const [odkFieldOrder, setOdkFieldOrder] = useState([]);

    // Order verification panel state
    const [showOrderVerification, setShowOrderVerification] = useState(false);
    const [orderComparison, setOrderComparison] = useState({ odk: [], csv: [], matches: true });

    // Multi-Select Country Filter State
    const [selectedCountries, setSelectedCountries] = useState(["All Countries"]);

    useEffect(() => {
        fetchResults();
    }, []);

    const fetchResults = async () => {
        try {
            // Using correct port 9005
            const host = window.location.hostname;
            const [resultsRes, structureRes] = await Promise.all([
                axios.get(`http://${host}:9005/simulation-results`),
                axios.get(`http://${host}:9005/latest-structure`)
            ]);

            const rawData = resultsRes.data;
            const structure = structureRes.data;

            // Get ODK field order from structure (preserve original order)
            const odkFieldOrder = structure.survey
                .filter(q => !q.is_group_start && q.name)
                .map(q => q.name);

            // Store ODK field order for CSV export
            setOdkFieldOrder(odkFieldOrder);

            // Keep ALL original data without filtering (preserve order from backend)
            setData(rawData);

            if (rawData.length > 0) {
                // Use ODK order for columns, then add any extra fields
                const existingKeys = new Set(Object.keys(rawData[0]));
                const orderedKeys = [];

                // First: ODK fields in order
                odkFieldOrder.forEach(f => {
                    if (existingKeys.has(f)) {
                        orderedKeys.push(f);
                        existingKeys.delete(f);
                    }
                });

                // Then: any remaining fields (internal ones like latitude, longitude, etc.)
                existingKeys.forEach(k => orderedKeys.push(k));

                const priority = ["SvyDate", "Country", "ADMIN1Name", "FCSStap", "HHSFr"];

                const newCols = orderedKeys.map(k => ({
                    field: k,
                    filter: true,
                    headerName: k,
                    pinned: priority.includes(k) ? 'left' : null
                }));
                setColDefs(newCols);
            }
        } catch (error) {
            console.error("Error fetching results:", error);
        } finally {
            setLoading(false);
        }
    };



    // Filter Logic
    const uniqueCountries = React.useMemo(() => {
        return Array.from(new Set(data.map(r => r.Country || "Unknown"))).sort();
    }, [data]);

    // Initialize with all countries selected by default
    useEffect(() => {
        if (uniqueCountries.length > 0 && selectedCountries.length === 0) {
            // Default to showing all data initially (empty selection treated as All in UI logic if preferred, 
            // but here we use explict list for clarity in multi-select)
            // Actually, let's keep "All Countries" concept for the filter logic but UI uses checkboxes
            setSelectedCountries(["All Countries"]); // Initialize with "All Countries" selected
        }
    }, [uniqueCountries, selectedCountries]);

    // Handle Multi-Select Change
    const toggleCountry = (country) => {
        if (country === "All Countries") {
            if (selectedCountries.includes("All Countries")) {
                setSelectedCountries([]); // Deselect all
            } else {
                setSelectedCountries(["All Countries"]); // Select All
            }
            return;
        }

        let newSelection = [...selectedCountries];
        if (newSelection.includes("All Countries")) {
            newSelection = []; // Clear "All" if picking specific
        }

        if (newSelection.includes(country)) {
            newSelection = newSelection.filter(c => c !== country);
        } else {
            newSelection.push(country);
        }

        // If no countries selected, or if users manually selected all, revert to "All Countries" mode? 
        // Or keep empty = none. Let's keep empty = none for clarity.
        setSelectedCountries(newSelection);
    };

    const isAllSelected = selectedCountries.includes("All Countries") || selectedCountries.length === 0;

    const filteredData = React.useMemo(() => {
        if (isAllSelected) return data;
        return data.filter(r => selectedCountries.includes(r.Country || "Unknown"));
    }, [data, selectedCountries, isAllSelected]);

    // Shuffle data for map to avoid "First N" bias when clipping
    const mapData = React.useMemo(() => {
        // Create a copy to shuffle
        const shuffled = [...filteredData];
        // Fisher-Yates shuffle
        for (let i = shuffled.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }
        return shuffled;
    }, [filteredData]);


    // Calculate Summary KPIs (based on filtered data)
    const totalHH = filteredData.length;
    const avgFCS = filteredData.length > 0 ? (filteredData.reduce((acc, r) => acc + (parseFloat(r.FCSStap) || 0), 0) / filteredData.length).toFixed(1) : 0;

    // Verify order and show comparison panel before exporting
    const verifyAndExport = () => {
        if (!filteredData.length) return;

        // Get all unique keys from data
        const allKeys = new Set(Object.keys(filteredData[0]));

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

        // Then: any remaining fields
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

    // Export Function - Uses ODK field order
    const exportToCSV = (dataToExport) => {
        if (!dataToExport.length) return;

        // Build ordered headers: ODK fields first (in order), then any extra fields
        const existingKeys = new Set(Object.keys(dataToExport[0]));
        const orderedHeaders = [];

        // Add ODK fields in correct order
        odkFieldOrder.forEach(field => {
            if (existingKeys.has(field)) {
                orderedHeaders.push(field);
                existingKeys.delete(field);
            }
        });

        // Add any remaining fields (internal ones like latitude, longitude, _events_summary)
        existingKeys.forEach(field => orderedHeaders.push(field));

        const csvRows = [];

        // Add headers
        csvRows.push(orderedHeaders.join(','));

        // Add data rows in the same order
        for (const row of dataToExport) {
            const values = orderedHeaders.map(header => {
                const value = row[header];
                // Handle null/undefined
                if (value === null || value === undefined) return '';
                // Handle commas and quotes in values
                if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
                    return `"${value.replace(/"/g, '""')}"`;
                }
                return value;
            });
            csvRows.push(values.join(','));
        }

        const blob = new Blob([csvRows.join('\n')], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.setAttribute('hidden', '');
        a.setAttribute('href', url);
        a.setAttribute('download', `simulation_results_${isAllSelected ? 'all_countries' : selectedCountries.join('_')}.csv`);
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

        // Close verification panel after export
        setShowOrderVerification(false);
    };

    if (loading) return <div className="text-slate-600 p-10 animate-pulse">Loading visualization dashboard...</div>;

    return (
        <div className="p-6 bg-slate-50 min-h-screen font-sans text-slate-900">
            {/* Header */}
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-extrabold text-slate-800 tracking-tight">Mission Analytics Dashboard</h1>
                    <p className="text-slate-500 mt-1">Visualizing humanitarian impact across 5 years</p>
                </div>

                <div className="flex gap-4 items-center">
                    {/* Multi-Select Dropdown */}
                    <div className="relative group z-50">
                        <button className="bg-white border border-slate-300 px-4 py-2 rounded-lg shadow-sm text-sm font-medium text-slate-700 flex items-center gap-2 hover:bg-slate-50">
                            {isAllSelected ? "All Countries" : `${selectedCountries.length} Selected`}
                            <span className="text-xs text-slate-400">▼</span>
                        </button>

                        {/* Dropdown Menu */}
                        <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-xl border border-slate-100 hidden group-hover:block p-2 max-h-80 overflow-y-auto">
                            <label className="flex items-center gap-2 p-2 hover:bg-slate-50 rounded cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={isAllSelected}
                                    onChange={() => toggleCountry("All Countries")}
                                    className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                                />
                                <span className="text-sm font-medium text-slate-700">All Countries</span>
                            </label>
                            <div className="h-px bg-slate-100 my-1"></div>
                            {uniqueCountries.map(c => (
                                <label key={c} className="flex items-center gap-2 p-2 hover:bg-slate-50 rounded cursor-pointer">
                                    <input
                                        type="checkbox"
                                        checked={selectedCountries.includes(c)}
                                        onChange={() => toggleCountry(c)}
                                        className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                                    />
                                    <span className="text-sm text-slate-600">{c}</span>
                                </label>
                            ))}
                        </div>
                    </div>

                    {/* Export Buttons */}
                    <button
                        onClick={verifyAndExport}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-semibold shadow-md transition-all flex items-center gap-2"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        Verificar Orden
                    </button>
                    <button
                        onClick={() => exportToCSV(filteredData)}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm font-semibold shadow-md transition-all flex items-center gap-2"
                    >
                        <Download size={16} />
                        Export
                    </button>

                    <div className="bg-white p-3 rounded-xl shadow-sm border border-slate-200">
                        <div className="text-xs font-bold text-slate-400 uppercase">Total Households</div>
                        <div className="text-2xl font-black text-slate-800">{totalHH}</div>
                    </div>
                    <div className="bg-white p-3 rounded-xl shadow-sm border border-slate-200">
                        <div className="text-xs font-bold text-slate-400 uppercase">Avg FCS Score</div>
                        <div className="text-2xl font-black text-yellow-500">{avgFCS}</div>
                    </div>
                </div>
            </div>

            {/* Dashboard Grid */}
            <div className="space-y-6">

                {/* 1. Map & Insights Row */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Analysis Card */}
                    <DashboardInsights data={filteredData} selectedCountries={isAllSelected ? uniqueCountries : selectedCountries} />

                    {/* Map Card */}
                    <div className="bg-slate-800 p-6 rounded-xl shadow-lg border border-slate-700">
                        <h3 className="text-lg font-semibold text-white mb-4">Geographic Distribution</h3>
                        <div className="h-80 w-full rounded-lg overflow-hidden bg-slate-900/50">
                            {/* Pass shuffled mapData to Map to avoid clipping bias */}
                            <DashboardMap data={mapData} />
                        </div>
                        {/* Legend */}
                        <div className="mt-4 flex gap-4 text-xs text-slate-400 bg-slate-900/50 p-3 rounded-lg w-fit">
                            <div className="font-semibold text-slate-300 mb-1 block w-full">FCS Status</div>
                            <div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-green-500"></span> Acceptable</div>
                            <div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-yellow-500"></span> Borderline</div>
                            <div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-red-500"></span> Poor</div>
                        </div>
                    </div>
                </div>

                {/* 2. Charts Section */}
                <DashboardCharts activeData={filteredData} selectedCountry={isAllSelected || selectedCountries.length > 1 ? "Comparison" : selectedCountries[0]} />

                {/* 3. Data Table */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
                    <h3 className="text-lg font-bold text-slate-800 mb-4">Raw Data Explorer</h3>
                    <div className="ag-theme-alpine w-full h-96" style={{ '--ag-font-size': '13px', '--ag-header-background-color': '#f8fafc' }}>
                        <AgGridReact
                            rowData={filteredData}
                            columnDefs={colDefs}
                            pagination={true}
                            paginationPageSize={10}
                            rowSelection="multiple"
                        />
                    </div>
                </div>
            </div>

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
                                onClick={() => exportToCSV(filteredData)}
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

export default SceneVisualization;
