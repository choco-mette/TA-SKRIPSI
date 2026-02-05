// Dashboard DOM Logic
let currentConversationId = null;
let currentUser = null;

// --- Initialization ---
document.addEventListener('DOMContentLoaded', async () => {
    // Auth Check
    if (!isAuthenticated()) {
        window.location.href = '/login';
        return;
    }

    await loadUser();
    await loadConversations();
    
    // Check URL for Conversation ID
    const pathParts = window.location.pathname.split('/');
    // Expected: /chat/{uuid} or just /chat
    if (pathParts.length >= 3 && pathParts[1] === 'chat' && pathParts[2]) {
        const potentialId = pathParts[2];
        // optional: validate UUID format if needed
        if (potentialId) {
            await loadChat(potentialId, false); // false = don't push state since we are here
        }
    }
});

async function loadUser() {
    const res = await apiCall('/auth/me');
    if (res && res.ok) {
        currentUser = await res.json();
        
        // Strict Role Check: Admins specific page
        // if (currentUser.role === 'admin') {
        //    window.location.href = '/admin';
        //    return;
        // }

        const nameEl = document.getElementById('user-name');
        const sidebarAvatarEl = document.getElementById('sidebar-user-avatar');

        if (nameEl) nameEl.textContent = currentUser.username;
        
        // Update Sidebar Avatar
        if (sidebarAvatarEl) {
             const avatarUrl = getUserAvatarUrl(currentUser.gender, currentUser.username);
             sidebarAvatarEl.innerHTML = `<div class="w-8 rounded-full"><img src="${avatarUrl}" alt="${currentUser.username}" /></div>`;
        }
    }
}

function getUserAvatarUrl(gender, username) {
    // Gender enum: 'laki-laki' | 'perempuan'
    if (gender === 'laki-laki') {
        return '/static/images/boy-avatar.png'; // Local boy
    } else if (gender === 'perempuan') {
        return '/static/images/girl-avatar.png'; // Local girl
    } else {
        return '/static/images/user-avatar.png'; // Local fallback
    }
}


