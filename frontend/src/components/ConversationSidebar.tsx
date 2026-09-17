import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const API_URL = "http://127.0.0.1:8000";

interface Conversation {
  id: string;
  title: string;
  created_at: string;
}

interface ConversationSidebarProps {
  currentConversationId?: string;
}

export default function ConversationSidebar({
  currentConversationId,
}: ConversationSidebarProps) {
  const navigate = useNavigate();

  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);

  const token = localStorage.getItem("access_token");

  // =====================================================
  // LOAD ALL CONVERSATIONS
  // =====================================================

  const loadConversations = async () => {
    if (!token) {
      navigate("/login");
      return;
    }

    try {
      const response = await fetch(
        `${API_URL}/api/conversations`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.status === 401) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("user");
        navigate("/login");
        return;
      }

      const data = await response.json();

      if (data.success) {
        setConversations(data.conversations);
      }
    } catch (error) {
      console.error(
        "Failed to load conversations:",
        error
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadConversations();
  }, []);

  // =====================================================
  // CREATE NEW CONVERSATION
  // =====================================================

  const createNewConversation = async () => {
    if (!token) {
      navigate("/login");
      return;
    }

    try {
      const response = await fetch(
        `${API_URL}/api/conversations`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.status === 401) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("user");
        navigate("/login");
        return;
      }

      const data = await response.json();

      if (data.success) {
        navigate(`/chat/${data.conversation_id}`);
      }
    } catch (error) {
      console.error(
        "Failed to create conversation:",
        error
      );
    }
  };

  // =====================================================
  // LOGOUT
  // =====================================================

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");

    navigate("/login");
  };

  // =====================================================
  // UI
  // =====================================================

  return (
    <aside
      style={{
        width: "260px",
        height: "100vh",
        background: "#111827",
        borderRight: "1px solid #374151",
        display: "flex",
        flexDirection: "column",
        padding: "16px",
        boxSizing: "border-box",
      }}
    >
      {/* Logo / Title */}

      <h2
        style={{
          fontSize: "18px",
          marginBottom: "20px",
          color: "white",
        }}
      >
        Enterprise RAG
      </h2>

      {/* New Chat */}

      <button
        onClick={createNewConversation}
        style={{
          padding: "12px",
          borderRadius: "8px",
          border: "none",
          background: "#2563eb",
          color: "white",
          cursor: "pointer",
          marginBottom: "20px",
          fontSize: "14px",
        }}
      >
        + New Chat
      </button>

      {/* Conversations */}

      <div
        style={{
          flex: 1,
          overflowY: "auto",
        }}
      >
        <p
          style={{
            color: "#9ca3af",
            fontSize: "13px",
            marginBottom: "10px",
          }}
        >
          Conversations
        </p>

        {loading && (
          <p
            style={{
              color: "#6b7280",
              fontSize: "13px",
            }}
          >
            Loading...
          </p>
        )}

        {!loading &&
          conversations.length === 0 && (
            <p
              style={{
                color: "#6b7280",
                fontSize: "13px",
              }}
            >
              No conversations yet
            </p>
          )}

        {conversations.map((conversation) => (
          <button
            key={conversation.id}
            onClick={() =>
              navigate(
                `/chat/${conversation.id}`
              )
            }
            style={{
              width: "100%",
              textAlign: "left",
              padding: "10px",
              marginBottom: "6px",
              borderRadius: "6px",
              border: "none",
              background:
                currentConversationId ===
                conversation.id
                  ? "#374151"
                  : "transparent",
              color: "white",
              cursor: "pointer",
              fontSize: "13px",
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}
          >
            {conversation.title ||
              "New Conversation"}
          </button>
        ))}
      </div>

      {/* Dashboard */}

      <button
        onClick={() =>
          navigate("/dashboard")
        }
        style={{
          padding: "10px",
          marginBottom: "8px",
          borderRadius: "6px",
          border: "1px solid #374151",
          background: "transparent",
          color: "white",
          cursor: "pointer",
        }}
      >
        ← Dashboard
      </button>

      {/* Logout */}

      <button
        onClick={logout}
        style={{
          padding: "10px",
          borderRadius: "6px",
          border: "1px solid #374151",
          background: "transparent",
          color: "#f87171",
          cursor: "pointer",
        }}
      >
        Logout
      </button>
    </aside>
  );
}