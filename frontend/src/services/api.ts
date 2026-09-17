const API_URL = "http://127.0.0.1:8000";

export const getToken = () => {
  return localStorage.getItem("access_token");
};

export const apiRequest = async (
  endpoint: string,
  options: RequestInit = {}
) => {
  const token = getToken();

  const headers: HeadersInit = {
    ...(options.body ? { "Content-Type": "application/json" } : {}),
    ...(token
      ? {
          Authorization: `Bearer ${token}`,
        }
      : {}),
    ...(options.headers || {}),
  };

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail || data.message || "Request failed"
    );
  }

  return data;
};

export const createConversation = async () => {
  return apiRequest("/api/conversations", {
    method: "POST",
  });
};

export const getConversation = async (
  conversationId: string
) => {
  return apiRequest(
    `/api/conversations/${conversationId}`
  );
};

export const askQuestion = async (
  question: string,
  conversationId: string
) => {
  return apiRequest("/api/ask", {
    method: "POST",
    body: JSON.stringify({
      question,
      conversation_id: conversationId,
      limit: 5,
    }),
  });
};
export const analyzeDocument = async (
  documentId: string
) => {
  return apiRequest(
    `/api/documents/${documentId}/analyze`,
    {
      method: "POST",
    }
  );
};


export const getDocumentAnalysis = async (
  documentId: string
) => {
  return apiRequest(
    `/api/documents/${documentId}/analysis`
  );
};
// ============================================================
// DOCUMENT COMPARISON
// ============================================================

export const compareDocuments = async (
  documentAId: string,
  documentBId: string
) => {
  return apiRequest("/api/comparison", {
    method: "POST",
    body: JSON.stringify({
      document_a_id: documentAId,
      document_b_id: documentBId,
    }),
  });
};