const messagesContainer = document.getElementById("messagesContainer");
const tabs = document.querySelectorAll(".tab");
const sortFilter = document.getElementById("sortFilter");

let currentFilter = "all";
let messages = [];

async function fetchMessages() {
    const res = await fetch('/api/admin/contacts');
    messages = await res.json();
    renderMessages();
}

async function updateStatus(id, status) {
    await fetch(`/api/admin/contacts/${id}/status`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status })
    });
    fetchMessages();
}

async function deleteMessage(id) {
    await fetch(`/api/admin/contacts/${id}`, {
        method: "DELETE"
    });
    fetchMessages();
}

function renderMessages() {
    messagesContainer.innerHTML = "";

    let filtered = messages.filter(msg =>
        currentFilter === "all" ? true : msg.status === currentFilter
    );

    filtered.sort((a, b) =>
        sortFilter.value === "new"
            ? new Date(b.time) - new Date(a.time)
            : new Date(a.time) - new Date(b.time)
    );

    if (!filtered.length) {
        messagesContainer.innerHTML = "<p style='text-align:center'>No messages</p>";
        return;
    }

    filtered.forEach(msg => {
        const card = document.createElement("div");
        const isCompleted = msg.status === "completed";

        card.className = `card ${isCompleted ? "completed" : ""}`;

        card.innerHTML = `
            <button class="delete-btn">🗑️</button>
            <h3>${msg.name}</h3>
            <p>📧 ${msg.email}</p>
            <p>📱 ${msg.phone}</p>
            <p><b>${msg.service}</b></p>
            <div class="message-box">${msg.message}</div>
            <div class="footer">
                <small>${new Date(msg.time).toLocaleString()}</small>
                <button class="status-btn">
                    ${isCompleted ? "Mark Incomplete" : "Mark Completed"}
                </button>
            </div>
        `;

        card.querySelector(".status-btn").onclick = () =>
            updateStatus(msg.id, isCompleted ? "incomplete" : "completed");

        card.querySelector(".delete-btn").onclick = () => {
            if (confirm("Delete this message?")) deleteMessage(msg.id);
        };

        messagesContainer.appendChild(card);
    });
}

tabs.forEach(tab => {
    tab.onclick = () => {
        tabs.forEach(t => t.classList.remove("active"));
        tab.classList.add("active");
        currentFilter = tab.dataset.filter;
        renderMessages();
    };
});

sortFilter.onchange = renderMessages;
fetchMessages();
