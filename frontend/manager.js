if (!requireAuthOrRedirect()) {
    throw new Error("redirecting");
}

const currentUser = getStoredUser();
if (!currentUser || currentUser.role !== "manager") {
    window.location.href = currentUser && currentUser.role === "employee"
        ? "employee.html"
        : "login.html";
    throw new Error("wrong role");
}

initTopbarUser();
initTabNavigation();

const loadedTabs = new Set();

window.onTabActivated = function (target) {
    loadView(target);
};

function loadView(target) {
    if (loadedTabs.has(target)) return;
    loadedTabs.add(target);

    switch (target) {
        case "view-overview": loadOverview(); break;
        case "view-employees": loadEmployees(); break;
        case "view-departments": loadDepartments(); break;
        case "view-projects": loadProjects(); break;
        case "view-attendance": loadAttendance(); break;
        case "view-employee-intel": loadEmployeeIntelligence(); break;
        case "view-project-intel": loadProjectIntelligence(); break;
    }
}

// ---------------- OVERVIEW ----------------

async function loadOverview() {
    const cards = document.getElementById("overviewCards");
    const delayedContainer = document.getElementById("delayedProjectsContainer");
    renderLoading(cards, "Loading organization overview...");
    renderLoading(delayedContainer, "Loading delayed projects...");

    try {
        const [employees, departments, projects, delayed] = await Promise.all([
            apiFetch("/api/employees/"),
            apiFetch("/api/departments/"),
            apiFetch("/api/projects/"),
            apiFetch("/api/projects/delayed")
        ]);

        const ongoing = projects.filter(p => p.status === "ongoing").length;

        cards.innerHTML = `
            <div class="stat-card"><div class="stat-label">Total Employees</div><div class="stat-value">${employees.length}</div></div>
            <div class="stat-card"><div class="stat-label">Departments</div><div class="stat-value">${departments.length}</div></div>
            <div class="stat-card"><div class="stat-label">Total Projects</div><div class="stat-value">${projects.length}</div></div>
            <div class="stat-card"><div class="stat-label">Ongoing Projects</div><div class="stat-value">${ongoing}</div></div>
            <div class="stat-card"><div class="stat-label">Delayed Projects</div><div class="stat-value">${delayed.length}</div></div>
        `;

        if (delayed.length === 0) {
            renderEmpty(delayedContainer, "No delayed projects. Everything is on track.");
        } else {
            delayedContainer.innerHTML = `
                <table class="data-table">
                    <thead><tr><th>Project</th><th>Status</th><th>Progress</th><th>Deadline</th></tr></thead>
                    <tbody>
                        ${delayed.map(p => `
                            <tr>
                                <td>${escapeHTML(p.name)}</td>
                                <td>${badge(p.status)}</td>
                                <td>${p.progress}%</td>
                                <td>${formatDate(p.deadline)}</td>
                            </tr>
                        `).join("")}
                    </tbody>
                </table>
            `;
        }
    } catch (error) {
        renderError(cards, error);
        renderError(delayedContainer, error);
    }
}

// ---------------- EMPLOYEES ----------------

