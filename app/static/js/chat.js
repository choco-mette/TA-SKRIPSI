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
            const container = document.createElement('div');
            container.className = 'flex items-center w-full group';

            const btn = document.createElement('button');
            btn.className = 'btn btn-ghost btn-sm flex-1 justify-start font-normal truncate';
            btn.onclick = () => loadChat(conv.id);
            btn.id = `conv-${conv.id}`;
            btn.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-4 h-4 mr-2 opacity-70">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 01.865-.501 48.172 48.172 0 003.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018z" />
                </svg>
                <span class="truncate">${conv.title || 'Conversation ' + conv.id.slice(0,4)}</span>
            `;

            const delBtn = document.createElement('button');
            delBtn.className = 'btn btn-ghost btn-xs btn-square opacity-0 group-hover:opacity-100 transition-opacity ml-1 text-error';
            delBtn.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
                    <path fill-rule="evenodd" d="M8.75 1A2.75 2.75 0 0 0 6 3.75v.443c-.795.077-1.584.176-2.365.298a.75.75 0 1 0 .23 1.482l.149-.022.841 10.518A2.75 2.75 0 0 0 7.596 19h4.807a2.75 2.75 0 0 0 2.742-2.53l.841-10.52.149.023a.75.75 0 0 0 .23-1.482A41.03 41.03 0 0 0 14 4.193V3.75A2.75 2.75 0 0 0 11.25 1h-2.5ZM10 4c.84 0 1.673.025 2.5.075V3.75c0-.69-.56-1.25-1.25-1.25h-2.5c-.69 0-1.25.56-1.25 1.25v.325C8.327 4.025 9.16 4 10 4ZM8.58 7.72a.75.75 0 0 0-1.5.06l.3 7.5a.75.75 0 1 0 1.5-.06l-.3-7.5Zm4.34.06a.75.75 0 1 0-1.5-.06l-.3 7.5a.75.75 0 0 0 1.5.06l.3-7.5Z" clip-rule="evenodd" />
                </svg>
            `;
            delBtn.onclick = (e) => {
                e.stopPropagation();
                if(confirm('Are you sure you want to delete this conversation?')) {
                    deleteConversation(conv.id);
                }
            };

            container.appendChild(btn);
            container.appendChild(delBtn);
            listEl.appendChild(container);
        });
    }
}

async function deleteConversation(id) {
    const res = await apiCall(`/conversations/${id}`, 'DELETE');
    if (res && res.ok) {
        showToast('Conversation deleted', 'success');
        if (currentConversationId === id) {
            startNewChat();
        }
        await loadConversations();
    } else {
        showToast('Failed to delete conversation', 'error');
    }
}

function startNewChat() {
    currentConversationId = null;
    
    // Update URL to /chat
    history.pushState({}, '', '/chat');

    // Reset Sidebar Selection
    const allBtns = document.querySelectorAll('#conversation-list button');
    allBtns.forEach(b => b.classList.remove('btn-active'));

    // Reset Main View
    const welcomeScreen = document.getElementById('welcome-screen');
    const messagesContainer = document.getElementById('chat-messages');

    // Show welcome screen initially, hide messages
    if (welcomeScreen) welcomeScreen.classList.remove('hidden');
    if (messagesContainer) messagesContainer.innerHTML = '';
    
    // Enable Input for new conversation
    const input = document.getElementById('message-input');
    const btn = document.getElementById('send-btn');
    if (input) {
        input.disabled = false;
        input.value = '';
        input.focus();
    }
    if (btn) btn.disabled = false;
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
    
    // UI Change: Use 'chat-bubble-ai' (Custom Soft Gray) for Bot, 'chat-bubble-primary' (Green) for User
    // Note: 'chat-bubble-ai' is defined in base.html styles
    const bubbleColor = isBot ? 'chat-bubble-ai' : 'chat-bubble-primary';
    
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

function setChatState(isLoading) {
    const input = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');
    
    if (input) {
        input.disabled = isLoading;
        if (!isLoading) input.focus();
    }
    if (sendBtn) {
        sendBtn.disabled = isLoading;
        sendBtn.classList.toggle('opacity-50', isLoading);
        sendBtn.classList.toggle('cursor-not-allowed', isLoading);
    }
}

async function sendMessage(event) {
    event.preventDefault();
    const input = document.getElementById('message-input');
    const content = input.value.trim();
    
    if (!content) return;

    // Lock Interface
    setChatState(true);
    let loadingId = null;

    try {
        // --- Lazy Conversation Creation ---
        if (!currentConversationId) {
            // Generate title from first 50 chars, cleaning newlines
            let title = content.split('\n')[0].substring(0, 50).trim();
            if (content.length > 50 || content.split('\n').length > 1) title += '...';

            const res = await apiCall('/conversations', 'POST', { title: title });
            if (res && res.ok) {
                const newConv = await res.json();
                currentConversationId = newConv.id;
                
                // Update URL
                history.pushState({conversationId: currentConversationId}, '', `/chat/${currentConversationId}`);

                // Load Sidebar
                await loadConversations();
                
                // Highlight new chat in sidebar
                const activeBtn = document.getElementById(`conv-${currentConversationId}`);
                if (activeBtn) activeBtn.classList.add('btn-active');

                // Hide Welcome Screen
                const welcomeScreen = document.getElementById('welcome-screen');
                if (welcomeScreen) welcomeScreen.classList.add('hidden');
            } else {
                showToast('Failed to create conversation', 'error');
                return;
            }
        }

        // UI Optimistic Update (Use backend format)
        appendMessage({ sender: 'user', message: content });
        input.value = '';
        scrollToBottom();

        // Show loading indicator
        loadingId = 'loading-' + Date.now();
        const container = document.getElementById('chat-messages');
        container.insertAdjacentHTML('beforeend', `
            <div id="${loadingId}" class="chat chat-start">
                <div class="chat-image avatar">
                    <div class="w-10 rounded-full">
                         <img src="/static/images/bot-avatar.png" onerror="this.src='https://ui-avatars.com/api/?name=AI&background=10b981&color=fff'" />
                    </div>
                </div>
                <div class="chat-bubble chat-bubble-ai">
                    <span class="loading loading-dots loading-sm"></span>
                </div>
            </div>
        `);
        scrollToBottom();

        // Send { "message": "..." } as expected by Pydantic ChatRequest
        const res = await apiCall(`/conversations/${currentConversationId}/messages`, 'POST', { message: content });

        if (res && res.ok) {
            const responseData = await res.json();
            // Response is { messages: [UserMsg, AiMsg] }
            
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
        console.error(e);
        showToast('Error processing message', 'error');
    } finally {
        if (loadingId) {
             const loader = document.getElementById(loadingId);
             if(loader) loader.remove();
        }
        setChatState(false);
        scrollToBottom();
    }
}

function scrollToBottom() {
    const container = document.getElementById('chat-messages');
    if(container) container.scrollTop = container.scrollHeight;
}
