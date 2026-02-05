// Admin Panel Logic

// --- Pagination State ---
const state = {
    rules: { page: 1, limit: 10 },
    envs: { page: 1, limit: 10 },
    docs: { page: 1, limit: 10 },
    knowledge: { page: 1, limit: 10 }
};

document.addEventListener('DOMContentLoaded', async () => {
    if (!isAuthenticated()) {
        window.location.href = '/login';
        return;
    }
    
    // Check admin role
    try {
        const userRes = await apiCall('/auth/me');
        if (userRes && userRes.ok) {
            const user = await userRes.json();
            if (user.role !== 'admin') {
                window.location.href = '/chat';
                return;
            }
        }
    } catch(e) { window.location.href = '/login'; }

    // Initial Load based on URL or Default
    const initial = window.initialSection || 'overview';
    showSection(initial, false);

    // Initial Data Fetch
    refreshAll();
    
    // History Listener
    window.onpopstate = (event) => {
        if (event.state && event.state.section) {
            showSection(event.state.section, false);
        } else {
             // Fallback to path parsing if no state
             const pathParts = window.location.pathname.split('/');
             const section = pathParts[2] || 'overview';
             showSection(section, false);
        }
    };
});

// Navigation
function showSection(sectionId, pushHistory = true) {
    document.querySelectorAll('.admin-section').forEach(el => el.classList.add('hidden'));
    
    const target = document.getElementById(`section-${sectionId}`);
    if (target) {
        target.classList.remove('hidden');
    } else {
        // Fallback
        document.getElementById(`section-overview`).classList.remove('hidden');
    }
    
    document.querySelectorAll('.menu a').forEach(el => el.classList.remove('active'));
    const navItem = document.getElementById(`nav-${sectionId}`);
    if (navItem) navItem.classList.add('active');

    if (pushHistory) {
        const newPath = sectionId === 'overview' ? '/admin' : `/admin/${sectionId}`;
        history.pushState({ section: sectionId }, '', newPath);
    }
}

async function refreshAll() {
    loadRules();
    loadPersonality();
    loadEnvs();
    loadDocs();
    loadKnowledge();
}

// --- Pagination Logic ---
async function nextPage(type) {
    state[type].page++;
    await reloadByType(type);
}

async function prevPage(type) {
    if (state[type].page > 1) {
        state[type].page--;
        await reloadByType(type);
    }
}

async function reloadByType(type) {
    const el = document.getElementById(`page-info-${type}`);
    if(el) el.innerText = `Page ${state[type].page}`;
    
    if (type === 'rules') await loadRules();
    if (type === 'envs') await loadEnvs();
    if (type === 'docs') await loadDocs();
    if (type === 'knowledge') await loadKnowledge();
}

