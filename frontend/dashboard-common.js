// Shared helpers for rendering dashboard UI state (used by both manager
// and employee dashboards).

function escapeHTML(text) {
    return String(text).replace(/[&<>"\x27]/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[char]);
}

function renderLoading(container, label = "Loading...") {
    container.innerHTML = `<div class="loading-state">${escapeHTML(label)}</div>`;
}

function renderEmpty(container, label = "Nothing to show yet.") {
    container.innerHTML = `<div class="empty-state">${escapeHTML(label)}</div>`;
}

function renderError(container, error) {
    const message = error && error.message
        ? error.message
        : "Something went wrong.";
    container.innerHTML = `<div class="error-state">${escapeHTML(message)}</div>`;
}

function badge(value) {
    if (!value) return "";
    const cls = String(value).toLowerCase().replace(/\s+/g, "_");
    return `<span class="badge ${cls}">${escapeHTML(value)}</span>`;
}

function formatDate(value) {
    if (!value) return "-";
    return value;
}

function initTopbarUser() {
    const user = getStoredUser();
    const nameEl = document.getElementById("topbarUserName");
    const roleEl = document.getElementById("topbarUserRole");
    if (user && nameEl && roleEl) {
        nameEl.textContent = user.username;
        roleEl.textContent = user.role;
    }

    const logoutBtn = document.getElementById("logoutBtn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => logout());
    }
}

function initTabNavigation() {
    const tabs = document.querySelectorAll(".nav-tab");
    const views = document.querySelectorAll(".view");

    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            tabs.forEach(t => t.classList.remove("active"));
            views.forEach(v => v.classList.remove("active"));

            tab.classList.add("active");
            const target = document.getElementById(tab.dataset.target);
            if (target) target.classList.add("active");

            if (typeof window.onTabActivated === "function") {
                window.onTabActivated(tab.dataset.target);
            }
        });
    });
}