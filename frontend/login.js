const loginForm = document.getElementById("loginForm");
const loginBtn = document.getElementById("loginBtn");
const loginBtnText = document.getElementById("loginBtnText");
const loginError = document.getElementById("loginError");

// If already logged in, skip straight to the right dashboard.
(function redirectIfAuthenticated() {
    const token = getToken();
    const user = getStoredUser();
    if (token && user) {
        window.location.href = user.role === "manager" ? "manager.html" : "employee.html";
    }
})();

function setLoading(isLoading) {
    loginBtn.disabled = isLoading;
    loginBtnText.innerHTML = isLoading
        ? `<span class="spinner"></span>Signing in...`
        : "Sign In";
}

function showError(message) {
    loginError.textContent = message;
    loginError.hidden = false;
}

function hideError() {
    loginError.hidden = true;
}

loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    hideError();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    if (!username || !password) {
        showError("Please enter both username and password.");
        return;
    }

    setLoading(true);

    try {
        const tokenResponse = await apiFetch("/api/auth/login", {
            method: "POST",
            body: JSON.stringify({ username, password })
        });

        setToken(tokenResponse.access_token);

        const me = await apiFetch("/api/auth/me", { method: "GET" });
        setStoredUser(me);

        window.location.href = me.role === "manager" ? "manager.html" : "employee.html";

    } catch (error) {
        clearToken();
        if (error.status === 401) {
            showError("Invalid username or password.");
        } else if (error.status === 403) {
            showError("This account is disabled. Contact your administrator.");
        } else {
            showError(error.message || "Login failed. Please try again.");
        }
    } finally {
        setLoading(false);
    }
});