if (!requireAuthOrRedirect()) {
    throw new Error("redirecting");
}

const currentUser = getStoredUser();
if (!currentUser || currentUser.role !== "employee") {
    window.location.href = currentUser && currentUser.role === "manager"
        ? "manager.html"
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
        case "view-profile": loadProfile(); break;
        case "view-projects": loadMyProjects(); break;
        case "view-tasks": loadMyTasks(); break;
        case "view-attendance": loadMyAttendance(); break;
        case "view-intel": loadMyIntelligence(); break;
    }
}

function getEmployeeId() {
    return currentUser.employee_id;
}

// ---------------- PROFILE ----------------

async function loadProfile() {
    const container = document.getElementById("profileContainer");

    if (!getEmployeeId()) {
        renderError(container, { message: "No employee profile is linked to this account. Contact your administrator." });
        return;
    }

    renderLoading(container, "Loading profile...");

    try {
        const employee = await apiFetch(`/api/employees/${getEmployeeId()}`);

        container.innerHTML = `
            <div class="cards-grid">
                <div class="stat-card"><div class="stat-label">Name</div><div class="stat-value" style="font-size:17px;">${escapeHTML(employee.name)}</div></div>
                <div class="stat-card"><div class="stat-label">Employee Code</div><div class="stat-value" style="font-size:17px;">${escapeHTML(employee.employee_code)}</div></div>
                <div class="stat-card"><div class="stat-label">Designation</div><div class="stat-value" style="font-size:17px;">${escapeHTML(employee.designation || "-")}</div></div>
                <div class="stat-card"><div class="stat-label">Status</div><div class="stat-value" style="font-size:17px;">${badge(employee.employment_status)}</div></div>
            </div>
            <p style="color:#6b7280; font-size:13px;">Email: ${escapeHTML(employee.email)}</p>
        `;
    } catch (error) {
        renderError(container, error);
    }
}

// ---------------- PROJECTS ----------------

