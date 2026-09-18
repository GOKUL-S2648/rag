import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import "../App.css";

import { API_URL } from "../config";


interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at?: string;
}

interface ConversationData {
  success: boolean;
  conversation?: {
    id: string;
    title?: string;
    created_at?: string;
  };
  messages?: Message[];
  message?: string;
}

export default function Chat() {
  const navigate = useNavigate();

  const { conversationId } = useParams<{
    conversationId: string;
  }>();

  const [messages, setMessages] =
    useState<Message[]>([]);

  const [question, setQuestion] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [loadingConversation, setLoadingConversation] =
    useState(true);

  const [error, setError] =
    useState("");

  const messagesEndRef =
    useRef<HTMLDivElement | null>(null);


  const token =
    localStorage.getItem(
      "access_token"
    );


  /* ==========================================================
     AUTH CHECK
     ========================================================== */

  useEffect(() => {
    if (!token) {
      navigate("/login");
    }
  }, [token, navigate]);


  /* ==========================================================
     LOAD CONVERSATION
     ========================================================== */

  useEffect(() => {

    if (!conversationId || !token) {
      return;
    }

    loadConversation();

  }, [conversationId, token]);


  const loadConversation = async () => {

    setLoadingConversation(true);
    setError("");

    try {

      const response =
        await fetch(
          `${API_URL}/api/conversations/${conversationId}`,
          {
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


      const data: ConversationData =
        await response.json();


      if (!response.ok) {

        throw new Error(
          data.message ||
          "Unable to load conversation."
        );
      }


      setMessages(
        data.messages || []
      );

    } catch (error) {

      console.error(error);

      setError(
        error instanceof Error
          ? error.message
          : "Unable to load conversation."
      );

    } finally {

      setLoadingConversation(false);

    }
  };


  /* ==========================================================
     SCROLL TO BOTTOM
     ========================================================== */

  useEffect(() => {

    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });

  }, [messages]);


  /* ==========================================================
     SEND QUESTION
     ========================================================== */

  const sendQuestion = async () => {

    const trimmedQuestion =
      question.trim();


    if (!trimmedQuestion) {
      return;
    }


    if (!conversationId) {

      setError(
        "Conversation not found."
      );

      return;
    }


    if (!token) {

      navigate("/login");

      return;
    }


    if (loading) {
      return;
    }


    setError("");
    setLoading(true);


    const temporaryUserMessage: Message = {
      id:
        `temp-${Date.now()}`,

      role: "user",

      content:
        trimmedQuestion,
    };


    setMessages(
      previous => [
        ...previous,
        temporaryUserMessage,
      ]
    );


    setQuestion("");


    try {

      const response =
        await fetch(
          `${API_URL}/api/ask`,
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json",

              Authorization:
                `Bearer ${token}`,
            },

            body: JSON.stringify({
              question:
                trimmedQuestion,

              conversation_id:
                conversationId,

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

        throw new Error(
          data.detail ||
          data.message ||
          "Failed to get AI response."
        );
      }


      if (!data.success) {

        throw new Error(
          data.message ||
          "The AI could not answer the question."
        );
      }


      const assistantMessage: Message = {
        id:
          `assistant-${Date.now()}`,

        role: "assistant",

        content:
          data.answer ||
          "I could not generate an answer.",
      };


      setMessages(
        previous => [
          ...previous.filter(
            message =>
              message.id !==
              temporaryUserMessage.id
          ),

          {
            ...temporaryUserMessage,
            id:
              `user-${Date.now()}`,
          },

          assistantMessage,
        ]
      );

    } catch (error) {

      console.error(error);


      setMessages(
        previous =>
          previous.filter(
            message =>
              message.id !==
              temporaryUserMessage.id
          )
      );


      setError(
        error instanceof Error
          ? error.message
          : "Unable to get AI response."
      );

    } finally {

      setLoading(false);

    }
  };


  /* ==========================================================
     ENTER KEY
     ========================================================== */

  const handleKeyDown = (
    event: React.KeyboardEvent<HTMLTextAreaElement>
  ) => {

    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {

      event.preventDefault();

      sendQuestion();
    }
  };


  /* ==========================================================
     NEW CHAT
     ========================================================== */

  const createNewChat = async () => {

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

      }

    } catch (error) {

      console.error(error);

      setError(
        "Unable to create a new conversation."
      );
    }
  };


  /* ==========================================================
     BACK TO DASHBOARD
     ========================================================== */

  const goDashboard = () => {
    navigate("/dashboard");
  };


  /* ==========================================================
     RENDER
     ========================================================== */

  return (

    <div className="chat-page">

      {/* Background decorative elements */}

      <div className="chat-bg-circle chat-bg-circle-one" />

      <div className="chat-bg-circle chat-bg-circle-two" />


      {/* ======================================================
          HEADER
          ====================================================== */}

      <header className="chat-header">

        <div className="chat-brand">

          <div className="chat-brand-mark">
            R
          </div>

          <div>

            <div className="chat-brand-name">
              Enterprise RAG
            </div>

            <div className="chat-brand-subtitle">
              Intelligent Knowledge Assistant
            </div>

          </div>

        </div>


        <div className="chat-header-actions">

          <button
            className="chat-header-button"
            onClick={goDashboard}
          >
            ← Dashboard
          </button>


          <button
            className="chat-new-button"
            onClick={createNewChat}
          >
            + New conversation
          </button>

        </div>

      </header>


      {/* ======================================================
          MAIN
          ====================================================== */}

      <main className="chat-main">


        {/* ====================================================
            TOP INTRO
            ==================================================== */}

        <section className="chat-intro">

          <div className="chat-eyebrow">
            AI KNOWLEDGE ASSISTANT
          </div>


          <h1>
            Ask your knowledge.
          </h1>


          <p>
            Get answers grounded in your
            enterprise documents.
          </p>

        </section>


        {/* ====================================================
            ERROR
            ==================================================== */}

        {error && (

          <div className="chat-error">

            <span>!</span>

            {error}

            <button
              onClick={() =>
                setError("")
              }
            >
              ×
            </button>

          </div>

        )}


        {/* ====================================================
            CHAT AREA
            ==================================================== */}

        <section className="chat-workspace">


          {/* ==================================================
              MESSAGES
              ================================================== */}

          <div className="chat-messages">

            {loadingConversation ? (

              <div className="chat-loading">

                <div className="chat-loading-mark">
                  R
                </div>

                <p>
                  Loading conversation...
                </p>

              </div>

            ) : messages.length === 0 ? (

              <div className="chat-empty">

                <div className="chat-empty-number">
                  01
                </div>

                <h2>
                  How can I help you?
                </h2>

                <p>
                  Ask a question about your
                  uploaded enterprise documents.
                </p>


                <div className="chat-suggestions">

                  <button
                    onClick={() =>
                      setQuestion(
                        "What are the main topics in my documents?"
                      )
                    }
                  >
                    Main topics →
                  </button>


                  <button
                    onClick={() =>
                      setQuestion(
                        "Summarize the important information in my documents."
                      )
                    }
                  >
                    Summarize documents →
                  </button>


                  <button
                    onClick={() =>
                      setQuestion(
                        "What important concepts should I know?"
                      )
                    }
                  >
                    Key concepts →
                  </button>

                </div>

              </div>

            ) : (

              <div className="message-list">

                {messages.map(
                  (
                    message,
                    index
                  ) => (

                    <article
                      key={
                        message.id ||
                        index
                      }
                      className={
                        message.role ===
                        "user"
                          ? "message-row user-message"
                          : "message-row assistant-message"
                      }
                    >

                      <div className="message-label">

                        {message.role ===
                        "user"
                          ? "YOU"
                          : "RAG ASSISTANT"}

                      </div>


                      <div className="message-content">

                        {message.content}

                      </div>


                      {message.role ===
                        "assistant" && (

                        <div className="message-source-note">

                          Answer generated from
                          your accessible
                          enterprise knowledge.

                        </div>

                      )}

                    </article>

                  )
                )}


                {loading && (

                  <article className="message-row assistant-message">

                    <div className="message-label">
                      RAG ASSISTANT
                    </div>

                    <div className="typing-indicator">

                      <span />
                      <span />
                      <span />

                      <em>
                        Thinking...
                      </em>

                    </div>

                  </article>

                )}

                <div
                  ref={messagesEndRef}
                />

              </div>

            )}

          </div>


          {/* ==================================================
              INPUT AREA
              ================================================== */}

          <div className="chat-input-area">

            <div className="chat-input-top">

              <span>
                ASK YOUR KNOWLEDGE BASE
              </span>

              <span>
                SHIFT + ENTER FOR NEW LINE
              </span>

            </div>


            <div className="chat-input-wrapper">

              <textarea
                value={question}
                onChange={(event) =>
                  setQuestion(
                    event.target.value
                  )
                }
                onKeyDown={
                  handleKeyDown
                }
                placeholder="Ask something about your documents..."
                rows={1}
                disabled={
                  loading ||
                  loadingConversation
                }
              />


              <button
                onClick={
                  sendQuestion
                }
                disabled={
                  loading ||
                  loadingConversation ||
                  !question.trim()
                }
              >

                {loading
                  ? "Thinking..."
                  : "Send →"}

              </button>

            </div>


            <div className="chat-input-footer">

              <span>
                AI · RAG · VECTOR SEARCH
              </span>

              <span>
                Answers are grounded in accessible documents
              </span>

            </div>

          </div>

        </section>

      </main>


      {/* ======================================================
          FOOTER
          ====================================================== */}

      <footer className="chat-footer">

        <span>
          ENTERPRISE RAG ASSISTANT
        </span>

        <span>
          SECURE KNOWLEDGE ACCESS
        </span>

      </footer>

    </div>
  );
}