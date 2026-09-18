import { useState } from "react";

import { API_URL } from "../config";

interface DocumentUploadProps {
  onUploadSuccess?: () => void;
}

export default function DocumentUpload({
  onUploadSuccess,
}: DocumentUploadProps) {
  const [file, setFile] =
    useState<File | null>(null);

  const [uploading, setUploading] =
    useState(false);

  const [message, setMessage] =
    useState("");

  const [error, setError] =
    useState(false);

  const handleUpload = async () => {
    if (!file) {
      setMessage(
        "Please select a file."
      );
      setError(true);
      return;
    }

    const token =
      localStorage.getItem(
        "access_token"
      );

    if (!token) {
      setMessage(
        "Please login first."
      );
      setError(true);
      return;
    }

    const formData =
      new FormData();

    formData.append(
      "file",
      file
    );

    setUploading(true);
    setMessage("");
    setError(false);

    try {
      const response =
        await fetch(
          `${API_URL}/api/documents/upload`,
          {
            method: "POST",

            headers: {
              Authorization:
                `Bearer ${token}`,
            },

            body: formData,
          }
        );

      const data =
        await response.json();

      if (!response.ok) {
        setMessage(
          data.detail ||
          "Upload failed."
        );

        setError(true);
        return;
      }

      setMessage(
        `Uploaded successfully: ${data.document.filename}`
      );

      setError(false);

      setFile(null);

      onUploadSuccess?.();

    } catch (error) {
      console.error(error);

      setMessage(
        "Cannot connect to the backend."
      );

      setError(true);

    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="upload-editorial">

      <div className="upload-header">

        <div>
          <div className="upload-eyebrow">
            KNOWLEDGE LIBRARY
          </div>

          <h2>
            Upload Document
          </h2>

          <p>
            Add a new source to your
            enterprise knowledge base.
          </p>
        </div>

        <div className="upload-number">
          01
        </div>

      </div>


      <div className="upload-divider" />


      <div className="upload-body">

        <div className="upload-file-area">

          <label
            htmlFor="document-file"
            className="upload-file-label"
          >
            <span className="upload-file-icon">
              +
            </span>

            <span>
              {file
                ? file.name
                : "Choose a document"}
            </span>
          </label>

          <input
            id="document-file"
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={(e) => {

              setFile(
                e.target.files?.[0] ||
                null
              );

              setMessage("");
              setError(false);

            }}
            className="upload-file-input"
          />

          <div className="upload-file-help">
            PDF · DOCX · TXT
          </div>

        </div>


        <button
          onClick={handleUpload}
          disabled={uploading}
          className="upload-action"
        >
          {uploading
            ? "Processing..."
            : "Upload Document →"}
        </button>

      </div>


      {message && (
        <div
          className={
            error
              ? "upload-message upload-message-error"
              : "upload-message upload-message-success"
          }
        >
          <span>
            {error ? "!" : "✓"}
          </span>

          {message}
        </div>
      )}

    </div>
  );
}