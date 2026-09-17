import { useEffect, useState } from "react";

import {
  apiRequest,
  compareDocuments,
} from "../services/api";


interface DocumentItem {
  id: string;
  filename: string;
  status: string;
  page_count: number;
  chunk_count: number;
}


interface ComparisonResult {
  document_a: {
    name: string;
    summary: string;
  };

  document_b: {
    name: string;
    summary: string;
  };

  common_information: string[];
  key_differences: string[];
  document_a_unique: string[];
  document_b_unique: string[];
  comparison_summary: string;
}


export default function DocumentComparison() {

  const [documents, setDocuments] =
    useState<DocumentItem[]>([]);

  const [documentA, setDocumentA] =
    useState("");

  const [documentB, setDocumentB] =
    useState("");

  const [comparison, setComparison] =
    useState<ComparisonResult | null>(null);

  const [loading, setLoading] =
    useState(false);

  const [loadingDocuments, setLoadingDocuments] =
    useState(true);

  const [error, setError] =
    useState("");


  // ============================================================
  // LOAD DOCUMENTS
  // ============================================================

  useEffect(() => {

    loadDocuments();

  }, []);


  const loadDocuments = async () => {

    try {

      setLoadingDocuments(true);
      setError("");

      const data =
        await apiRequest(
          "/api/documents"
        );

      setDocuments(
        data.documents || []
      );

    } catch (err) {

      setError(
        err instanceof Error
          ? err.message
          : "Failed to load documents"
      );

    } finally {

      setLoadingDocuments(false);

    }
  };


  // ============================================================
  // COMPARE DOCUMENTS
  // ============================================================

  const handleCompare = async () => {

    if (!documentA || !documentB) {

      setError(
        "Please select both documents."
      );

      return;
    }


    if (documentA === documentB) {

      setError(
        "Please select two different documents."
      );

      return;
    }


    try {

      setLoading(true);
      setError("");
      setComparison(null);


      const data =
        await compareDocuments(
          documentA,
          documentB
        );


      if (!data.success) {

        throw new Error(
          data.message ||
          "Document comparison failed"
        );
      }


      setComparison(
        data.comparison
      );

    } catch (err) {

      setError(
        err instanceof Error
          ? err.message
          : "Document comparison failed"
      );

    } finally {

      setLoading(false);

    }
  };


  return (

    <div className="comparison-editorial">

      {/* ======================================================
          HEADER
      ====================================================== */}

      <div className="comparison-header">

        <div>

          <div className="comparison-eyebrow">
            KNOWLEDGE ANALYSIS
          </div>

          <h2>
            Document Comparison
          </h2>

          <p>
            Compare two enterprise documents
            using AI-powered analysis.
          </p>

        </div>


        <div className="comparison-number">
          03
        </div>

      </div>


      <div className="comparison-divider" />


      {/* ======================================================
          DOCUMENT SELECTION
      ====================================================== */}

      <div className="comparison-select-grid">

        <div className="comparison-select-group">

          <label>
            DOCUMENT A
          </label>

          <select
            value={documentA}
            onChange={(e) =>
              setDocumentA(
                e.target.value
              )
            }
            disabled={loadingDocuments}
          >

            <option value="">
              Select Document A
            </option>

            {documents.map(
              (document) => (

                <option
                  key={document.id}
                  value={document.id}
                >
                  {document.filename}
                </option>

              )
            )}

          </select>

        </div>


        <div className="comparison-vs">
          VS
        </div>


        <div className="comparison-select-group">

          <label>
            DOCUMENT B
          </label>

          <select
            value={documentB}
            onChange={(e) =>
              setDocumentB(
                e.target.value
              )
            }
            disabled={loadingDocuments}
          >

            <option value="">
              Select Document B
            </option>

            {documents.map(
              (document) => (

                <option
                  key={document.id}
                  value={document.id}
                >
                  {document.filename}
                </option>

              )
            )}

          </select>

        </div>

      </div>


      {/* ======================================================
          COMPARE BUTTON
      ====================================================== */}

      <button
        onClick={handleCompare}
        disabled={
          loading ||
          loadingDocuments ||
          !documentA ||
          !documentB
        }
        className="comparison-button"
      >

        {loading
          ? "Comparing Documents..."
          : "Compare Documents →"}

      </button>


      {/* ======================================================
          ERROR
      ====================================================== */}

      {error && (

        <div className="comparison-error">

          <span>!</span>

          {error}

        </div>

      )}


      {/* ======================================================
          COMPARISON RESULT
      ====================================================== */}

      {comparison && (

        <div className="comparison-result">

          {/* SUMMARY */}

          <div className="comparison-summary">

            <div className="comparison-result-label">
              AI ANALYSIS
            </div>

            <h3>
              Comparison Summary
            </h3>

            <p>
              {comparison.comparison_summary}
            </p>

          </div>


          {/* DOCUMENT SUMMARIES */}

          <div className="comparison-document-grid">

            <div className="comparison-document-card">

              <div className="comparison-card-number">
                A
              </div>

              <div className="comparison-result-label">
                DOCUMENT A
              </div>

              <h3>
                {comparison.document_a.name}
              </h3>

              <p>
                {comparison.document_a.summary}
              </p>

            </div>


            <div className="comparison-document-card">

              <div className="comparison-card-number">
                B
              </div>

              <div className="comparison-result-label">
                DOCUMENT B
              </div>

              <h3>
                {comparison.document_b.name}
              </h3>

              <p>
                {comparison.document_b.summary}
              </p>

            </div>

          </div>


          {/* COMMON INFORMATION */}

          <ComparisonSection
            title="Common Information"
            number="01"
            items={
              comparison.common_information
            }
            emptyMessage=
              "No common information identified."
          />


          {/* KEY DIFFERENCES */}

          <ComparisonSection
            title="Key Differences"
            number="02"
            items={
              comparison.key_differences
            }
            emptyMessage=
              "No major differences identified."
          />


          {/* DOCUMENT A UNIQUE */}

          <ComparisonSection
            title="Document A — Unique Information"
            number="03"
            items={
              comparison.document_a_unique
            }
            emptyMessage=
              "No unique information identified."
          />


          {/* DOCUMENT B UNIQUE */}

          <ComparisonSection
            title="Document B — Unique Information"
            number="04"
            items={
              comparison.document_b_unique
            }
            emptyMessage=
              "No unique information identified."
          />

        </div>

      )}

    </div>
  );
}


// ============================================================
// COMPARISON SECTION
// ============================================================

interface ComparisonSectionProps {
  title: string;
  number: string;
  items: string[];
  emptyMessage: string;
}


function ComparisonSection({
  title,
  number,
  items,
  emptyMessage,
}: ComparisonSectionProps) {

  return (

    <div className="comparison-section">

      <div className="comparison-section-number">
        {number}
      </div>


      <div className="comparison-section-content">

        <h3>
          {title}
        </h3>


        {items.length === 0 ? (

          <p className="comparison-empty">
            {emptyMessage}
          </p>

        ) : (

          <ul>

            {items.map(
              (item, index) => (

                <li key={index}>
                  {item}
                </li>

              )
            )}

          </ul>

        )}

      </div>

    </div>

  );
}