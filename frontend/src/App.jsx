import { useState, useEffect } from "react";
import Navbar from "./components/Navbar";
import Dropzone from "./components/Dropzone";
import SamplePicker from "./components/SamplePicker";
import PipelineStepper from "./components/PipelineStepper";
import DocumentViewer from "./components/DocumentViewer";
import OverviewBadges from "./components/OverviewBadges";
import ExportBar from "./components/ExportBar";
import ResultTabs from "./components/ResultTabs";
import "./index.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

function App() {
  const [file, setFile] = useState(null);
  const [documentId, setDocumentId] = useState(null);
  const [statusStep, setStatusStep] = useState(0); // 0 = idle, 1..4 = pipeline steps
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [durationMs, setDurationMs] = useState(null);
  const [samples, setSamples] = useState([]);

  // Fetch preloaded sample document list on load
  useEffect(() => {
    async function loadSamples() {
      try {
        const res = await fetch(`${API_BASE_URL}/documents/samples`);
        if (res.ok) {
          const data = await res.json();
          setSamples(data);
        }
      } catch {
        // Fallback static samples if backend is starting up
        setSamples([
          {
            id: "sample-invoice",
            name: "Standard Tech Invoice",
            document_type: "invoice",
            description: "Tax invoice with line-item table, vendor, customer, and tax calculations.",
            filename: "sample_invoice.png",
          },
          {
            id: "sample-receipt",
            name: "Retail Store Receipt",
            document_type: "receipt",
            description: "Store receipt with transaction timestamp, cashier ID, and itemized totals.",
            filename: "sample_receipt.png",
          },
          {
            id: "sample-resume",
            name: "Software Engineer Resume",
            document_type: "resume",
            description: "Professional CV with contact details, sections, skills, and work history.",
            filename: "sample_resume.png",
          },
        ]);
      }
    }
    loadSamples();
  }, []);

  const handleFileSelect = (selectedFile) => {
    if (!selectedFile) return;
    const allowed = ["application/pdf", "image/png", "image/jpeg", "image/jpg"];
    if (!allowed.includes(selectedFile.type) && !selectedFile.name.match(/\.(pdf|png|jpe?g)$/i)) {
      setError("Please select a PDF, PNG, or JPG file.");
      return;
    }
    if (selectedFile.size > 10 * 1024 * 1024) {
      setError("File exceeds the 10 MB maximum limit.");
      return;
    }
    setFile(selectedFile);
    setError("");
  };

  const handleClearFile = () => {
    setFile(null);
    setError("");
  };

  const handleReset = () => {
    setFile(null);
    setDocumentId(null);
    setResult(null);
    setError("");
    setStatusStep(0);
    setDurationMs(null);
  };

  // Process user uploaded document using unified pipeline
  const processUploadedDocument = async () => {
    if (!file) return;

    try {
      setError("");
      setResult(null);
      setStatusStep(1);

      const formData = new FormData();
      formData.append("file", file);

      // Advance stepper visually to show progressive pipeline
      const stepTimer1 = setTimeout(() => setStatusStep(2), 500);
      const stepTimer2 = setTimeout(() => setStatusStep(3), 1200);
      const stepTimer3 = setTimeout(() => setStatusStep(4), 1800);

      const response = await fetch(`${API_BASE_URL}/documents/process`, {
        method: "POST",
        body: formData,
      });

      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      clearTimeout(stepTimer3);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Document processing failed");
      }

      const data = await response.json();
      setDocumentId(data.document_id);
      setResult(data.extraction);
      setDurationMs(data.duration_ms);
      setStatusStep(0);
    } catch (err) {
      setStatusStep(0);
      setError(err.message || "An unexpected error occurred during processing.");
    }
  };

  // Process sample document with one-click
  const processSampleDocument = async (sampleId) => {
    try {
      setError("");
      setResult(null);
      setStatusStep(1);

      const sample = samples.find((s) => s.id === sampleId);
      if (sample) {
        setFile({ name: sample.filename, size: 45000, type: "image/png" });
      }

      const stepTimer1 = setTimeout(() => setStatusStep(2), 400);
      const stepTimer2 = setTimeout(() => setStatusStep(3), 900);
      const stepTimer3 = setTimeout(() => setStatusStep(4), 1400);

      const response = await fetch(
        `${API_BASE_URL}/documents/samples/${sampleId}/process`,
        { method: "POST" }
      );

      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      clearTimeout(stepTimer3);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Sample processing failed");
      }

      const data = await response.json();
      setDocumentId(data.document_id);
      setResult(data.extraction);
      setDurationMs(data.duration_ms);
      setStatusStep(0);
    } catch (err) {
      setStatusStep(0);
      setError(err.message || "Failed to process sample document.");
    }
  };

  const isProcessing = statusStep > 0;

  return (
    <div className="app">
      <Navbar onReset={handleReset} hasResult={Boolean(result)} />

      <main className="main-content">
        {!result && !isProcessing && (
          <section className="hero-section">
            <div className="hero-text-block">
              <span className="eyebrow">INTELLIGENT DOCUMENT RECOGNITION</span>
              <h1>Extract High-Accuracy Structured Data from Any Document</h1>
              <p className="subtitle">
                DocuVoice automatically classifies document intent, runs region-aware
                multi-pass OCR, reconstructs table matrices, and extracts typed schema entities.
              </p>
            </div>

            {samples.length > 0 && (
              <SamplePicker
                samples={samples}
                onSelectSample={processSampleDocument}
                isProcessing={isProcessing}
              />
            )}

            <div className="divider-row">
              <span>OR UPLOAD CUSTOM FILE</span>
            </div>

            <Dropzone
              file={file}
              onFileSelect={handleFileSelect}
              onClearFile={handleClearFile}
              onProcess={processUploadedDocument}
              isProcessing={isProcessing}
              error={error}
            />
          </section>
        )}

        {isProcessing && (
          <section className="processing-section">
            <PipelineStepper currentStep={statusStep} />
          </section>
        )}

        {result && (
          <section className="results-container">
            <div className="results-top-bar">
              <div className="result-headline">
                <span className="eyebrow">EXTRACTION SUMMARY</span>
                <h2>{file?.name || "Processed Document"}</h2>
              </div>
              <ExportBar result={result} filename={file?.name?.replace(/\.[^/.]+$/, "")} />
            </div>

            <OverviewBadges result={result} durationMs={durationMs} />

            <div className="split-view-container">
              {documentId && (
                <div className="split-col-left">
                  <DocumentViewer
                    documentId={documentId}
                    file={file}
                    apiBaseUrl={API_BASE_URL}
                  />
                </div>
              )}

              <div className={`split-col-right ${!documentId ? "full-width" : ""}`}>
                <ResultTabs result={result} />
              </div>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;