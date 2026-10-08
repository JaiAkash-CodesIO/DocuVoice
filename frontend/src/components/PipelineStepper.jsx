export default function PipelineStepper({ currentStep }) {
  const steps = [
    { id: 1, label: "Ingestion", desc: "Validating file & UUID tagging" },
    { id: 2, label: "Preprocessing", desc: "Aspect normalization & contrast" },
    { id: 3, label: "Region OCR", desc: "Tesseract multi-pass segmentation" },
    { id: 4, label: "Extraction", desc: "Heuristic classification & entities" },
  ];

  return (
    <div className="stepper-card">
      <div className="stepper-header">
        <div className="spinner-orbit"></div>
        <div>
          <h4>Pipeline Processing Active</h4>
          <p>Converting unstructured visual document into typed JSON schema</p>
        </div>
      </div>

      <div className="stepper-track">
        {steps.map((step) => {
          const isDone = currentStep > step.id;
          const isActive = currentStep === step.id;
          return (
            <div
              key={step.id}
              className={`stepper-item ${isDone ? "completed" : ""} ${isActive ? "active" : ""}`}
            >
              <div className="stepper-indicator">
                {isDone ? (
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                ) : (
                  <span>{step.id}</span>
                )}
              </div>
              <div className="stepper-details">
                <span className="step-label">{step.label}</span>
                <span className="step-desc">{step.desc}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
