export default function OverviewBadges({ result, durationMs }) {
  const confidence = result.ocr?.average_confidence ?? 0;

  const getConfidenceColor = (score) => {
    if (score >= 80) return "high";
    if (score >= 60) return "medium";
    return "low";
  };

  const getDocTypeIcon = (type) => {
    switch (type) {
      case "invoice":
        return "🧾";
      case "receipt":
        return "🛒";
      case "resume":
        return "👤";
      case "report":
        return "📊";
      case "certificate":
        return "📜";
      default:
        return "📄";
    }
  };

  return (
    <div className="overview-grid">
      <div className="metric-card">
        <span className="metric-label">DOCUMENT CLASSIFICATION</span>
        <div className="metric-value-row">
          <span className="type-icon">{getDocTypeIcon(result.document_type)}</span>
          <strong className="metric-value capitalize">
            {result.document_type?.replace("_", " ") || "General Document"}
          </strong>
        </div>
        <span className="metric-subtext">Heuristic intent analysis</span>
      </div>

      <div className="metric-card">
        <span className="metric-label">OCR CONFIDENCE</span>
        <div className="metric-value-row">
          <strong className={`metric-value confidence-${getConfidenceColor(confidence)}`}>
            {confidence}%
          </strong>
          <span className={`confidence-pill pill-${getConfidenceColor(confidence)}`}>
            {confidence >= 80 ? "Optimal" : confidence >= 60 ? "Acceptable" : "Review"}
          </span>
        </div>
        <span className="metric-subtext">Multi-pass PSM 6 & 11 evaluation</span>
      </div>

      <div className="metric-card">
        <span className="metric-label">TOKENS RECOGNIZED</span>
        <div className="metric-value-row">
          <strong className="metric-value">
            {result.ocr?.word_count ?? 0}
          </strong>
          <span className="unit-label">words</span>
        </div>
        <span className="metric-subtext">Spatial bounding boxes mapped</span>
      </div>

      <div className="metric-card">
        <span className="metric-label">PIPELINE LATENCY</span>
        <div className="metric-value-row">
          <strong className="metric-value">
            {durationMs ? Math.round(durationMs) : "< 1500"}
          </strong>
          <span className="unit-label">ms</span>
        </div>
        <span className="metric-subtext">End-to-end multi-stage execution</span>
      </div>
    </div>
  );
}
