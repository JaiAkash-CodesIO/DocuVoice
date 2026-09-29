import { useState } from "react";
import "./index.css";

const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const handleFile = (selectedFile) => {
    if (!selectedFile) return;

    const allowedTypes = [
      "application/pdf",
      "image/png",
      "image/jpeg",
    ];

    if (!allowedTypes.includes(selectedFile.type)) {
      setError("Please select a PDF, PNG, or JPG file.");
      return;
    }

    setFile(selectedFile);
    setError("");
    setResult(null);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setDragging(false);
    handleFile(event.dataTransfer.files[0]);
  };

  const processDocument = async () => {
    if (!file) {
      setError("Please select a document first.");
      return;
    }

    try {
      setError("");
      setResult(null);
      setStatus("Uploading document...");

      const formData = new FormData();
      formData.append("file", file);

      const uploadResponse = await fetch(
        `${API_BASE_URL}/documents/upload`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!uploadResponse.ok) {
        throw new Error("Document upload failed.");
      }

      const uploadData = await uploadResponse.json();
      const documentId = uploadData.document_id;

      setStatus("Preprocessing document...");

      const preprocessResponse = await fetch(
        `${API_BASE_URL}/documents/${documentId}/preprocess`,
        {
          method: "POST",
        }
      );

      if (!preprocessResponse.ok) {
        const data = await preprocessResponse.json();
        throw new Error(data.detail || "Preprocessing failed.");
      }

      setStatus("Running OCR...");

      const ocrResponse = await fetch(
        `${API_BASE_URL}/documents/${documentId}/ocr`,
        {
          method: "POST",
        }
      );

      if (!ocrResponse.ok) {
        const data = await ocrResponse.json();
        throw new Error(data.detail || "OCR processing failed.");
      }

      setStatus("Extracting document information...");

      const extractionResponse = await fetch(
        `${API_BASE_URL}/documents/${documentId}/extract`,
        {
          method: "POST",
        }
      );

      if (!extractionResponse.ok) {
        const data = await extractionResponse.json();
        throw new Error(
          data.detail || "Document extraction failed."
        );
      }

      const extractionData = await extractionResponse.json();

      setResult(extractionData.extraction);
      setStatus("");
    } catch (err) {
      setStatus("");
      setError(err.message || "Something went wrong.");
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div className="brand">
          <div className="brand-mark">D</div>
          <span>DocuVoice</span>
        </div>

        <span className="header-label">
          Document Extraction
        </span>
      </header>

      <main className="main">
        {!result ? (
          <section className="upload-page">
            <div className="intro">
              <p className="eyebrow">DOCUMENT INTELLIGENCE</p>

              <h1>
                Extract useful information
                <br />
                from your documents.
              </h1>

              <p className="subtitle">
                Upload a document and DocuVoice will extract
                text, fields, sections, entities, and tables.
              </p>
            </div>

            <div
              className={`upload-box ${
                dragging ? "dragging" : ""
              }`}
              onDragOver={(event) => {
                event.preventDefault();
                setDragging(true);
              }}
              onDragLeave={() => setDragging(false)}
              onDrop={handleDrop}
            >
              <div className="upload-icon">↑</div>

              <h2>Upload a document</h2>

              <p>
                Drag and drop your file here, or choose one
                from your computer.
              </p>

              <label className="choose-button">
                Choose file
                <input
                  type="file"
                  accept=".pdf,.png,.jpg,.jpeg"
                  onChange={(event) =>
                    handleFile(event.target.files[0])
                  }
                />
              </label>

              <span className="file-types">
                PDF, PNG, JPG or JPEG · Max 10 MB
              </span>

              {file && (
                <div className="selected-file">
                  <span>{file.name}</span>
                  <span>
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </span>
                </div>
              )}
            </div>

            {error && (
              <div className="message error">
                {error}
              </div>
            )}

            {status && (
              <div className="message status">
                {status}
              </div>
            )}

            <button
              className="process-button"
              onClick={processDocument}
              disabled={!file || Boolean(status)}
            >
              {status ? "Processing..." : "Process document"}
            </button>
          </section>
        ) : (
          <section className="results-page">
            <div className="results-header">
              <div>
                <p className="eyebrow">EXTRACTION RESULT</p>
                <h1>{file?.name}</h1>
              </div>

              <button
                className="secondary-button"
                onClick={() => {
                  setResult(null);
                  setFile(null);
                }}
              >
                Process another
              </button>
            </div>

            <div className="overview">
              <div>
                <span className="label">
                  Document type
                </span>
                <strong>
                  {result.document_type || "Unknown"}
                </strong>
              </div>

              <div>
                <span className="label">
                  OCR confidence
                </span>
                <strong>
                  {result.ocr?.average_confidence ?? 0}%
                </strong>
              </div>

              <div>
                <span className="label">
                  Words detected
                </span>
                <strong>
                  {result.ocr?.word_count ?? 0}
                </strong>
              </div>
            </div>

            <div className="results-grid">
              <section className="result-card">
                <h2>Fields</h2>

                {result.fields?.length ? (
                  <div className="field-list">
                    {result.fields.map((field, index) => (
                      <div
                        className="field"
                        key={index}
                      >
                        <span>{field.key}</span>
                        <strong>{field.value}</strong>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="empty">
                    No structured fields detected.
                  </p>
                )}
              </section>

              <section className="result-card">
                <h2>Entities</h2>

                <div className="entity-group">
                  <span>Emails</span>
                  <p>
                    {result.entities?.emails?.length
                      ? result.entities.emails.join(", ")
                      : "None detected"}
                  </p>
                </div>

                <div className="entity-group">
                  <span>Phone numbers</span>
                  <p>
                    {result.entities?.phone_numbers?.length
                      ? result.entities.phone_numbers.join(", ")
                      : "None detected"}
                  </p>
                </div>

                <div className="entity-group">
                  <span>Dates</span>
                  <p>
                    {result.entities?.dates?.length
                      ? result.entities.dates.join(", ")
                      : "None detected"}
                  </p>
                </div>

                <div className="entity-group">
                  <span>URLs</span>
                  <p>
                    {result.entities?.urls?.length
                      ? result.entities.urls.join(", ")
                      : "None detected"}
                  </p>
                </div>
              </section>
            </div>

            <section className="result-card">
              <h2>Sections</h2>

              {result.sections?.length ? (
                <div className="sections">
                  {result.sections.map(
                    (section, index) => (
                      <div
                        className="section"
                        key={index}
                      >
                        <h3>{section.title}</h3>
                        <p>{section.content}</p>
                      </div>
                    )
                  )}
                </div>
              ) : (
                <p className="empty">
                  No sections detected.
                </p>
              )}
            </section>

            <section className="result-card">
              <h2>Tables</h2>

              {result.tables?.length ? (
                result.tables.map((table, tableIndex) => (
                  <div
                    className="table-wrapper"
                    key={tableIndex}
                  >
                    <table>
                      <thead>
                        <tr>
                          {table.headers.map(
                            (header, index) => (
                              <th key={index}>
                                {header}
                              </th>
                            )
                          )}
                        </tr>
                      </thead>

                      <tbody>
                        {table.rows.map(
                          (row, rowIndex) => (
                            <tr key={rowIndex}>
                              {row.map(
                                (cell, cellIndex) => (
                                  <td key={cellIndex}>
                                    {cell}
                                  </td>
                                )
                              )}
                            </tr>
                          )
                        )}
                      </tbody>
                    </table>
                  </div>
                ))
              ) : (
                <p className="empty">
                  No tables detected.
                </p>
              )}
            </section>

            <section className="result-card text-card">
              <h2>Extracted text</h2>
              <pre>{result.text || "No text detected."}</pre>
            </section>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;