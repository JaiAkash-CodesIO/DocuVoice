import { useState } from "react";

export default function ExportBar({ result, filename }) {
  const [copied, setCopied] = useState(false);

  const handleCopyJson = () => {
    navigator.clipboard.writeText(JSON.stringify(result, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadJson = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(result, null, 2));
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `${filename || "extraction"}_docuvoice.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const handleDownloadCsv = () => {
    if (!result.tables || result.tables.length === 0) return;
    const table = result.tables[0];
    const csvRows = [];
    if (table.headers && table.headers.length) {
      csvRows.push(table.headers.map((h) => `"${h.replace(/"/g, '""')}"`).join(","));
    }
    if (table.rows && table.rows.length) {
      table.rows.forEach((row) => {
        csvRows.push(row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(","));
      });
    }

    const csvContent = "data:text/csv;charset=utf-8," + encodeURIComponent(csvRows.join("\n"));
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", csvContent);
    downloadAnchor.setAttribute("download", `${filename || "table"}_docuvoice.csv`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const hasTables = result.tables && result.tables.length > 0;

  return (
    <div className="export-bar">
      <div className="export-status">
        <span className="export-indicator">●</span>
        <span>Extraction Ready</span>
      </div>

      <div className="export-buttons">
        <button className="export-btn" onClick={handleCopyJson}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
          </svg>
          {copied ? "Copied to Clipboard!" : "Copy JSON"}
        </button>

        <button className="export-btn" onClick={handleDownloadJson}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="7 10 12 15 17 10" />
            <line x1="12" y1="15" x2="12" y2="3" />
          </svg>
          Export JSON
        </button>

        {hasTables && (
          <button className="export-btn highlight" onClick={handleDownloadCsv}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="8" y1="13" x2="16" y2="13" />
              <line x1="8" y1="17" x2="16" y2="17" />
            </svg>
            Export Table (CSV)
          </button>
        )}
      </div>
    </div>
  );
}
