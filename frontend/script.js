const API_URL = "http://127.0.0.1:8000/api/chat/";

const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const messages = document.getElementById("messages");
const welcomeScreen = document.getElementById("welcomeScreen");
const sendBtn = document.getElementById("sendBtn");
const chatArea = document.getElementById("chatArea");
const newChatBtn = document.getElementById("newChatBtn");

function scrollToBottom() {
    chatArea.scrollTo({
        top: chatArea.scrollHeight,
        behavior: "smooth"
    });
}

function escapeHTML(text) {
    return text.replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[char]);
}

function formatMessage(text) {
    let safe = escapeHTML(text);

    safe = safe.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    safe = safe.replace(/^### (.*$)/gm, "<h3>$1</h3>");
    safe = safe.replace(/^## (.*$)/gm, "<h3>$1</h3>");
    safe = safe.replace(/^- (.*)$/gm, "• $1");
    safe = safe.replace(/\n/g, "<br>");

    return safe;
}

function getTime() {
    return new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit"
    });
}

function addMessage(text, sender) {
    welcomeScreen.style.display = "none";

    const message = document.createElement("div");
    message.className = `message ${sender}`;

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = sender === "user" ? "Y" : "O";

    const wrapper = document.createElement("div");
    wrapper.className = "message-wrapper";

    const content = document.createElement("div");
    content.className = "message-content";
    content.innerHTML = formatMessage(text);

    const timestamp = document.createElement("div");
    timestamp.className = "message-time";
    timestamp.textContent = getTime();

    wrapper.appendChild(content);
    wrapper.appendChild(timestamp);

    message.appendChild(avatar);
    message.appendChild(wrapper);

    messages.appendChild(message);
    scrollToBottom();

    return message;
}

function showTypingIndicator() {
    welcomeScreen.style.display = "none";

    const message = document.createElement("div");
    message.className = "message assistant";
    message.id = "typingIndicator";

    message.innerHTML = `
        <div class="avatar">O</div>
        <div class="message-wrapper">
            <div class="message-content typing-bubble">
                <span></span><span></span><span></span>
            </div>
            <div class="message-time">OrgMind AI is thinking</div>
        </div>
    `;

    messages.appendChild(message);
    scrollToBottom();

    return message;
}

async function sendMessage(question) {
    if (!question.trim() || sendBtn.disabled) return;

    addMessage(question, "user");

    messageInput.value = "";
    messageInput.style.height = "auto";
    sendBtn.disabled = true;

    const typing = showTypingIndicator();

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question
            })
        });

        if (!response.ok) {
            throw new Error(`Server returned ${response.status}`);
        }

        const data = await response.json();

        typing.remove();

        addMessage(
            data.answer || "I couldn't generate an answer.",
            "assistant"
        );

    } catch (error) {
        console.error("Chat error:", error);

        typing.remove();

        addMessage(
            "I couldn't connect to the backend. Please check that the server is running and try again.",
            "assistant"
        );

    } finally {
        sendBtn.disabled = false;
        messageInput.focus();
        scrollToBottom();
    }
}

chatForm.addEventListener("submit", event => {
    event.preventDefault();
    sendMessage(messageInput.value);
});

messageInput.addEventListener("keydown", event => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        chatForm.requestSubmit();
    }
});

messageInput.addEventListener("input", () => {
    messageInput.style.height = "auto";
    messageInput.style.height =
        Math.min(messageInput.scrollHeight, 120) + "px";
});

document.querySelectorAll("[data-question]").forEach(button => {
    button.addEventListener("click", () => {
        sendMessage(button.dataset.question);
    });
});

newChatBtn.addEventListener("click", () => {
    messages.innerHTML = "";
    welcomeScreen.style.display = "block";
    messageInput.value = "";
    messageInput.focus();
});
