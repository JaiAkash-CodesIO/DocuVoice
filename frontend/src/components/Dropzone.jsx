import { useState, useRef } from "react";

export default function Dropzone({
  file,
  onFileSelect,
  onClearFile,
  onProcess,
  isProcessing,
  error,
}) {
  const [dragging, setDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragging(true);
  };

  const handleDragLeave = () => {
    setDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onFileSelect(e.dataTransfer.files[0]);
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
  };

  return (
    <div className="dropzone-container">
      <div
        className={`upload-box ${dragging ? "dragging" : ""} ${file ? "has-file" : ""}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !file && fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.png,.jpg,.jpeg"
          style={{ display: "none" }}
          onChange={(e) => {
            if (e.target.files && e.target.files[0]) {
              onFileSelect(e.target.files[0]);
            }
          }}
        />

        {!file ? (
          <>
            <div className="upload-icon-wrapper">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
            </div>
            <h2>Drag & drop document here</h2>
            <p className="upload-hint">Supports high-res scans, multi-page PDFs, invoices, and photos</p>
            <div className="upload-btn-container">
              <button
                type="button"
                className="choose-button"
                onClick={(e) => {
                  e.stopPropagation();
                  fileInputRef.current?.click();
                }}
              >
                Browse Files
              </button>
            </div>
            <span className="file-types">
              PDF, PNG, JPG or JPEG &middot; Max 10 MB
            </span>
          </>
        ) : (
          <div className="file-selected-card" onClick={(e) => e.stopPropagation()}>
            <div className="file-icon-badge">
              {file.type.includes("pdf") ? "PDF" : "IMG"}
            </div>
            <div className="file-info-col">
              <span className="file-name-text">{file.name}</span>
              <span className="file-size-text">{formatFileSize(file.size)}</span>
            </div>
            {!isProcessing && (
              <button
                type="button"
                className="remove-file-btn"
                title="Remove file"
                onClick={onClearFile}
              >
                &times;
              </button>
            )}
          </div>
        )}
      </div>

      {error && (
        <div className="message error">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <span>{error}</span>
        </div>
      )}

      {file && !isProcessing && (
        <button
          type="button"
          className="process-button"
          onClick={onProcess}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polygon points="5 3 19 12 5 21 5 3"></polygon>
          </svg>
          Process Document Pipeline
        </button>
      )}
    </div>
  );
}
