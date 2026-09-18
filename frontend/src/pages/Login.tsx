import { useState } from "react";
import { useNavigate } from "react-router-dom";

import "../App.css";

import { API_URL } from "../config";


function Login() {
  const navigate = useNavigate();

  const [isRegister, setIsRegister] =
    useState(false);

  const [name, setName] =
    useState("");

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [confirmPassword, setConfirmPassword] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [success, setSuccess] =
    useState("");


  const switchMode = () => {
    setIsRegister(!isRegister);

    setName("");
    setEmail("");
    setPassword("");
    setConfirmPassword("");

    setError("");
    setSuccess("");
  };


  const handleSubmit = async () => {

    setError("");
    setSuccess("");


    /* ========================================================
       VALIDATION
       ======================================================== */

    if (isRegister && !name.trim()) {

      setError(
        "Please enter your name."
      );

      return;
    }


    if (!email.trim()) {

      setError(
        "Please enter your email address."
      );

      return;
    }


    if (!password) {

      setError(
        "Please enter your password."
      );

      return;
    }


    if (isRegister) {

      if (password.length < 6) {

        setError(
          "Password must contain at least 6 characters."
        );

        return;
      }


      if (
        password !==
        confirmPassword
      ) {

        setError(
          "Passwords do not match."
        );

        return;
      }

    }


    setLoading(true);


    try {

      /* ======================================================
         REGISTER
         ====================================================== */

      if (isRegister) {

        const response =
          await fetch(
            `${API_URL}/api/auth/register`,
            {
              method: "POST",

              headers: {
                "Content-Type":
                  "application/json",
              },

              body: JSON.stringify({
                name:
                  name.trim(),

                email:
                  email.trim()
                    .toLowerCase(),

                password,
              }),
            }
          );


        const data =
          await response.json();


        if (!response.ok) {

          throw new Error(
            data.detail ||
            data.message ||
            "Registration failed."
          );
        }


        /*
         * Backend returns:
         *
         * access_token
         * user
         *
         * If your backend returns token instead,
         * the fallback below also handles it.
         */

        const token =
          data.access_token ||
          data.token;


        if (!token) {

          throw new Error(
            "Account created, but authentication token was not returned."
          );
        }


        localStorage.setItem(
          "access_token",
          token
        );


        if (data.user) {

          localStorage.setItem(
            "user",
            JSON.stringify(
              data.user
            )
          );

        }


        setSuccess(
          "Account created successfully."
        );


        /*
         * Give the success message
         * a moment to appear.
         */

        setTimeout(() => {

          navigate(
            "/dashboard"
          );

        }, 500);


        return;
      }


      /* ======================================================
         LOGIN
         ====================================================== */

      const response =
        await fetch(
          `${API_URL}/api/auth/login`,
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json",
            },

            body: JSON.stringify({
              email:
                email.trim()
                  .toLowerCase(),

              password,
            }),
          }
        );


      const data =
        await response.json();


      if (!response.ok) {

        throw new Error(
          data.detail ||
          data.message ||
          "Invalid email or password."
        );
      }


      const token =
        data.access_token ||
        data.token;


      if (!token) {

        throw new Error(
          "Login succeeded, but authentication token was not returned."
        );
      }


      localStorage.setItem(
        "access_token",
        token
      );


      if (data.user) {

        localStorage.setItem(
          "user",
          JSON.stringify(
            data.user
          )
        );

      }


      navigate(
        "/dashboard"
      );

    } catch (error) {

      console.error(error);


      setError(
        error instanceof Error
          ? error.message
          : isRegister
            ? "Registration failed."
            : "Login failed."
      );

    } finally {

      setLoading(false);

    }
  };


  return (

    <div className="auth-page">

      {/* =====================================================
          BACKGROUND DECORATION
          ===================================================== */}

      <div
        className="
          auth-decoration
          auth-decoration-one
        "
      />

      <div
        className="
          auth-decoration
          auth-decoration-two
        "
      />


      {/* =====================================================
          HEADER
          ===================================================== */}

      <header className="auth-header">

        <div className="auth-brand">

          <span className="auth-brand-mark">
            R
          </span>

          <span>
            Enterprise RAG
          </span>

        </div>


        <span className="auth-header-label">
          AI KNOWLEDGE PLATFORM
        </span>

      </header>


      {/* =====================================================
          MAIN
          ===================================================== */}

      <main className="auth-main">


        {/* ===================================================
            LEFT SIDE
            =================================================== */}

        <section className="auth-intro">

          <div className="auth-eyebrow">
            INTELLIGENT KNOWLEDGE
          </div>


          <h1>

            Your knowledge.

            <br />

            Understood.

          </h1>


          <p>

            Search, explore and interact
            with your enterprise documents
            using intelligent retrieval and
            source-backed AI.

          </p>


          <div className="auth-features">

            <div>

              <span>
                01
              </span>

              Semantic document search

            </div>


            <div>

              <span>
                02
              </span>

              AI-powered answers

            </div>


            <div>

              <span>
                03
              </span>

              Enterprise knowledge access

            </div>

          </div>

        </section>


        {/* ===================================================
            AUTH CARD
            =================================================== */}

        <section className="auth-card">


          <div className="auth-card-top">

            <span>

              {isRegister
                ? "NEW ACCOUNT"
                : "WELCOME BACK"}

            </span>


            <span>
              SECURE ACCESS
            </span>

          </div>


          <h2>

            {isRegister
              ? "Create account"
              : "Sign in"}

          </h2>


          <p className="auth-subtitle">

            {isRegister
              ? "Create your enterprise knowledge account."
              : "Access your enterprise knowledge assistant."}

          </p>


          {/* =================================================
              NAME
              ================================================= */}

          {isRegister && (

            <div className="form-group">

              <label>
                Full name
              </label>


              <input
                type="text"
                placeholder="Your name"
                value={name}
                onChange={(e) =>
                  setName(
                    e.target.value
                  )
                }
                autoComplete="name"
              />

            </div>

          )}


          {/* =================================================
              EMAIL
              ================================================= */}

          <div className="form-group">

            <label>
              Email address
            </label>


            <input
              type="email"
              placeholder="you@company.com"
              value={email}
              onChange={(e) =>
                setEmail(
                  e.target.value
                )
              }
              autoComplete="email"
            />

          </div>


          {/* =================================================
              PASSWORD
              ================================================= */}

          <div className="form-group">

            <label>
              Password
            </label>


            <input
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) =>
                setPassword(
                  e.target.value
                )
              }
              onKeyDown={(e) => {

                if (
                  e.key ===
                  "Enter" &&
                  !isRegister
                ) {

                  handleSubmit();

                }

              }}
              autoComplete={
                isRegister
                  ? "new-password"
                  : "current-password"
              }
            />

          </div>


          {/* =================================================
              CONFIRM PASSWORD
              ================================================= */}

          {isRegister && (

            <div className="form-group">

              <label>
                Confirm password
              </label>


              <input
                type="password"
                placeholder="Confirm your password"
                value={
                  confirmPassword
                }
                onChange={(e) =>
                  setConfirmPassword(
                    e.target.value
                  )
                }
                onKeyDown={(e) => {

                  if (
                    e.key ===
                    "Enter"
                  ) {

                    handleSubmit();

                  }

                }}
                autoComplete="new-password"
              />

            </div>

          )}


          {/* =================================================
              ERROR
              ================================================= */}

          {error && (

            <div className="error-message">

              <span>
                !
              </span>

              {error}

            </div>

          )}


          {/* =================================================
              SUCCESS
              ================================================= */}

          {success && (

            <div className="auth-success-message">

              <span>
                ✓
              </span>

              {success}

            </div>

          )}


          {/* =================================================
              SUBMIT
              ================================================= */}

          <button
            className="auth-login-button"
            onClick={handleSubmit}
            disabled={loading}
          >

            {loading

              ? (
                isRegister
                  ? "Creating account..."
                  : "Signing in..."
              )

              : (
                isRegister
                  ? "Create Account →"
                  : "Continue →"
              )

            }

          </button>


          {/* =================================================
              SWITCH LOGIN / REGISTER
              ================================================= */}

          <div className="auth-switch">

            <span>

              {isRegister
                ? "Already have an account?"
                : "Don't have an account?"}

            </span>


            <button
              type="button"
              onClick={switchMode}
            >

              {isRegister
                ? "Sign in"
                : "Create account"}

            </button>

          </div>


          {/* =================================================
              SECURITY
              ================================================= */}

          <div className="auth-security">

            <span>
              ●
            </span>

            Protected enterprise access

          </div>

        </section>

      </main>


      {/* =====================================================
          FOOTER
          ===================================================== */}

      <footer className="auth-footer">

        <span>
          ENTERPRISE RAG ASSISTANT
        </span>


        <span>
          AI · RAG · VECTOR SEARCH
        </span>

      </footer>

    </div>
  );
}


export default Login;