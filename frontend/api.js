// Shared API helper for OrgMind AI frontend.
//
// Token storage note: the JWT is stored in sessionStorage. This is a
// development-grade choice: it is cleared when the tab closes and is not
// shared across tabs, but it is still readable by any JavaScript running on
// this origin (i.e. vulnerable to XSS). Do not treat this as production
// grade secret storage. No API keys (Anthropic or otherwise) are ever
// stored or referenced here; only the user own JWT issued by the backend.

const API_BASE = "http://127.0.0.1:8000";
const TOKEN_KEY = "orgmind_token";

function getToken() {
    return sessionStorage.getItem(TOKEN_KEY);
}

function setToken(token) {
    sessionStorage.setItem(TOKEN_KEY, token);
}

function clearToken() {
    sessionStorage.removeItem(TOKEN_KEY);
    sessionStorage.removeItem("orgmind_user");
}

function getStoredUser() {
    const raw = sessionStorage.getItem("orgmind_user");
    return raw ? JSON.parse(raw) : null;
}

function setStoredUser(user) {
    sessionStorage.setItem("orgmind_user", JSON.stringify(user));
}

function logout() {
    clearToken();
    window.location.href = "login.html";
}

function requireAuthOrRedirect() {
    if (!getToken()) {
        window.location.href = "login.html";
        return false;
    }
    return true;
}

/**
 * Authenticated fetch wrapper.
 * Automatically attaches the bearer token, handles 401 by redirecting to
 * login, and surfaces a normalized error for other failures.
 */
async function apiFetch(path, options = {}) {
    const token = getToken();

    const headers = Object.assign(
        { "Content-Type": "application/json" },
        options.headers || {}
    );

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    let response;

    try {
        response = await fetch(`${API_BASE}${path}`, {
            ...options,
            headers
        });
    } catch (networkError) {
        throw new ApiError(
            0,
            "Could not reach the backend. Please check that the server is running."
        );
    }

    if (response.status === 401) {
        clearToken();
        window.location.href = "login.html";
        throw new ApiError(401, "Session expired. Please log in again.");
    }

    if (!response.ok) {
        let detail = `Request failed (${response.status})`;
        try {
            const body = await response.json();
            if (body && body.detail) {
                detail = typeof body.detail === "string"
                    ? body.detail
                    : JSON.stringify(body.detail);
            }
        } catch (_) {
            // Response had no JSON body; keep the default message.
        }
        throw new ApiError(response.status, detail);
    }

    if (response.status === 204) {
        return null;
    }

    return response.json();
}

class ApiError extends Error {
    constructor(status, message) {
        super(message);
        this.status = status;
    }
}