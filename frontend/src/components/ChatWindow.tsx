import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  askQuestion,
  getConversation,
} from "../services/api";

interface Message {
  id?: string;
  role: "user" | "assistant";
  content: string;
  created_at?: string;
}

interface Source {
  source_number: number;
  document_id: string;
  page_number: number;
  chunk_index: number;
  citation: string;
}

interface ChatWindowProps {
  conversationId: string;
}

function ChatWindow({
  conversationId,
}: ChatWindowProps) {
  const navigate = useNavigate();

  const [messages, setMessages] = useState<
    Message[]
  >([]);

  const [question, setQuestion] = useState("");

  const [sources, setSources] = useState<
    Source[]
  >([]);

  const [loading, setLoading] = useState(false);

  const [conversationTitle, setConversationTitle] =
    useState("New Conversation");

  useEffect(() => {
    loadConversation();
  }, [conversationId]);

  const loadConversation = async () => {
    try {
      const data = await getConversation(
        conversationId
      );

      if (data.success) {
        setMessages(data.messages || []);

        setConversationTitle(
          data.title || "New Conversation"
        );
      }
    } catch (error) {
      console.error(
        "Failed to load conversation:",
        error
      );
    }
  };

  const sendMessage = async () => {
    const userQuestion = question.trim();

    if (!userQuestion || loading) {
      return;
    }

    setQuestion("");

    const userMessage: Message = {
      role: "user",
      content: userQuestion,
    };

    setMessages((previous) => [
      ...previous,
      userMessage,
    ]);

    setLoading(true);
    setSources([]);

    try {
      const data = await askQuestion(
        userQuestion,
        conversationId
      );

      if (data.success) {
        const assistantMessage: Message = {
          role: "assistant",
          content: data.answer,
        };

        setMessages((previous) => [
          ...previous,
          assistantMessage,
        ]);

        setSources(data.sources || []);
      } else {
        throw new Error(
          data.message || "Failed to get answer"
        );
      }
    } catch (error) {
      console.error(error);

      const errorMessage: Message = {
        role: "assistant",
        content:
          error instanceof Error
            ? error.message
            : "Sorry, I could not process your question.",
      };

      setMessages((previous) => [
        ...previous,
        errorMessage,
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (
    event: React.KeyboardEvent<HTMLTextAreaElement>
  ) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat-page">

      {/* Header */}

      <header className="chat-header">

        <button
          className="back-button"
          onClick={() => navigate("/dashboard")}
        >
          ← Dashboard
        </button>

        <div>
          <h1>
            Enterprise RAG Assistant
          </h1>

          <p>{conversationTitle}</p>
        </div>

      </header>

      {/* Chat Area */}

      <main className="chat-container">

        <div className="messages-container">

          {messages.length === 0 && (
            <div className="empty-chat">
              <h2>
                How can I help you?
              </h2>

              <p>
                Ask a question about your
                uploaded enterprise documents.
              </p>
            </div>
          )}

          {messages.map(
            (message, index) => (
              <div
                key={
                  message.id || index
                }
                className={`message-row ${
                  message.role
                }`}
              >
                <div
                  className={`message-bubble ${
                    message.role
                  }`}
                >
                  <div className="message-role">
                    {message.role === "user"
                      ? "You"
                      : "AI Assistant"}
                  </div>

                  <div className="message-content">
                    {message.content}
                  </div>
                </div>
              </div>
            )
          )}

          {loading && (
            <div className="message-row assistant">
              <div className="message-bubble assistant">
                <div className="message-role">
                  AI Assistant
                </div>

                <div className="message-content">
                  Thinking...
                </div>
              </div>
            </div>
          )}

          {/* Sources */}

          {sources.length > 0 && (
            <div className="sources-box">
              <h3>
                Sources
              </h3>

              {sources.map(
                (source) => (
                  <div
                    key={
                      source.source_number
                    }
                    className="source-item"
                  >
                    <strong>
                      Source{" "}
                      {source.source_number}
                    </strong>

                    <span>
                      {source.citation}
                    </span>
                  </div>
                )
              )}
            </div>
          )}

        </div>

        {/* Input */}

        <div className="chat-input-area">

          <textarea
            value={question}
            onChange={(event) =>
              setQuestion(
                event.target.value
              )
            }
            onKeyDown={handleKeyDown}
            placeholder="Ask something about your documents..."
            rows={3}
            disabled={loading}
          />

          <button
            className="send-button"
            onClick={sendMessage}
            disabled={
              loading ||
              !question.trim()
            }
          >
            {loading
              ? "Thinking..."
              : "Send"}
          </button>

        </div>

        <p className="input-hint">
          Press Enter to send • Shift + Enter
          for a new line
        </p>

      </main>
    </div>
  );
}

export default ChatWindow;