// --- Conversations Logic ---
async function loadConversations() {
    const res = await apiCall('/conversations');
    const listEl = document.getElementById('conversation-list');
    
    if (!listEl) return;
    
    listEl.innerHTML = '';

    if (res && res.ok) {
        const conversations = await res.json();
        if (conversations.length === 0) {
            listEl.innerHTML = '<div class="text-center p-4 opacity-50 text-sm">No history yet.</div>';
            return;
        }

        conversations.forEach(conv => {
            const btn = document.createElement('button');
            btn.className = 'btn btn-ghost btn-sm w-full justify-start font-normal truncate';
            btn.onclick = () => loadChat(conv.id);
            btn.id = `conv-${conv.id}`;
            btn.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4 mr-2 opacity-70">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 01.865-.501 48.172 48.172 0 003.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018z" />
                </svg>
                <span class="truncate">${conv.title || 'Conversation ' + conv.id.slice(0,4)}</span>
            `;
            listEl.appendChild(btn);
        });
    }
}

async function startNewChat() {
    const res = await apiCall('/conversations', 'POST');
    if (res && res.ok) {
        const newConv = await res.json();
        await loadConversations();
        loadChat(newConv.id);
    }
}

// --- Chat Logic ---
async function loadChat(conversationId, updateUrl = true) {
    currentConversationId = conversationId;
    
    // Update URL if requested
    if (updateUrl) {
         history.pushState({conversationId}, '', `/chat/${conversationId}`);
    }

    // Update Sidebar UI
    const allBtns = document.querySelectorAll('#conversation-list button');
    allBtns.forEach(b => b.classList.remove('btn-active'));
    
    const activeBtn = document.getElementById(`conv-${conversationId}`);
    if(activeBtn) activeBtn.classList.add('btn-active');

    // Reset Main View
    const welcomeScreen = document.getElementById('welcome-screen');
    const messagesContainer = document.getElementById('chat-messages');
    
    if(welcomeScreen) welcomeScreen.classList.add('hidden');
    if(messagesContainer) messagesContainer.innerHTML = '';
    
    // Enable Input
    const input = document.getElementById('message-input');
    const btn = document.getElementById('send-btn');
    if(input) input.disabled = false;
    if(btn) btn.disabled = false;

    // Load Messages
    const res = await apiCall(`/conversations/${conversationId}/messages`);
    if (res && res.ok) {
        const messages = await res.json();
        messages.forEach(msg => appendMessage(msg));
        scrollToBottom();
    }
}

function appendMessage(msg) {
    const container = document.getElementById('chat-messages');
    if (!container) return;

    // Backend returns 'llm' or 'user' in 'sender' field
    const isBot = msg.sender === 'llm'; 
    const alignClass = isBot ? 'chat-start' : 'chat-end';
    const bubbleColor = isBot ? 'chat-bubble-secondary' : 'chat-bubble-primary';
    
    // Determine Avatar URL
    let avatarUrl;
    if (isBot) {
        avatarUrl = '/static/images/bot-avatar.png'; // Use local
    } else {
        // Use Global currentUser provided by loadUser() or fallback
        if (currentUser) {
            avatarUrl = getUserAvatarUrl(currentUser.gender, currentUser.username);
        } else {
            avatarUrl = '/static/images/user-avatar.png';
        }
    }
    
    // Debug Avatar URL (check console if blank)
    // console.log(`Message from ${isBot ? 'Bot' : 'User'}:`, avatarUrl);

    // Check for msg.message (backend) or msg.content (legacy/fallback)
    const textContent = msg.message || msg.content || '';

    // Handle Image Error inside HTML string (fallback to text if image fails)
    const imgError = "this.onerror=null;this.src='/static/images/user-avatar.png';";

    const html = `
        <div class="chat ${alignClass}">
            <div class="chat-image avatar">
                <div class="w-10 rounded-full">
                    <img src="${avatarUrl}" onerror="${imgError}" />
                </div>
            </div>
            <div class="chat-header opacity-50 text-xs mb-1">
                ${isBot ? 'Wellness Assistant' : (currentUser ? currentUser.username : 'You')}
            </div>
            <div class="chat-bubble ${bubbleColor} whitespace-pre-wrap">${textContent}</div>
        </div>
    `;
    container.insertAdjacentHTML('beforeend', html);
}

async function sendMessage(event) {
    event.preventDefault();
    const input = document.getElementById('message-input');
    const content = input.value.trim();
    
    if (!content || !currentConversationId) return;

    // UI Optimistic Update (Use backend format)
    appendMessage({ sender: 'user', message: content });
    input.value = '';
    scrollToBottom();

    // Show loading indicator
    const loadingId = 'loading-' + Date.now();
    const container = document.getElementById('chat-messages');
    container.insertAdjacentHTML('beforeend', `
        <div id="${loadingId}" class="chat chat-start">
            <div class="chat-image avatar">
                <div class="w-10 rounded-full">
                     <img src="https://ui-avatars.com/api/?name=AI&background=10b981&color=fff" />
                </div>
            </div>
            <div class="chat-bubble chat-bubble-secondary">
                <span class="loading loading-dots loading-sm"></span>
            </div>
        </div>
    `);
    scrollToBottom();

    try {
        // Send { "message": "..." } as expected by Pydantic ChatRequest
        const res = await apiCall(`/conversations/${currentConversationId}/messages`, 'POST', { message: content });
        
        // Remove loading
        const loader = document.getElementById(loadingId);
        if(loader) loader.remove();

        if (res && res.ok) {
            const responseData = await res.json();
            // Response is { messages: [UserMsg, AiMsg] }
            // We already showed UserMsg optimistically, so only show the last one (AI Response)
            // Or better: ensure we only append what we haven't shown. 
            // The backend returns both.
            
            if (responseData.messages && responseData.messages.length > 0) {
                 // Find the AI message
                 const aiMsg = responseData.messages.find(m => m.sender === 'llm');
                 if (aiMsg) {
                     appendMessage(aiMsg);
                 }
            }
        } else {
            showToast('Failed to send message', 'error');
        }
    } catch (e) {
        const loader = document.getElementById(loadingId);
        if(loader) loader.remove();
        console.error(e);
        showToast('Error sending message', 'error');
    }
    scrollToBottom();
}

function scrollToBottom() {
    const container = document.getElementById('chat-messages');
    if(container) container.scrollTop = container.scrollHeight;
}
