const messagesContainer = document.getElementById("messagesContainer");
const tabs = document.querySelectorAll(".tab");
const sortFilter = document.getElementById("sortFilter");

let currentFilter = "all";
let messages = [];

async function fetchMessages() {
    try {
        const response = await fetch('/api/admin/contacts');
        if (response.ok) {
            messages = await response.json();
            renderMessages();
        } else {
            console.error('Failed to fetch messages');
            messagesContainer.innerHTML = '<div class="card"><h3>Error loading messages</h3></div>';
        }
    } catch (error) {
        console.error('Error:', error);
        messagesContainer.innerHTML = '<div class="card"><h3>Error connecting to server</h3></div>';
    }
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

    if (filtered.length === 0) {
        messagesContainer.innerHTML = '<div style="text-align:center; padding: 20px; color: #666;">No messages found</div>';
        return;
    }

    filtered.forEach(msg => {
        const card = document.createElement("div");
        card.className = `card ${msg.status === "completed" ? "completed" : ""}`;

        const isCompleted = msg.status === "completed";

        card.innerHTML = `
            <button class="delete-btn" title="Delete">🗑️</button>
            <h3>${msg.name}</h3>
            <div class="info">📧 ${msg.email}</div>
            <div class="info">📱 ${msg.phone}</div>
            <div class="info">🔧 <b>${msg.service}</b></div>
            <div class="message-box">${msg.message}</div>
            <div class="footer">
                <small>⏰ ${new Date(msg.time).toLocaleString()}</small>
                <button class="status-btn ${isCompleted ? "incomplete-btn" : "complete-btn"}">
                    ${isCompleted ? "Mark Incomplete" : "Mark Completed"}
                </button>
            </div>
        `;

        card.querySelector(".status-btn").onclick = () => {
            msg.status = isCompleted ? "incomplete" : "completed";
            renderMessages();
            alert("Note: Status update is local only (API update not implemented)");
        };

        card.querySelector(".delete-btn").onclick = () => {
            if (confirm("Delete this message?")) {
                messages = messages.filter(m => m.id !== msg.id);
                renderMessages();
                alert("Note: Deletion is local only (API delete not implemented)");
            }
        };

        messagesContainer.appendChild(card);
    });
}

tabs.forEach(tab => {
    tab.addEventListener("click", () => {
        tabs.forEach(t => t.classList.remove("active"));
        tab.classList.add("active");
        currentFilter = tab.dataset.filter;
        renderMessages();
    });
});

sortFilter.addEventListener("change", renderMessages);

fetchMessages();
