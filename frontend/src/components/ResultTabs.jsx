import { useState } from "react";

export default function ResultTabs({ result }) {
  // Put Sections tab first as requested
  const [activeTab, setActiveTab] = useState("sections");
  const [copiedText, setCopiedText] = useState(null);
  const [sectionFilter, setSectionFilter] = useState("");

  const tablesCount = result.tables?.length || 0;
  const fieldsCount = result.fields?.length || 0;
  const sectionsCount = result.sections?.length || 0;
  const entitiesCount =
    (result.entities?.emails?.length || 0) +
    (result.entities?.phone_numbers?.length || 0) +
    (result.entities?.dates?.length || 0) +
    (result.entities?.urls?.length || 0);

  const copyToClipboard = (text, label) => {
    navigator.clipboard.writeText(text);
    setCopiedText(label);
    setTimeout(() => setCopiedText(null), 1500);
  };

  const getSectionCategory = (title) => {
    const t = title.toUpperCase();
    if (t.includes("SKILL") || t.includes("TECH")) return { icon: "💻", tag: "Skills & Tech" };
    if (t.includes("EXPERIENCE") || t.includes("INTERN") || t.includes("WORK") || t.includes("TRAINING"))
      return { icon: "💼", tag: "Experience" };
    if (t.includes("PROJECT")) return { icon: "🚀", tag: "Projects" };
    if (t.includes("EDUCATION") || t.includes("ACADEMIC") || t.includes("DEGREE"))
      return { icon: "🎓", tag: "Education" };
    if (t.includes("SUMMARY") || t.includes("PROFILE") || t.includes("ABOUT"))
      return { icon: "📝", tag: "Summary" };
    if (t.includes("CERTIF") || t.includes("AWARD"))
      return { icon: "🏆", tag: "Certifications" };
    return { icon: "📑", tag: "Section" };
  };

  // Format section text into bullet points if it contains list indicators
  const renderFormattedContent = (content) => {
    if (!content) return null;

    // Check if content has bullet characters or line-based items
    const hasBullets = content.includes("•") || content.includes("·") || content.includes("- ");
    if (hasBullets) {
      const parts = content.split(/[•·]|\s-\s/).map((p) => p.trim()).filter(Boolean);
      if (parts.length > 1) {
        return (
          <ul className="section-bullet-list">
            {parts.map((part, pIdx) => (
              <li key={pIdx}>{part}</li>
            ))}
          </ul>
        );
      }
    }

    // Check for multiple sentences or paragraphs
    return <p className="section-body">{content}</p>;
  };

  const filteredSections = (result.sections || []).filter((s) => {
    if (!sectionFilter.trim()) return true;
    const q = sectionFilter.toLowerCase();
    return s.title.toLowerCase().includes(q) || s.content.toLowerCase().includes(q);
  });

  return (
    <div className="results-tabs-container">
      {/* TABS HEADER - SECTIONS IS FIRST */}
      <div className="tabs-header">
        <button
          className={`tab-btn ${activeTab === "sections" ? "active" : ""}`}
          onClick={() => setActiveTab("sections")}
        >
          <span>Sections</span>
          {sectionsCount > 0 && <span className="tab-pill">{sectionsCount}</span>}
        </button>

        <button
          className={`tab-btn ${activeTab === "tables" ? "active" : ""}`}
          onClick={() => setActiveTab("tables")}
        >
          <span>Tables</span>
          {tablesCount > 0 && <span className="tab-pill">{tablesCount}</span>}
        </button>

        <button
          className={`tab-btn ${activeTab === "fields" ? "active" : ""}`}
          onClick={() => setActiveTab("fields")}
        >
          <span>Fields</span>
          {fieldsCount > 0 && <span className="tab-pill">{fieldsCount}</span>}
        </button>

        <button
          className={`tab-btn ${activeTab === "entities" ? "active" : ""}`}
          onClick={() => setActiveTab("entities")}
        >
          <span>Entities</span>
          {entitiesCount > 0 && <span className="tab-pill">{entitiesCount}</span>}
        </button>

        <button
          className={`tab-btn ${activeTab === "json" ? "active" : ""}`}
          onClick={() => setActiveTab("json")}
        >
          <span>Raw Text & JSON</span>
        </button>
      </div>

      <div className="tab-content-area">
        {/* TAB 1: SECTIONS (NOW FIRST) */}
        {activeTab === "sections" && (
          <div className="tab-pane">
            <div className="tab-pane-header">
              <div className="pane-title-group">
                <h4>Extracted Document Sections</h4>
                <span className="pane-subtext">
                  Discovered {sectionsCount} structured heading blocks
                </span>
              </div>

              {sectionsCount > 2 && (
                <div className="section-search-box">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="11" cy="11" r="8" />
                    <line x1="21" y1="21" x2="16.65" y2="16.65" />
                  </svg>
                  <input
                    type="text"
                    placeholder="Search sections or keywords..."
                    value={sectionFilter}
                    onChange={(e) => setSectionFilter(e.target.value)}
                    className="section-search-input"
                  />
                  {sectionFilter && (
                    <button className="clear-search-btn" onClick={() => setSectionFilter("")}>
                      &times;
                    </button>
                  )}
                </div>
              )}
            </div>

            {filteredSections.length > 0 ? (
              <div className="sections-list">
                {filteredSections.map((section, sIndex) => {
                  const meta = getSectionCategory(section.title);
                  return (
                    <div key={sIndex} className="section-block modern-section">
                      <div className="section-block-top">
                        <div className="section-title-wrap">
                          <span className="section-cat-icon">{meta.icon}</span>
                          <h4 className="section-title">{section.title}</h4>
                          <span className="section-cat-tag">{meta.tag}</span>
                        </div>

                        <button
                          className="copy-section-btn"
                          onClick={() => copyToClipboard(`${section.title}\n\n${section.content}`, `sec-${sIndex}`)}
                          title="Copy section"
                        >
                          {copiedText === `sec-${sIndex}` ? "✓ Copied" : "Copy"}
                        </button>
                      </div>

                      <div className="section-content-wrapper">
                        {renderFormattedContent(section.content)}
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="empty-state">
                <span className="empty-icon">📑</span>
                <p>
                  {sectionFilter
                    ? `No sections matching "${sectionFilter}"`
                    : "No discrete section headings discovered."}
                </p>
                <small>Documents with clear headings will be organized into structured blocks here.</small>
              </div>
            )}
          </div>
        )}

        {/* TAB 2: TABLES */}
        {activeTab === "tables" && (
          <div className="tab-pane">
            {tablesCount > 0 ? (
              result.tables.map((table, tIndex) => (
                <div key={tIndex} className="table-card">
                  <div className="table-card-header">
                    <h4>Reconstructed Table #{tIndex + 1}</h4>
                    <span className="table-meta">{table.rows.length} rows &middot; {table.headers.length} columns</span>
                  </div>
                  <div className="table-scroll-wrapper">
                    <table className="data-table">
                      <thead>
                        <tr>
                          {table.headers.map((header, hIndex) => (
                            <th key={hIndex}>{header || `Col ${hIndex + 1}`}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {table.rows.map((row, rIndex) => (
                          <tr key={rIndex}>
                            {row.map((cell, cIndex) => (
                              <td key={cIndex}>{cell || "—"}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ))
            ) : (
              <div className="empty-state">
                <span className="empty-icon">📊</span>
                <p>No tabular structures detected in this document.</p>
                <small>Documents with clear vertical columns or grid lines are automatically reconstructed into tables.</small>
              </div>
            )}
          </div>
        )}

        {/* TAB 3: FIELDS */}
        {activeTab === "fields" && (
          <div className="tab-pane">
            {fieldsCount > 0 ? (
              <div className="fields-grid">
                {result.fields.map((field, fIndex) => (
                  <div key={fIndex} className="field-card">
                    <span className="field-key">{field.key}</span>
                    <strong className="field-val">{field.value}</strong>
                    <button
                      className="field-copy-btn"
                      onClick={() => copyToClipboard(field.value, `field-${fIndex}`)}
                      title="Copy value"
                    >
                      {copiedText === `field-${fIndex}` ? "✓" : "📋"}
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <span className="empty-icon">🏷️</span>
                <p>No key-value pairs discovered.</p>
                <small>Key-value pairs matching standard "Label: Value" syntax will appear here.</small>
              </div>
            )}
          </div>
        )}

        {/* TAB 4: ENTITIES */}
        {activeTab === "entities" && (
          <div className="tab-pane">
            <div className="entities-matrix">
              {/* Emails */}
              <div className="entity-box">
                <div className="entity-box-title">
                  <span className="entity-icon">✉️</span>
                  <h5>Email Addresses</h5>
                  <span className="entity-count">({result.entities?.emails?.length || 0})</span>
                </div>
                {result.entities?.emails?.length > 0 ? (
                  <div className="entity-tags">
                    {result.entities.emails.map((email, idx) => (
                      <a
                        key={idx}
                        href={`mailto:${email}`}
                        className="entity-chip link"
                        title="Click to send email"
                      >
                        {email}
                        <small className="entity-action-hint">✉ Send</small>
                      </a>
                    ))}
                  </div>
                ) : (
                  <span className="none-found">None discovered</span>
                )}
              </div>

              {/* Phone Numbers */}
              <div className="entity-box">
                <div className="entity-box-title">
                  <span className="entity-icon">📞</span>
                  <h5>Phone Numbers</h5>
                  <span className="entity-count">({result.entities?.phone_numbers?.length || 0})</span>
                </div>
                {result.entities?.phone_numbers?.length > 0 ? (
                  <div className="entity-tags">
                    {result.entities.phone_numbers.map((phone, idx) => (
                      <a
                        key={idx}
                        href={`tel:${phone}`}
                        className="entity-chip link"
                        title="Click to call"
                      >
                        {phone}
                        <small className="entity-action-hint">📞 Call</small>
                      </a>
                    ))}
                  </div>
                ) : (
                  <span className="none-found">None discovered</span>
                )}
              </div>

              {/* Hyperlinks & Profiles */}
              <div className="entity-box">
                <div className="entity-box-title">
                  <span className="entity-icon">🔗</span>
                  <h5>Links & Professional Profiles</h5>
                  <span className="entity-count">({result.entities?.urls?.length || 0})</span>
                </div>
                {result.entities?.urls?.length > 0 ? (
                  <div className="entity-tags">
                    {result.entities.urls.map((url, idx) => {
                      const isLinkedIn = url.includes("linkedin.com");
                      const isGitHub = url.includes("github.com");
                      return (
                        <a
                          key={idx}
                          href={url}
                          target="_blank"
                          rel="noreferrer"
                          className={`entity-chip link ${isLinkedIn ? "chip-linkedin" : ""} ${isGitHub ? "chip-github" : ""}`}
                        >
                          {isLinkedIn && "💼 LinkedIn: "}
                          {isGitHub && "🐙 GitHub: "}
                          {url.replace(/^https?:\/\//, "")} ↗
                        </a>
                      );
                    })}
                  </div>
                ) : (
                  <span className="none-found">None discovered</span>
                )}
              </div>

              {/* Dates */}
              <div className="entity-box">
                <div className="entity-box-title">
                  <span className="entity-icon">📅</span>
                  <h5>Dates Recognized</h5>
                  <span className="entity-count">({result.entities?.dates?.length || 0})</span>
                </div>
                {result.entities?.dates?.length > 0 ? (
                  <div className="entity-tags">
                    {result.entities.dates.map((date, idx) => (
                      <span
                        key={idx}
                        className="entity-chip"
                        onClick={() => copyToClipboard(date, `date-${idx}`)}
                        title="Click to copy"
                      >
                        {date}
                        <small>{copiedText === `date-${idx}` ? " (Copied)" : ""}</small>
                      </span>
                    ))}
                  </div>
                ) : (
                  <span className="none-found">None discovered</span>
                )}
              </div>
            </div>
          </div>
        )}

        {/* TAB 5: RAW TEXT & JSON */}
        {activeTab === "json" && (
          <div className="tab-pane json-pane">
            <div className="split-code-view">
              <div className="code-block">
                <div className="code-header">
                  <span>Structured Schema Output (JSON)</span>
                  <button
                    className="small-btn"
                    onClick={() => copyToClipboard(JSON.stringify(result, null, 2), "json-code")}
                  >
                    {copiedText === "json-code" ? "Copied!" : "Copy"}
                  </button>
                </div>
                <pre className="code-content">{JSON.stringify(result, null, 2)}</pre>
              </div>

              <div className="code-block">
                <div className="code-header">
                  <span>Raw OCR Stream</span>
                  <button
                    className="small-btn"
                    onClick={() => copyToClipboard(result.text || "", "text-code")}
                  >
                    {copiedText === "text-code" ? "Copied!" : "Copy"}
                  </button>
                </div>
                <pre className="code-content">{result.text || "No text available"}</pre>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
