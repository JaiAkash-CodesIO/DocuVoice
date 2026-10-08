import { useState } from "react";

export default function DocumentViewer({ documentId, file, apiBaseUrl }) {
  const [viewMode, setViewMode] = useState("preview"); // 'preview' or 'source'
  const [zoom, setZoom] = useState(1);

  const fileUrl = `${apiBaseUrl}/documents/${documentId}/file`;
  const previewUrl = `${apiBaseUrl}/documents/${documentId}/preview`;
  const isPdf = file?.name?.toLowerCase().endsWith(".pdf") || file?.type?.includes("pdf");

  const handleZoomIn = () => setZoom((prev) => Math.min(prev + 0.25, 2.5));
  const handleZoomOut = () => setZoom((prev) => Math.max(prev - 0.25, 0.5));
  const handleResetZoom = () => setZoom(1);

  return (
    <div className="doc-viewer-card">
      <div className="doc-viewer-header">
        <div className="viewer-title-group">
          <span className="viewer-badge">VISUAL SCAN</span>
          <span className="viewer-filename">{file?.name || "Document"}</span>
        </div>

        <div className="viewer-toolbar">
          <div className="viewer-mode-toggle">
            <button
              className={`toggle-btn ${viewMode === "preview" ? "active" : ""}`}
              onClick={() => setViewMode("preview")}
              title="Show high-contrast OpenCV preprocessed image used for OCR"
            >
              OCR Scan
            </button>
            <button
              className={`toggle-btn ${viewMode === "source" ? "active" : ""}`}
              onClick={() => setViewMode("source")}
              title="Show original uploaded document"
            >
              Original
            </button>
          </div>

          <div className="zoom-controls">
            <button className="icon-btn" onClick={handleZoomOut} title="Zoom Out">-</button>
            <span className="zoom-text">{Math.round(zoom * 100)}%</span>
            <button className="icon-btn" onClick={handleZoomIn} title="Zoom In">+</button>
            <button className="icon-btn" onClick={handleResetZoom} title="Reset">1:1</button>
          </div>
        </div>
      </div>

      <div className="doc-viewer-viewport">
        {viewMode === "source" && isPdf ? (
          <iframe
            src={`${fileUrl}#toolbar=0`}
            title="PDF Document"
            className="doc-iframe"
          />
        ) : (
          <div className="image-scroll-pane">
            <img
              src={viewMode === "preview" ? previewUrl : fileUrl}
              alt="Document preview"
              style={{ transform: `scale(${zoom})`, transformOrigin: "top center" }}
              className="doc-image"
              onError={(e) => {
                // Fallback to fileUrl if preview fails (e.g. single page)
                if (viewMode === "preview") {
                  e.target.src = fileUrl;
                }
              }}
            />
          </div>
        )}
      </div>

      <div className="doc-viewer-footer">
        <span>Mode: {viewMode === "preview" ? "OpenCV Binarized Grayscale" : "Raw Source Ingestion"}</span>
        <span>ID: {documentId.substring(0, 8)}...</span>
      </div>
    </div>
  );
}