async function loadEmployees() {
    const container = document.getElementById("employeesContainer");
    renderLoading(container, "Loading employees...");

    try {
        const employees = await apiFetch("/api/employees/");

        if (employees.length === 0) {
            renderEmpty(container, "No employees found.");
            return;
        }

        container.innerHTML = `
            <table class="data-table">
                <thead><tr><th>Name</th><th>Code</th><th>Email</th><th>Designation</th><th>Status</th></tr></thead>
                <tbody>
                    ${employees.map(e => `
                        <tr>
                            <td>${escapeHTML(e.name)}</td>
                            <td>${escapeHTML(e.employee_code)}</td>
                            <td>${escapeHTML(e.email)}</td>
                            <td>${escapeHTML(e.designation || "-")}</td>
                            <td>${badge(e.employment_status)}</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        `;
    } catch (error) {
        renderError(container, error);
    }
}

// ---------------- DEPARTMENTS ----------------

async function loadDepartments() {
    const container = document.getElementById("departmentsContainer");
    renderLoading(container, "Loading departments...");

    try {
        const departments = await apiFetch("/api/departments/");

        if (departments.length === 0) {
            renderEmpty(container, "No departments found.");
            return;
        }

        container.innerHTML = `
            <table class="data-table">
                <thead><tr><th>Name</th><th>Description</th></tr></thead>
                <tbody>
                    ${departments.map(d => `
                        <tr>
                            <td>${escapeHTML(d.name)}</td>
                            <td>${escapeHTML(d.description || "-")}</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        `;
    } catch (error) {
        renderError(container, error);
    }
}

// ---------------- PROJECTS ----------------

async function loadProjects() {
    const container = document.getElementById("projectsContainer");
    renderLoading(container, "Loading projects...");

    try {
        const projects = await apiFetch("/api/projects/");

        if (projects.length === 0) {
            renderEmpty(container, "No projects found.");
            return;
        }

        container.innerHTML = `
            <table class="data-table">
                <thead><tr><th>Project</th><th>Status</th><th>Progress</th><th>Deadline</th></tr></thead>
                <tbody>
                    ${projects.map(p => `
                        <tr>
                            <td>${escapeHTML(p.name)}</td>
                            <td>${badge(p.status)}</td>
                            <td style="min-width:140px;">
                                <div class="progress-bar-track"><div class="progress-bar-fill" style="width:${p.progress}%;"></div></div>
                                <small>${p.progress}%</small>
                            </td>
                            <td>${formatDate(p.deadline)}</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        `;
    } catch (error) {
        renderError(container, error);
    }
}

// ---------------- ATTENDANCE ----------------

async function loadAttendance() {
    const container = document.getElementById("attendanceContainer");
    renderLoading(container, "Loading today attendance...");

    try {
        const records = await apiFetch("/api/attendance/today");

        if (records.length === 0) {
            renderEmpty(container, "No attendance recorded yet today.");
            return;
        }

        container.innerHTML = `
            <table class="data-table">
                <thead><tr><th>Employee</th><th>Check In</th><th>Check Out</th><th>Status</th></tr></thead>
                <tbody>
                    ${records.map(r => `
                        <tr>
                            <td>${escapeHTML(r.employee_name)}</td>
                            <td>${r.check_in ? new Date(r.check_in).toLocaleTimeString() : "-"}</td>
                            <td>${r.check_out ? new Date(r.check_out).toLocaleTimeString() : "-"}</td>
                            <td>${badge(r.status)}</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        `;
    } catch (error) {
        renderError(container, error);
    }
}

// ---------------- EMPLOYEE INTELLIGENCE ----------------

async function loadEmployeeIntelligence() {
    const container = document.getElementById("employeeIntelContainer");
    renderLoading(container, "Analyzing employees...");

    try {
        const overview = await apiFetch("/api/employee-intelligence/overview");

        if (overview.employees.length === 0) {
            renderEmpty(container, "No employee intelligence available.");
            return;
        }

        container.innerHTML = `
            <p style="margin-bottom:14px; color:#6b7280; font-size:13px;">
                ${overview.total_employees} employees analyzed, ${overview.employees_with_insights} with active insights.
            </p>
            <table class="data-table">
                <thead><tr><th>Employee</th><th>Completion</th><th>Pending</th><th>Insights</th></tr></thead>
                <tbody>
                    ${overview.employees.map(e => `
                        <tr>
                            <td>${escapeHTML(e.employee_name || "-")}</td>
                            <td>${e.completion_percentage}%</td>
                            <td>${e.pending_tasks}</td>
                            <td>${(e.insights || []).map(i => escapeHTML(i)).join("<br>") || "-"}</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        `;
    } catch (error) {
        renderError(container, error);
    }
}

// ---------------- PROJECT INTELLIGENCE ----------------

async function loadProjectIntelligence() {
    const container = document.getElementById("projectIntelContainer");
    renderLoading(container, "Analyzing projects...");

    try {
        const overview = await apiFetch("/api/project-intelligence/overview");

        if (overview.projects.length === 0) {
            renderEmpty(container, "No project intelligence available.");
            return;
        }

        container.innerHTML = `
            <p style="margin-bottom:14px; color:#6b7280; font-size:13px;">
                ${overview.total_projects} projects analyzed, ${overview.at_risk_projects} at risk.
            </p>
            <table class="data-table">
                <thead><tr><th>Project</th><th>Completion</th><th>Overdue Tasks</th><th>Risks</th></tr></thead>
                <tbody>
                    ${overview.projects.map(p => `
                        <tr>
                            <td>${escapeHTML(p.project_name || "-")}</td>
                            <td>${p.completion_percentage_from_tasks}%</td>
                            <td>${(p.overdue_tasks || []).length}</td>
                            <td>${(p.risks || []).map(r => escapeHTML(r)).join("<br>") || "-"}</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        `;
    } catch (error) {
        renderError(container, error);
    }
}

// ---------------- AI CHAT ----------------

const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const messagesEl = document.getElementById("messages");
const welcomeScreen = document.getElementById("welcomeScreen");
const sendBtn = document.getElementById("sendBtn");
const chatArea = document.getElementById("chatArea");

function scrollToBottom() {
    chatArea.scrollTo({ top: chatArea.scrollHeight, behavior: "smooth" });
}

function addMessage(text, sender) {
    welcomeScreen.style.display = "none";
    const message = document.createElement("div");
    message.className = `message ${sender}`;
    message.innerHTML = `
        <div class="avatar">${sender === "user" ? "Y" : "O"}</div>
        <div class="message-wrapper">
            <div class="message-content">${escapeHTML(text).replace(/\n/g, "<br>")}</div>
            <div class="message-time">${new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</div>
        </div>
    `;
    messagesEl.appendChild(message);
    scrollToBottom();
    return message;
}

async function sendMessage(question) {
    if (!question.trim() || sendBtn.disabled) return;

    addMessage(question, "user");
    messageInput.value = "";
    sendBtn.disabled = true;

    const typing = addMessage("OrgMind AI is thinking...", "assistant");

    try {
        const data = await apiFetch("/api/chat/", {
            method: "POST",
            body: JSON.stringify({ question })
        });
        typing.remove();
        addMessage(data.answer || "I could not generate an answer.", "assistant");
    } catch (error) {
        typing.remove();
        addMessage(error.message || "I could not connect to the backend.", "assistant");
    } finally {
        sendBtn.disabled = false;
    }
}

chatForm.addEventListener("submit", event => {
    event.preventDefault();
    sendMessage(messageInput.value);
});

// Initial view
loadView("view-overview");
