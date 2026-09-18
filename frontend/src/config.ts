const getApiUrl = (): string => {
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl && envUrl.trim() !== "") {
    return envUrl.trim().replace(/\/+$/, "");
  }

  if (typeof window !== "undefined") {
    const hostname = window.location.hostname;

    if (hostname.includes("onrender.com")) {
      const protocol = window.location.protocol;
      // Auto replace 'frontend' with 'backend' in render domain if VITE_API_URL is missing
      const backendHostname = hostname.includes("frontend")
        ? hostname.replace("frontend", "backend")
        : hostname;
      return `${protocol}//${backendHostname}`;
    }
  }

  return "http://127.0.0.1:8000";
};

export const API_URL = getApiUrl();