async function loadMyProjects() {
    const container = document.getElementById("projectsContainer");
    renderLoading(container, "Loading your projects...");

    try {
        const projects = await apiFetch("/api/projects/");

        if (projects.length === 0) {
            renderEmpty(container, "You are not assigned to any projects yet.");
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

// ---------------- TASKS ----------------

async function loadMyTasks() {
    const container = document.getElementById("tasksContainer");
    renderLoading(container, "Loading your tasks...");

    try {
        const projects = await apiFetch("/api/projects/");
        let allTasks = [];

        for (const project of projects) {
            const tasks = await apiFetch(`/api/projects/${project.id}/tasks`);
            allTasks = allTasks.concat(tasks.map(t => ({ ...t, project_name: project.name })));
        }

        if (allTasks.length === 0) {
            renderEmpty(container, "You have no assigned tasks.");
            return;
        }

        container.innerHTML = allTasks.map(t => `
            <div class="task-card" data-task-id="${t.id}">
                <div class="task-card-header">
                    <strong>${escapeHTML(t.title)}</strong>
                    ${badge(t.priority)}
                </div>
                <p style="font-size:12.5px; color:#6b7280; margin-bottom:6px;">
                    ${escapeHTML(t.project_name)} &middot; Due ${formatDate(t.due_date)}
                </p>
                ${t.description ? `<p style="font-size:13px; margin-bottom:8px;">${escapeHTML(t.description)}</p>` : ""}
                <div style="display:flex; align-items:center; gap:10px;">
                    ${badge(t.status)}
                    <div class="progress-bar-track" style="flex:1; max-width:220px;"><div class="progress-bar-fill" style="width:${t.progress}%;"></div></div>
                    <small>${t.progress}%</small>
                </div>
                <div class="task-controls">
                    <select class="task-status-select">
                        <option value="pending" ${t.status === "pending" ? "selected" : ""}>Pending</option>
                        <option value="in_progress" ${t.status === "in_progress" ? "selected" : ""}>In Progress</option>
                        <option value="completed" ${t.status === "completed" ? "selected" : ""}>Completed</option>
                    </select>
                    <input type="number" class="task-progress-input" min="0" max="100" value="${t.progress}">
                    <button type="button" class="task-save-btn">Save Progress</button>
                    <span class="inline-save-msg"></span>
                </div>
            </div>
        `).join("");

        container.querySelectorAll(".task-card").forEach(card => {
            const taskId = card.dataset.taskId;
            const saveBtn = card.querySelector(".task-save-btn");
            const statusSelect = card.querySelector(".task-status-select");
            const progressInput = card.querySelector(".task-progress-input");
            const msgEl = card.querySelector(".inline-save-msg");

            saveBtn.addEventListener("click", async () => {
                const progressValue = Number(progressInput.value);

                if (Number.isNaN(progressValue) || progressValue < 0 || progressValue > 100) {
                    msgEl.textContent = "Progress must be between 0 and 100.";
                    msgEl.classList.add("error");
                    return;
                }

                saveBtn.disabled = true;
                msgEl.classList.remove("error");
                msgEl.textContent = "Saving...";

                try {
                    const updated = await apiFetch(`/api/projects/tasks/${taskId}/progress`, {
                        method: "PATCH",
                        body: JSON.stringify({
                            status: statusSelect.value,
                            progress: progressValue
                        })
                    });

                    msgEl.textContent = "Saved.";
                    msgEl.classList.remove("error");

                    const track = card.querySelector(".progress-bar-fill");
                    const trackLabel = card.querySelector(".progress-bar-track").nextElementSibling;
                    if (track) track.style.width = `${updated.progress}%`;
                    if (trackLabel) trackLabel.textContent = `${updated.progress}%`;

                } catch (error) {
                    msgEl.textContent = error.message || "Could not save progress.";
                    msgEl.classList.add("error");
                } finally {
                    saveBtn.disabled = false;
                }
            });
        });

    } catch (error) {
        renderError(container, error);
    }
}

// ---------------- ATTENDANCE ----------------

async function loadMyAttendance() {
    const todayContainer = document.getElementById("todayAttendanceContainer");
    const historyContainer = document.getElementById("attendanceHistoryContainer");

    if (!getEmployeeId()) {
        renderError(todayContainer, { message: "No employee profile is linked to this account." });
        return;
    }

    renderLoading(todayContainer, "Loading today status...");
    renderLoading(historyContainer, "Loading history...");

    try {
        const [today, history] = await Promise.all([
            apiFetch(`/api/attendance/employee/${getEmployeeId()}/today`),
            apiFetch(`/api/attendance/employee/${getEmployeeId()}`)
        ]);

        todayContainer.innerHTML = `
            <div class="cards-grid">
                <div class="stat-card"><div class="stat-label">Status</div><div class="stat-value" style="font-size:16px;">${escapeHTML(today.attendance || "-")}</div></div>
                <div class="stat-card"><div class="stat-label">Check In</div><div class="stat-value" style="font-size:16px;">${today.check_in ? new Date(today.check_in).toLocaleTimeString() : "-"}</div></div>
                <div class="stat-card"><div class="stat-label">Check Out</div><div class="stat-value" style="font-size:16px;">${today.check_out ? new Date(today.check_out).toLocaleTimeString() : "-"}</div></div>
            </div>
        `;

        if (history.length === 0) {
            renderEmpty(historyContainer, "No attendance history yet.");
            return;
        }

        historyContainer.innerHTML = `
            <table class="data-table">
                <thead><tr><th>Date</th><th>Check In</th><th>Check Out</th><th>Status</th></tr></thead>
                <tbody>
                    ${history.map(r => `
                        <tr>
                            <td>${formatDate(r.attendance_date)}</td>
                            <td>${r.check_in ? new Date(r.check_in).toLocaleTimeString() : "-"}</td>
                            <td>${r.check_out ? new Date(r.check_out).toLocaleTimeString() : "-"}</td>
                            <td>${badge(r.status)}</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        `;
    } catch (error) {
        renderError(todayContainer, error);
        renderError(historyContainer, error);
    }
}

// ---------------- MY INTELLIGENCE ----------------

async function loadMyIntelligence() {
    const container = document.getElementById("intelContainer");

    if (!getEmployeeId()) {
        renderError(container, { message: "No employee profile is linked to this account." });
        return;
    }

    renderLoading(container, "Analyzing your work...");

    try {
        const result = await apiFetch(`/api/employee-intelligence/${getEmployeeId()}/analysis`);

        container.innerHTML = `
            <div class="cards-grid">
                <div class="stat-card"><div class="stat-label">Completion</div><div class="stat-value">${result.completion_percentage}%</div></div>
                <div class="stat-card"><div class="stat-label">Total Tasks</div><div class="stat-value">${result.total_tasks}</div></div>
                <div class="stat-card"><div class="stat-label">Completed</div><div class="stat-value">${result.completed_tasks}</div></div>
                <div class="stat-card"><div class="stat-label">Pending</div><div class="stat-value">${result.pending_tasks}</div></div>
            </div>
            <div class="panel" style="margin-top:0;">
                <h3>Insights</h3>
                ${(result.insights || []).length > 0
                    ? `<ul style="padding-left:18px; font-size:13px;">${result.insights.map(i => `<li>${escapeHTML(i)}</li>`).join("")}</ul>`
                    : `<p style="color:#9299a9; font-size:13px;">No active insights.</p>`}
            </div>
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
loadView("view-profile");
