
import React, { useState, useCallback } from 'react';
import axios from 'axios';
import { useDropzone } from 'react-dropzone'; // Assuming useDropzone if installed or simple implementation

// Fallback simple DnD implementation since we didn't install react-dropzone explicitly, 
// using generic HTML events or we should have installed it. 
// Let's implement a simple drop zone without extra libs to be safe, or use what I installed (axios).
// Wait, I didn't install react-dropzone. I'll code a custom one.

export default function SceneUpload({ onUploadComplete, onAdvance, structure }) {
    const [isDragging, setIsDragging] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState(null);

    const handleDragOver = (e) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = async (e) => {
        e.preventDefault();
        setIsDragging(false);
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            uploadFile(files[0]);
        }
    };

    const uploadFile = async (file) => {
        setUploading(true);
        setError(null);
        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await axios.post('http://localhost:9005/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            onUploadComplete(res.data);
        } catch (err) {
            console.error(err);
            setError("Failed to process file. Ensure backend is running.");
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="space-y-6 animate-fade-in-up">
            <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100 text-center">
                <h2 className="text-2xl font-semibold text-gray-800 mb-2">Upload ODK Survey</h2>
                <p className="text-gray-500 mb-6">Drag and drop your .xlsx ODK Form here to analyze its rules.</p>

                <div
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    className={`
                        border-2 border-dashed rounded-xl p-10 transition-all cursor-pointer
                        ${isDragging ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 hover:border-indigo-300 hover:bg-gray-50'}
                    `}
                >
                    {uploading ? (
                        <div className="text-indigo-600 font-medium">Analyzing Survey Logic...</div>
                    ) : (
                        <div className="text-gray-400">
                            <span className="text-4xl block mb-2">📄</span>
                            Drop file here or click to select
                            <input
                                type="file"
                                className="hidden"
                                onChange={(e) => e.target.files[0] && uploadFile(e.target.files[0])}
                                id="fileInput"
                            />
                        </div>
                    )}
                </div>
                {error && <p className="text-red-500 mt-4">{error}</p>}
            </div>

            {structure && (
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                    <div className="p-6 border-b border-gray-100 flex justify-between items-center bg-gray-50">
                        <div>
                            <h3 className="text-lg font-bold text-gray-800">Survey Documentation</h3>
                            <p className="text-sm text-gray-500">Structured analysis of {structure.survey.length} fields</p>
                        </div>
                        <button
                            onClick={onAdvance}
                            className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-lg font-medium transition-colors shadow-sm"
                        >
                            Continue to Simulation →
                        </button>
                    </div>
                    <div className="divide-y divide-gray-100 max-h-[600px] overflow-y-auto p-4 bg-gray-50 space-y-4">
                        {structure.survey.map((q, idx) => {
                            // Section Header Style
                            if (q.is_group_start) {
                                return (
                                    <div key={idx} className="bg-indigo-50 p-4 rounded-lg border border-indigo-100 mt-6 shadow-sm">
                                        <div className="text-xs font-bold text-indigo-400 uppercase tracking-widest mb-1 flex items-center gap-1">
                                            <span>📂</span> SECTION
                                        </div>
                                        <h3 className="text-xl font-bold text-indigo-900">
                                            {q['label::English (en)'] || q['label'] || q.name}
                                        </h3>
                                        <p className="text-xs text-indigo-500 font-mono">{q.name}</p>
                                    </div>
                                );
                            }

                            // Regular Question Card
                            return (
                                <div key={idx} className="bg-white p-5 rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow relative ml-4 border-l-4 border-l-indigo-100">
                                    <span className="absolute top-4 right-4 text-xs font-mono px-2 py-1 bg-gray-100 text-gray-500 rounded border border-gray-200">
                                        {q.type}
                                    </span>

                                    {/* Hierarchy Breadcrumbs */}
                                    {q.hierarchy && q.hierarchy.length > 0 && (
                                        <div className="flex items-center gap-1 text-xs text-gray-400 mb-2">
                                            {q.hierarchy.map((g, i) => (
                                                <React.Fragment key={i}>
                                                    <span className="font-medium text-gray-500">{g}</span>
                                                    <span>/</span>
                                                </React.Fragment>
                                            ))}
                                        </div>
                                    )}

                                    <h4 className="font-bold text-gray-900 text-lg mb-1">
                                        {q['label::English (en)'] || q['label'] || q.name}
                                    </h4>
                                    <p className="text-xs text-indigo-500 font-mono mb-4">{q.name}</p>

                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        {/* Business Rules Section */}
                                        <div className="space-y-2">
                                            <h5 className="text-xs font-bold uppercase tracking-wider text-gray-400">Rules & Logic</h5>
                                            {q.relevant && (
                                                <div className="flex flex-col">
                                                    <span className="text-xs font-semibold text-amber-600">Only shows if:</span>
                                                    <code className="text-xs bg-amber-50 text-amber-800 p-1.5 rounded mt-1 border border-amber-100">
                                                        {q.relevant}
                                                    </code>
                                                </div>
                                            )}
                                            {q.constraint && (
                                                <div className="flex flex-col">
                                                    <span className="text-xs font-semibold text-red-600">Validation:</span>
                                                    <code className="text-xs bg-red-50 text-red-800 p-1.5 rounded mt-1 border border-red-100">
                                                        {q.constraint}
                                                    </code>
                                                    {q['constraint_message::English (en)'] && (
                                                        <span className="text-xs text-red-500 italic mt-0.5">"{q['constraint_message::English (en)']}"</span>
                                                    )}
                                                </div>
                                            )}
                                            {q.calculation && (
                                                <div className="flex flex-col">
                                                    <span className="text-xs font-semibold text-green-600">Calculated as:</span>
                                                    <code className="text-xs bg-green-50 text-green-800 p-1.5 rounded mt-1 border border-green-100">
                                                        {q.calculation}
                                                    </code>
                                                </div>
                                            )}
                                            {!q.relevant && !q.constraint && !q.calculation && (
                                                <span className="text-sm text-gray-400 italic">No complex rules defined.</span>
                                            )}
                                        </div>

                                        {/* Options Section */}
                                        {q.options && q.options.length > 0 && (
                                            <div className="space-y-2">
                                                <h5 className="text-xs font-bold uppercase tracking-wider text-gray-400">Available Options</h5>
                                                <div className="flex flex-wrap gap-2">
                                                    {q.options.slice(0, 10).map((opt, i) => (
                                                        <span key={i} className="px-2.5 py-1 text-xs rounded-full bg-blue-50 text-blue-700 border border-blue-100">
                                                            {opt['label::English (en)'] || opt['label'] || opt.name}
                                                        </span>
                                                    ))}
                                                    {q.options.length > 10 && (
                                                        <span className="px-2 py-1 text-xs text-gray-500">
                                                            +{q.options.length - 10} more...
                                                        </span>
                                                    )}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}
        </div>
    );
}
