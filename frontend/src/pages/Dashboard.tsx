import { useState } from "react";
import { useNavigate } from "react-router-dom";

import "../App.css";

import DocumentUpload from "../components/DocumentUpload";
import MyDocuments from "../components/MyDocuments";
import DocumentComparison from "../components/DocumentComparison";


import { API_URL } from "../config";



interface SearchResult {
  chunk_id: string;
  document_id: string;
  document_name: string;
  content: string;
  page_number: number | null;
  chunk_index: number;
}


export default function Dashboard() {

  const navigate = useNavigate();


  const [
    documentsRefreshKey,
    setDocumentsRefreshKey
  ] = useState(0);


  const [
    searchQuery,
    setSearchQuery
  ] = useState("");


  const [
    searchResults,
    setSearchResults
  ] = useState<SearchResult[]>([]);


  const [
    searchLoading,
    setSearchLoading
  ] = useState(false);


  const [
    searchError,
    setSearchError
  ] = useState("");


  const [
    showSearch,
    setShowSearch
  ] = useState(false);


  const token =
    localStorage.getItem("access_token");




  // =====================================================
  // CREATE CONVERSATION
  // =====================================================

  const startNewConversation = async () => {

    if (!token) {

      navigate("/login");

      return;

    }


    try {

      const response =
        await fetch(
          `${API_URL}/api/conversations`,
          {
            method: "POST",

            headers: {
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

        navigate("/login");

        return;

      }


      const data =
        await response.json();


      if (data.success) {

        navigate(
          `/chat/${data.conversation_id}`
        );

      } else {

        alert(
          data.message ||
          "Failed to create conversation"
        );

      }

    } catch (error) {

      console.error(error);

      alert(
        "Cannot connect to the backend."
      );

    }

  };


  // =====================================================
  // LOGOUT
  // =====================================================

  const logout = () => {

    localStorage.removeItem(
      "access_token"
    );

    localStorage.removeItem(
      "user"
    );

    navigate("/login");

  };


  // =====================================================
  // SEARCH
  // =====================================================

  const performSearch = async () => {

    const query =
      searchQuery.trim();


    if (!query) {

      setSearchError(
        "Please enter something to search."
      );

      return;

    }


    if (!token) {

      navigate("/login");

      return;

    }


    setSearchLoading(true);

    setSearchError("");

    setSearchResults([]);


    try {

      const response =
        await fetch(
          `${API_URL}/api/search`,
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json",

              Authorization:
                `Bearer ${token}`,
            },

            body: JSON.stringify({
              query,
              limit: 5,
            }),
          }
        );


      if (response.status === 401) {

        localStorage.removeItem(
          "access_token"
        );

        localStorage.removeItem(
          "user"
        );

        navigate("/login");

        return;

      }


      const data =
        await response.json();


      if (!response.ok) {

        setSearchError(
          data.detail ||
          "Search failed."
        );

        return;

      }


      setSearchResults(
        data.results || []
      );

    } catch (error) {

      console.error(error);

      setSearchError(
        "Unable to connect to the server."
      );

    } finally {

      setSearchLoading(false);

    }

  };


  // =====================================================
  // OPEN DOCUMENTS
  // =====================================================

  const openDocuments = () => {

    document
      .getElementById(
        "documents-section"
      )
      ?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });

  };


  // =====================================================
  // OPEN UPLOAD
  // =====================================================

  const openUpload = () => {

    document
      .getElementById(
        "upload-section"
      )
      ?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });

  };


  // =====================================================
  // OPEN SEARCH
  // =====================================================

  const openSearch = () => {

    setShowSearch(true);


    setTimeout(() => {

      document
        .getElementById(
          "semantic-search-section"
        )
        ?.scrollIntoView({
          behavior: "smooth",
          block: "center",
        });

    }, 100);

  };


  // =====================================================
  // HERO SEARCH
  // =====================================================

  const heroSearch = () => {

    setShowSearch(true);


    setTimeout(() => {

      performSearch();

    }, 100);

  };


  // =====================================================
  // UI
  // =====================================================

  return (

    <div className="dashboard">

      <div className="dashboard-container">


        {/* ================================================= */}
        {/* NAVIGATION */}
        {/* ================================================= */}

        <header className="dashboard-header">

          <div className="brand-area">

            <h1>
              Enterprise RAG
            </h1>

            <p>
              Intelligent Knowledge Assistant
            </p>

          </div>


          <button
            className="logout-button"
            onClick={logout}
          >
            Logout
          </button>

        </header>


        {/* ================================================= */}
        {/* HERO */}
        {/* ================================================= */}

        <section className="hero-card">

          <div
            style={{
              position: "relative",
              zIndex: 2,
            }}
          >

            <div
              style={{
                marginBottom: "18px",
                color: "#77736b",
                fontSize: "11px",
                letterSpacing: "2px",
                textTransform: "uppercase",
              }}
            >
              AI Knowledge Platform
            </div>


            <h2>
              Your knowledge.
              <br />
              Understood.
            </h2>


            <p>
              Search, explore and interact
              with your enterprise documents
              through intelligent retrieval and
              source-backed AI answers.
            </p>


            {/* HERO SEARCH */}

            <div
              style={{
                display: "flex",
                gap: "0",
                maxWidth: "700px",
                marginTop: "30px",
              }}
            >

              <input
                className="search-input"
                value={searchQuery}
                onChange={(event) =>
                  setSearchQuery(
                    event.target.value
                  )
                }
                onKeyDown={(event) => {

                  if (
                    event.key ===
                    "Enter"
                  ) {

                    heroSearch();

                  }

                }}
                placeholder="Ask your enterprise knowledge..."
              />


              <button
                className="primary-button"
                onClick={heroSearch}
              >
                Search →
              </button>

            </div>


            {/* QUICK ACTIONS */}

            <div
              style={{
                display: "flex",
                gap: "22px",
                marginTop: "20px",
                flexWrap: "wrap",
              }}
            >

              <button
                onClick={
                  startNewConversation
                }
                style={{
                  border: "none",
                  background:
                    "transparent",
                  padding: 0,
                  color: "#55524c",
                  cursor:
                    "pointer",
                  fontSize:
                    "12px",
                }}
              >
                Ask AI →
              </button>


              <button
                onClick={openUpload}
                style={{
                  border: "none",
                  background:
                    "transparent",
                  padding: 0,
                  color: "#55524c",
                  cursor:
                    "pointer",
                  fontSize:
                    "12px",
                }}
              >
                Upload document →
              </button>


              <button
                onClick={openSearch}
                style={{
                  border: "none",
                  background:
                    "transparent",
                  padding: 0,
                  color: "#55524c",
                  cursor:
                    "pointer",
                  fontSize:
                    "12px",
                }}
              >
                Explore knowledge →
              </button>

            </div>

          </div>

        </section>


        {/* ================================================= */}
        {/* DOCUMENT UPLOAD */}
        {/* ================================================= */}

        <section
          id="upload-section"
          className="dashboard-section"
        >

          <DocumentUpload
            onUploadSuccess={() =>
              setDocumentsRefreshKey(
                previous =>
                  previous + 1
              )
            }
          />

        </section>


        {/* ================================================= */}
        {/* DOCUMENTS */}
        {/* ================================================= */}

        <section
          id="documents-section"
          className="dashboard-section"
        >

          <MyDocuments
            refreshKey={
              documentsRefreshKey
            }
          />

        </section>


        {/* ================================================= */}
        {/* SEARCH */}
        {/* ================================================= */}

        {showSearch && (

          <section
            id="semantic-search-section"
            className="dashboard-section search-panel"
          >

            <div className="section-card">

              <div
                style={{
                  display: "flex",
                  justifyContent:
                    "space-between",
                  alignItems:
                    "flex-start",
                  gap: "20px",
                }}
              >

                <div>

                  <h2 className="section-title">
                    Search knowledge.
                  </h2>

                  <p className="section-description">
                    Find relevant information
                    across your accessible
                    enterprise documents.
                  </p>

                </div>


                <button
                  onClick={() => {

                    setShowSearch(
                      false
                    );

                    setSearchResults(
                      []
                    );

                    setSearchError(
                      ""
                    );

                  }}
                  style={{
                    border:
                      "1px solid #aaa59b",
                    background:
                      "transparent",
                    padding:
                      "8px 13px",
                    cursor:
                      "pointer",
                    color:
                      "#55524c",
                  }}
                >
                  Close
                </button>

              </div>


              <div className="search-form">

                <input
                  className="search-input"
                  value={
                    searchQuery
                  }
                  onChange={event =>
                    setSearchQuery(
                      event.target.value
                    )
                  }
                  onKeyDown={event => {

                    if (
                      event.key ===
                      "Enter"
                    ) {

                      performSearch();

                    }

                  }}
                  placeholder="Search documents..."
                />


                <button
                  className="search-button"
                  onClick={
                    performSearch
                  }
                  disabled={
                    searchLoading
                  }
                >
                  {searchLoading
                    ? "Searching..."
                    : "Search"}
                </button>

              </div>


              {searchError && (

                <div className="search-error">
                  {searchError}
                </div>

              )}


              {searchLoading && (

                <div
                  style={{
                    padding:
                      "35px 0",
                    color:
                      "#77736b",
                    fontSize:
                      "13px",
                  }}
                >
                  Searching your
                  knowledge base...
                </div>

              )}


              {!searchLoading &&
                !searchError &&
                searchQuery.trim() &&
                searchResults.length ===
                  0 && (

                  <div className="search-empty">
                    No relevant information
                    found.
                  </div>

              )}


              {searchResults.length > 0 && (

                <div className="search-results">

                  <h3>
                    Relevant information
                  </h3>


                  {searchResults.map(
                    (
                      result,
                      index
                    ) => (

                      <div
                        className="search-result"
                        key={
                          result.chunk_id
                        }
                      >

                        <div className="result-source">
                          Source{" "}
                          {String(
                            index + 1
                          ).padStart(
                            2,
                            "0"
                          )}
                        </div>


                        <div className="result-document">
                          {result.document_name}
                        </div>


                        <div className="result-meta">
                          Page{" "}
                          {result.page_number ??
                            "N/A"}
                          {" · "}
                          Chunk{" "}
                          {
                            result.chunk_index
                          }
                        </div>


                        <div className="result-content">
                          {
                            result.content
                          }
                        </div>

                      </div>

                    )
                  )}

                </div>

              )}

            </div>

          </section>

        )}


        {/* ================================================= */}
        {/* COMPARISON */}
        {/* ================================================= */}

        <section
          className="dashboard-section"
        >

          <DocumentComparison />

        </section>


        {/* ================================================= */}
        {/* FEATURE NAVIGATION */}
        {/* ================================================= */}

        <section className="feature-grid">


          <button
            className="feature-card"
            onClick={
              openDocuments
            }
          >

            <div
              style={{
                fontSize: "28px",
                marginBottom:
                  "25px",
              }}
            >
              01
            </div>

            <h3>
              Documents
            </h3>

            <p>
              Manage your enterprise
              knowledge library and
              upload new sources.
            </p>

            <span className="feature-action">
              Explore documents
            </span>

          </button>


          <button
            className="feature-card"
            onClick={
              openSearch
            }
          >

            <div
              style={{
                fontSize: "28px",
                marginBottom:
                  "25px",
              }}
            >
              02
            </div>

            <h3>
              Search
            </h3>

            <p>
              Discover relevant
              information using semantic
              vector retrieval.
            </p>

            <span className="feature-action">
              Search knowledge
            </span>

          </button>


          <button
            className="feature-card"
            onClick={
              startNewConversation
            }
          >

            <div
              style={{
                fontSize: "28px",
                marginBottom:
                  "25px",
              }}
            >
              03
            </div>

            <h3>
              AI Assistant
            </h3>

            <p>
              Ask questions and receive
              answers grounded in your
              documents.
            </p>

            <span className="feature-action">
              Talk to AI
            </span>

          </button>


        </section>


        {/* ================================================= */}
        {/* FOOTER */}
        {/* ================================================= */}

        <footer
          style={{
            marginTop:
              "70px",

            padding:
              "25px 0",

            display:
              "flex",

            justifyContent:
              "space-between",

            fontSize:
              "11px",

            letterSpacing:
              "0.5px",
          }}
        >

          <span>
            ENTERPRISE RAG ASSISTANT
          </span>

          <span>
            AI · RAG · VECTOR SEARCH
          </span>

        </footer>


      </div>

    </div>
  );
}