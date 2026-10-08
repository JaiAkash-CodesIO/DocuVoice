export default function SamplePicker({ samples, onSelectSample, isProcessing }) {
  const getIcon = (type) => {
    switch (type) {
      case "invoice":
        return "🧾";
      case "receipt":
        return "🛒";
      case "resume":
        return "👤";
      default:
        return "📄";
    }
  };

  return (
    <div className="sample-picker-section">
      <div className="sample-picker-header">
        <span className="eyebrow">INSTANT DEMO</span>
        <h3>Try Preloaded Sample Documents</h3>
        <p>No document handy? Test the full pipeline with one click:</p>
      </div>

      <div className="sample-grid">
        {samples.map((sample) => (
          <div
            key={sample.id}
            className={`sample-card ${isProcessing ? "disabled" : ""}`}
            onClick={() => !isProcessing && onSelectSample(sample.id)}
          >
            <div className="sample-card-icon">{getIcon(sample.document_type)}</div>
            <div className="sample-card-body">
              <div className="sample-card-top">
                <h4>{sample.name}</h4>
                <span className={`type-tag tag-${sample.document_type}`}>
                  {sample.document_type}
                </span>
              </div>
              <p>{sample.description}</p>
            </div>
            <div className="sample-card-action">
              <span>Run Pipeline →</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