// --- Rules Logic ---
async function loadRules() {
    const skip = (state.rules.page - 1) * state.rules.limit;
    const res = await apiCall(`/admin/rules/?skip=${skip}&limit=${state.rules.limit}`);
    
    if(res && res.ok) {
        const rules = await res.json();
        const statEl = document.getElementById('stat-rules');
        if (state.rules.page === 1 && statEl) statEl.innerText = rules.length + (rules.length === state.rules.limit ? '+' : '');
        
        const tbody = document.getElementById('rules-table-body');
        tbody.innerHTML = '';
        
        if (rules.length === 0 && state.rules.page > 1) {
             state.rules.page--; // Revert
             const el = document.getElementById(`page-info-rules`);
             if(el) el.innerText = `Page ${state.rules.page}`;
             // Reload to show previous (valid) page
             await loadRules();
             return;
        }

        rules.forEach((r, index) => {
            const no = (state.rules.page - 1) * state.rules.limit + index + 1;
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${no}</td>
                <td class="truncate max-w-[150px] md:max-w-xs text-xs" title="${escapeHtml(r.content)}">${escapeHtml(truncate(r.content, 50))}</td>
                <td><div class="badge ${r.is_active ? 'badge-success' : 'badge-ghost'}">${r.is_active ? 'Active' : 'Inactive'}</div></td>
                <td>
                    <button class="btn btn-xs btn-info" onclick="editRule(${r.id}, '${escapeHtml(r.content)}', ${r.is_active})">Edit</button>
                    <button class="btn btn-xs btn-error" onclick="deleteRule(${r.id})">Del</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }
}

function openRuleModal() {
    document.getElementById('rule-id').value = '';
    document.getElementById('rule-content').value = '';
    document.getElementById('rule-active').checked = true;
    document.getElementById('rule-modal-title').innerText = 'Add New Rule';
    document.getElementById('rule_modal').showModal();
}

async function editRule(id, content, isActive) {
    document.getElementById('rule-id').value = id;
    document.getElementById('rule-content').value = unescapeHtml(content);
    document.getElementById('rule-active').checked = isActive;
    document.getElementById('rule-modal-title').innerText = 'Edit Rule';
    document.getElementById('rule_modal').showModal();
}

async function saveRule(e) {
    e.preventDefault(); 
    const id = document.getElementById('rule-id').value;
    const content = document.getElementById('rule-content').value;
    const is_active = document.getElementById('rule-active').checked;
    
    const payload = { content, is_active };
    let res;
    
    if (id) {
         res = await apiCall(`/admin/rules/${id}`, 'PUT', payload);
    } else {
         res = await apiCall('/admin/rules/', 'POST', payload);
    }

    if (res && res.ok) {
        showToast('Rule saved', 'success');
        document.getElementById('rule_modal').close();
        loadRules();
    } else {
        showToast('Failed to save rule', 'error');
    }
}

async function deleteRule(id) {
    if(!confirm('Are you sure?')) return;
    const res = await apiCall(`/admin/rules/${id}`, 'DELETE');
    if (res && (res.ok || res.status === 204)) {
        showToast('Rule deleted', 'success');
        loadRules();
    }
}


// --- Personality Logic ---
async function loadPersonality() {
    const res = await apiCall('/admin/personality/');
    if(res && res.ok) {
        const data = await res.json();
        const p = Array.isArray(data) ? data[0] : data;
        if (p) {
             document.getElementById('personality-input').value = p.content;
        }
    }
}

async function savePersonality() {
    const content = document.getElementById('personality-input').value;
    const res = await apiCall('/admin/personality/', 'PUT', { content });
    if(res && res.ok) {
         showToast('Personality saved', 'success');
    } else {
          const res2 = await apiCall('/admin/personality/', 'POST', { content });
           if(res2 && res2.ok) {
                showToast('Personality created', 'success');
           } else {
                showToast('Failed to save', 'error');
           }
    }
}

// --- Environment Logic ---
async function loadEnvs() {
    const skip = (state.envs.page - 1) * state.envs.limit;
    const res = await apiCall(`/admin/environments/?skip=${skip}&limit=${state.envs.limit}`);
    
    if(res && res.ok) {
        const envs = await res.json();
        const statEl = document.getElementById('stat-envs');
        if (state.envs.page === 1 && statEl) statEl.innerText = envs.length + (envs.length === state.envs.limit ? '+' : '');

        const tbody = document.getElementById('env-table-body');
        tbody.innerHTML = '';
        
        if (envs.length === 0 && state.envs.page > 1) {
             state.envs.page--;
             const el = document.getElementById(`page-info-envs`);
             if(el) el.innerText = `Page ${state.envs.page}`;
             await loadEnvs();
             return;
        }

        envs.forEach((e, index) => {
            const no = (state.envs.page - 1) * state.envs.limit + index + 1;
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${no}</td>
                <td>${e.models_name}</td>
                <td><div class="badge badge-outline">${e.model_type}</div></td>
                <td class="truncate max-w-[150px] md:max-w-xs text-xs">${e.base_url}</td>
                <td><div class="badge ${e.is_active ? 'badge-success' : 'badge-ghost'}">${e.is_active ? 'Active' : 'Inactive'}</div></td>
                <td>
                    <button class="btn btn-xs btn-info" onclick="editEnv(${e.id}, '${e.models_name}', '${e.base_url}', '${e.model_type}', ${e.is_active})">Edit</button>
                    <button class="btn btn-xs btn-error" onclick="deleteEnv(${e.id})">Del</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }
}

function openEnvModal() {
    document.getElementById('env-id').value = '';
    document.getElementById('env-name').value = '';
    document.getElementById('env-key').value = '';
    document.getElementById('env-url').value = '';
    document.getElementById('env-type').value = 'chat';
    document.getElementById('env-active').checked = false;
    document.getElementById('env-modal-title').innerText = 'Add Environment';
    document.getElementById('env_modal').showModal();
}

function editEnv(id, name, url, type, active) {
    document.getElementById('env-id').value = id;
    document.getElementById('env-name').value = name;
    document.getElementById('env-url').value = url;
    document.getElementById('env-key').value = ''; 
    document.getElementById('env-type').value = type;
    document.getElementById('env-active').checked = active;
    document.getElementById('env-modal-title').innerText = 'Edit Environment';
    document.getElementById('env_modal').showModal();
}

async function saveEnv(e) {
    e.preventDefault();
    const id = document.getElementById('env-id').value;
    const models_name = document.getElementById('env-name').value;
    const base_url = document.getElementById('env-url').value;
    const api_key = document.getElementById('env-key').value;
    const model_type = document.getElementById('env-type').value;
    const is_active = document.getElementById('env-active').checked;
    
    const payload = { models_name, base_url, model_type, is_active };
    if (api_key) payload.api_key = api_key;
    if (!id && !api_key) { showToast('API Key required for new env', 'error'); return; }

    let res;
    if (id) {
         res = await apiCall(`/admin/environments/${id}`, 'PUT', payload);
    } else {
         if (!api_key) { showToast('API Key required', 'error'); return; }
         payload.api_key = api_key;
         res = await apiCall('/admin/environments/', 'POST', payload);
    }

    if (res && res.ok) {
        showToast('Environment saved', 'success');
        document.getElementById('env_modal').close();
        loadEnvs();
    } else {
         showToast('Operation failed', 'error');
    }
}

async function deleteEnv(id) {
    if(!confirm('Delete this environment?')) return;
    const res = await apiCall(`/admin/environments/${id}`, 'DELETE');
    if(res && (res.ok || res.status === 204)) {
        loadEnvs();
    }
}


// --- Documents Logic ---
async function loadDocs() {
     const skip = (state.docs.page - 1) * state.docs.limit;
     const res = await apiCall(`/admin/documents/?skip=${skip}&limit=${state.docs.limit}`);
     
     if (res && res.ok) {
        const docs = await res.json();
        const statEl = document.getElementById('stat-docs');
        if (state.docs.page === 1 && statEl) statEl.innerText = docs.length + (docs.length === state.docs.limit ? '+' : '');
        
        const tbody = document.getElementById('docs-table-body');
        tbody.innerHTML = '';
        
        if (docs.length === 0 && state.docs.page > 1) {
             state.docs.page--;
             const el = document.getElementById(`page-info-docs`);
             if(el) el.innerText = `Page ${state.docs.page}`;
             await loadDocs();
             return;
        }

        docs.forEach((d, index) => {
            const no = (state.docs.page - 1) * state.docs.limit + index + 1;
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${no}</td>
                <td>${d.title}</td>
                <td>${new Date(d.created_at).toLocaleDateString()}</td>
                <td>
                    <button class="btn btn-xs btn-error" onclick="deleteDoc(${d.id})">Delete</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
     }
}

async function uploadDocument(e) {
    e.preventDefault();
    const fileInput = document.getElementById('pdf-file');
    if (!fileInput.files[0]) return;

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    showToast('Uploading & Indexing...', 'info');
    document.getElementById('upload-modal').close();

    const token = localStorage.getItem('token');
    const res = await fetch('/api/v1/admin/documents/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`
        },
        body: formData
    });

    if (res.ok) {
        showToast('File Processed Successfully', 'success');
        loadDocs();
    } else {
        const err = await res.json();
        showToast(`Error: ${err.detail || 'Upload failed'}`, 'error');
    }
}

async function deleteDoc(id) {
     if(!confirm('Delete this document? Embeddings will also be removed.')) return;
      const res = await apiCall(`/admin/documents/${id}`, 'DELETE');
      if (res && res.ok) {
          showToast('Document deleted', 'success');
          loadDocs();
      }
}


// --- Base Knowledge Logic ---
async function loadKnowledge() {
    const tbody = document.getElementById('knowledge-table-body');
    if(!tbody) return;

    try {
        const skip = (state.knowledge.page - 1) * state.knowledge.limit;
        const res = await apiCall(`/admin/base-knowledge/?skip=${skip}&limit=${state.knowledge.limit}`);
        
        if(res && res.ok) {
            const chunks = await res.json();
            
            tbody.innerHTML = '';
            if(chunks.length === 0) {
                 if (state.knowledge.page > 1) {
                     state.knowledge.page--;
                     const el = document.getElementById(`page-info-knowledge`);
                     if(el) el.innerText = `Page ${state.knowledge.page}`;
                     // Reload previous just in case
                     await loadKnowledge(); 
                     return;
                 }
                 tbody.innerHTML = '<tr><td colspan="3" class="text-center opacity-50">No knowledge chunks found.</td></tr>';
                 return;
            }

            chunks.forEach((chunk, index) => {
                const no = (state.knowledge.page - 1) * state.knowledge.limit + index + 1;
                const tr = document.createElement('tr');
                const contentPreview = truncate(chunk.content, 200);
                
                // Store content in a global or encoded way to avoid quote issues
                const safeContent = encodeURIComponent(chunk.content);

                tr.innerHTML = `
                    <td>${no}</td>
                    <td>${chunk.document_title || chunk.doc_id}</td>
                    <td class="text-xs whitespace-pre-wrap cursor-pointer hover:bg-base-200" title="Click to view full" onclick="viewKnowledge('${safeContent}')">${escapeHtml(contentPreview)}</td>
                    <td><button class="btn btn-xs btn-neutral" onclick="viewKnowledge('${safeContent}')">View</button></td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (e) {
        console.error('Error loading knowledge:', e);
        tbody.innerHTML = '<tr><td colspan="3" class="text-center text-error">Error loading data.</td></tr>';
    }
}

//Utils
function truncate(str, n){
  if(!str) return '';
  return (str.length > n) ? str.slice(0, n-1) + '...' : str;
}

function escapeHtml(text) {
  if (!text) return '';
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function unescapeHtml(text) {
     if (!text) return '';
      const doc = new DOMParser().parseFromString(text, "text/html");
      return doc.documentElement.textContent;
}

function viewKnowledge(encodedContent) {
    const content = decodeURIComponent(encodedContent);
    document.getElementById('knowledge-full-content').value = content;
    document.getElementById('knowledge_modal').showModal();
}
