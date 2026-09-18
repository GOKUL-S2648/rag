import { useEffect, useState } from "react";

import {
  analyzeDocument,
  getDocumentAnalysis,
} from "../services/api";

import { API_URL } from "../config";



interface DocumentAnalysis {
  title?: string;
  summary?: string;
  topics?: string[];
  key_concepts?: string[];
  important_terms?: string[];
  discussion_questions?: string[];
  page_count?: number;
  chunk_count?: number;
}


interface DocumentItem {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  status: string;
  page_count: number;
  chunk_count: number;
  created_at: string;
  analysis?: DocumentAnalysis | null;
}


interface MyDocumentsProps {
  refreshKey?: number;
}


export default function MyDocuments({
  refreshKey = 0,
}: MyDocumentsProps) {

  const [documents, setDocuments] =
    useState<DocumentItem[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [analyzingId, setAnalyzingId] =
    useState<string | null>(null);

  const [selectedAnalysis, setSelectedAnalysis] =
    useState<DocumentAnalysis | null>(null);

  const [selectedDocumentName, setSelectedDocumentName] =
    useState("");

  const [analysisError, setAnalysisError] =
    useState("");


  // ============================================================
  // LOAD DOCUMENTS
  // ============================================================

  const loadDocuments = async () => {

    const token =
      localStorage.getItem(
        "access_token"
      );

    if (!token) {
      setError("Please login first.");
      setLoading(false);
      return;
    }

    try {

      setLoading(true);
      setError("");

      const response =
        await fetch(
          `${API_URL}/api/documents`,
          {
            method: "GET",

            headers: {
              Accept:
                "application/json",

              Authorization:
                `Bearer ${token}`,
            },
          }
        );


      if (response.status === 401) {

        localStorage.removeItem(
          "access_token"
        );

        localStorage.removeItem(
          "user"
        );

        setError(
          "Session expired. Please login again."
        );

        return;
      }


      if (!response.ok) {

        const text =
          await response.text();

        throw new Error(
          `Server returned ${response.status}: ${text}`
        );
      }


      const data =
        await response.json();


      if (data.success) {

        setDocuments(
          data.documents || []
        );

      } else {

        setDocuments([]);

        setError(
          data.message ||
          "Failed to load documents."
        );
      }

    } catch (error) {

      console.error(
        "Failed to load documents:",
        error
      );

      if (
        error instanceof TypeError
      ) {

        setError(
          "Cannot connect to the backend. Make sure FastAPI is running."
        );

      } else {

        setError(
          error instanceof Error
            ? error.message
            : "Failed to load documents."
        );
      }

    } finally {

      setLoading(false);

    }
  };


  useEffect(() => {

    loadDocuments();

  }, [refreshKey]);


  // ============================================================
  // FORMAT FILE SIZE
  // ============================================================

  const formatFileSize = (
    bytes: number
  ) => {

    if (!bytes) return "0 KB";

    const kb =
      bytes / 1024;

    if (kb < 1024) {
      return `${kb.toFixed(1)} KB`;
    }

    return `${(
      kb / 1024
    ).toFixed(1)} MB`;
  };


  // ============================================================
  // FORMAT DATE
  // ============================================================

  const formatDate = (
    date: string
  ) => {

    if (!date) return "";

    return new Date(
      date
    ).toLocaleDateString();
  };


  // ============================================================
  // ANALYZE DOCUMENT
  // ============================================================

  const handleAnalyze = async (
    documentId: string,
    filename: string
  ) => {

    try {

      setAnalyzingId(
        documentId
      );

      setAnalysisError("");

      setSelectedAnalysis(
        null
      );

      setSelectedDocumentName(
        filename
      );


      const response =
        await analyzeDocument(
          documentId
        );


      if (
        response.success &&
        response.analysis
      ) {

        setSelectedAnalysis(
          response.analysis
        );

        return;
      }


      const existing =
        await getDocumentAnalysis(
          documentId
        );


      if (
        existing.success &&
        existing.analysis
      ) {

        setSelectedAnalysis(
          existing.analysis
        );

      } else {

        setAnalysisError(
          "No document analysis was returned."
        );
      }

    } catch (error) {

      console.error(
        "Document analysis failed:",
        error
      );


      try {

        const existing =
          await getDocumentAnalysis(
            documentId
          );


        if (
          existing.success &&
          existing.analysis
        ) {

          setSelectedAnalysis(
            existing.analysis
          );

          return;
        }

      } catch (fallbackError) {

        console.error(
          "Failed to retrieve existing analysis:",
          fallbackError
        );
      }


      setAnalysisError(
        error instanceof Error
          ? error.message
          : "Failed to analyze document."
      );

    } finally {

      setAnalyzingId(
        null
      );

    }
  };


  // ============================================================
  // DELETE DOCUMENT
  // ============================================================

  const deleteDocument = async (
    documentId: string,
    filename: string
  ) => {

    const token =
      localStorage.getItem(
        "access_token"
      );


    if (!token) {

      setError(
        "Please login first."
      );

      return;
    }


    const confirmed =
      window.confirm(
        `Delete "${filename}"?`
      );


    if (!confirmed) {
      return;
    }


    try {

      const response =
        await fetch(
          `${API_URL}/api/documents/${documentId}`,
          {
            method: "DELETE",

            headers: {
              Accept:
                "application/json",

              Authorization:
                `Bearer ${token}`,
            },
          }
        );


      const data =
        await response.json();


      if (!response.ok) {

        throw new Error(
          data.detail ||
          data.message ||
          "Failed to delete document."
        );
      }


      setDocuments(
        previous =>
          previous.filter(
            document =>
              document.id !==
              documentId
          )
      );


      if (
        selectedDocumentName ===
        filename
      ) {

        setSelectedAnalysis(
          null
        );

        setSelectedDocumentName(
          ""
        );
      }

    } catch (error) {

      console.error(
        "Failed to delete document:",
        error
      );

      setError(
        error instanceof Error
          ? error.message
          : "Failed to delete document."
      );
    }
  };


  return (

    <div className="documents-editorial">

      {/* ======================================================
          HEADER
      ====================================================== */}

      <div className="documents-header">

        <div>

          <div className="documents-eyebrow">
            KNOWLEDGE LIBRARY
          </div>

          <h2>
            My Documents
          </h2>

          <p>
            Manage your uploaded
            knowledge documents.
          </p>

        </div>


        <div className="documents-header-right">

          <div className="documents-count">
            {documents.length
              .toString()
              .padStart(2, "0")}
          </div>

          <button
            onClick={loadDocuments}
            disabled={loading}
            className="documents-refresh"
          >
            {loading
              ? "Loading..."
              : "Refresh →"}
          </button>

        </div>

      </div>


      <div className="documents-divider" />


      {/* ======================================================
          ERROR
      ====================================================== */}

      {error && (

        <div className="documents-error">
          <span>!</span>
          {error}
        </div>

      )}


      {/* ======================================================
          ANALYSIS ERROR
      ====================================================== */}

      {analysisError && (

        <div className="documents-error">
          <span>!</span>
          {analysisError}
        </div>

      )}


      {/* ======================================================
          LOADING
      ====================================================== */}

      {loading &&
        documents.length === 0 && (

          <div className="documents-empty">
            Loading your documents...
          </div>

      )}


      {/* ======================================================
          NO DOCUMENTS
      ====================================================== */}

      {!loading &&
        documents.length === 0 &&
        !error && (

          <div className="documents-empty documents-empty-border">

            <div className="documents-empty-number">
              00
            </div>

            <div>
              No documents uploaded yet.
            </div>

          </div>

      )}


      {/* ======================================================
          DOCUMENT LIST
      ====================================================== */}

      <div className="document-list">

        {documents.map(
          (document, index) => (

            <div
              key={document.id}
              className="document-row"
            >

              {/* NUMBER */}

              <div className="document-index">
                {String(
                  index + 1
                ).padStart(2, "0")}
              </div>


              {/* INFORMATION */}

              <div className="document-info">

                <div className="document-name">
                  <span className="document-icon">
                    □
                  </span>

                  <span>
                    {document.filename}
                  </span>
                </div>


                <div className="document-meta">

                  {document.file_type?.toUpperCase()}

                  {" · "}

                  {formatFileSize(
                    document.file_size
                  )}

                  {" · "}

                  {document.page_count}
                  {" pages"}

                  {" · "}

                  {document.chunk_count}
                  {" chunks"}

                  {" · "}

                  {formatDate(
                    document.created_at
                  )}

                </div>

              </div>


              {/* ACTIONS */}

              <div className="document-actions">

                <span
                  className={
                    document.status ===
                    "READY"
                      ? "document-status ready"
                      : "document-status processing"
                  }
                >
                  {document.status}
                </span>


                <button
                  onClick={() =>
                    handleAnalyze(
                      document.id,
                      document.filename
                    )
                  }
                  disabled={
                    analyzingId ===
                    document.id
                  }
                  className="document-analyze"
                >
                  {analyzingId ===
                  document.id
                    ? "Analyzing..."
                    : "Analyze"}
                </button>


                <button
                  onClick={() =>
                    deleteDocument(
                      document.id,
                      document.filename
                    )
                  }
                  className="document-delete"
                >
                  Delete
                </button>

              </div>

            </div>

          )
        )}

      </div>


      {/* ======================================================
          DOCUMENT INTELLIGENCE
      ====================================================== */}

      {selectedAnalysis && (

        <div className="intelligence-editorial">

          <div className="intelligence-header">

            <div>

              <div className="intelligence-eyebrow">
                DOCUMENT INTELLIGENCE
              </div>

              <h3>
                {selectedDocumentName}
              </h3>

            </div>

            <div className="intelligence-mark">
              AI
            </div>

          </div>


          <div className="intelligence-divider" />


          {/* TITLE */}

          {selectedAnalysis.title && (

            <div className="intelligence-block">

              <div className="intelligence-label">
                TITLE
              </div>

              <div className="intelligence-title">
                {selectedAnalysis.title}
              </div>

            </div>

          )}


          {/* SUMMARY */}

          {selectedAnalysis.summary && (

            <div className="intelligence-block">

              <div className="intelligence-label">
                SUMMARY
              </div>

              <p className="intelligence-summary">
                {selectedAnalysis.summary}
              </p>

            </div>

          )}


          {/* TOPICS */}

          {selectedAnalysis.topics &&
            selectedAnalysis.topics.length >
              0 && (

              <div className="intelligence-block">

                <div className="intelligence-label">
                  TOPICS
                </div>

                <ol className="intelligence-list">

                  {selectedAnalysis.topics.map(
                    (
                      topic,
                      index
                    ) => (

                      <li
                        key={index}
                      >
                        {topic}
                      </li>

                    )
                  )}

                </ol>

              </div>

          )}


          {/* KEY CONCEPTS */}

          {selectedAnalysis.key_concepts &&
            selectedAnalysis.key_concepts.length >
              0 && (

              <div className="intelligence-block">

                <div className="intelligence-label">
                  KEY CONCEPTS
                </div>

                <div className="concept-list">

                  {selectedAnalysis.key_concepts.map(
                    (
                      concept,
                      index
                    ) => (

                      <span
                        key={index}
                        className="concept-tag"
                      >
                        {concept}
                      </span>

                    )
                  )}

                </div>

              </div>

          )}


          {/* IMPORTANT TERMS */}

          {selectedAnalysis.important_terms &&
            selectedAnalysis.important_terms.length >
              0 && (

              <div className="intelligence-block">

                <div className="intelligence-label">
                  IMPORTANT TERMS
                </div>

                <ul className="intelligence-list">

                  {selectedAnalysis.important_terms.map(
                    (
                      term,
                      index
                    ) => (

                      <li
                        key={index}
                      >
                        {term}
                      </li>

                    )
                  )}

                </ul>

              </div>

          )}


          {/* DISCUSSION QUESTIONS */}

          {selectedAnalysis.discussion_questions &&
            selectedAnalysis.discussion_questions.length >
              0 && (

              <div className="intelligence-block">

                <div className="intelligence-label">
                  DISCUSSION QUESTIONS
                </div>

                <ol className="intelligence-list">

                  {selectedAnalysis.discussion_questions.map(
                    (
                      question,
                      index
                    ) => (

                      <li
                        key={index}
                      >
                        {question}
                      </li>

                    )
                  )}

                </ol>

              </div>

          )}


          {/* METADATA */}

          <div className="intelligence-metadata">

            {selectedAnalysis.page_count !==
              undefined && (
              <>
                {selectedAnalysis.page_count}
                {" pages"}
              </>
            )}

            {selectedAnalysis.page_count !==
              undefined &&
              selectedAnalysis.chunk_count !==
                undefined &&
              " · "}

            {selectedAnalysis.chunk_count !==
              undefined && (
              <>
                {selectedAnalysis.chunk_count}
                {" chunks"}
              </>
            )}

          </div>

        </div>

      )}

    </div>
  );
}