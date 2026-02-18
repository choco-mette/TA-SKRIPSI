import { state } from './state.js';
import { truncate, escapeHtml, unescapeHtml } from './utils.js';

export async function loadRules() {
    const tableBody = document.getElementById('rules-table-body');
    if (!tableBody) return;

    const skip = (state.rules.page - 1) * state.rules.limit;
    
    // apiCall is from http.js (global)
    const res = await apiCall(`/admin/rules/?skip=${skip}&limit=${state.rules.limit}`);
    
    if(res && res.ok) {
        const rules = await res.json();
        const statEl = document.getElementById('stat-rules');
        if (state.rules.page === 1 && statEl) statEl.innerText = rules.length + (rules.length === state.rules.limit ? '+' : '');
        
        tableBody.innerHTML = '';
        
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
            tableBody.appendChild(tr);
        });
    }
}

export function openRuleModal() {
    document.getElementById('rule-id').value = '';
    document.getElementById('rule-content').value = '';
    document.getElementById('rule-active').checked = true;
    document.getElementById('rule-modal-title').innerText = 'Add New Rule';
    document.getElementById('rule_modal').showModal();
}

export async function editRule(id, content, isActive) {
    document.getElementById('rule-id').value = id;
    document.getElementById('rule-content').value = unescapeHtml(content);
    document.getElementById('rule-active').checked = isActive;
    document.getElementById('rule-modal-title').innerText = 'Edit Rule';
    document.getElementById('rule_modal').showModal();
}

export async function saveRule(e) {
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

export async function deleteRule(id) {
    const result = await Swal.fire({
        title: 'Delete Rule?',
        text: "This action cannot be undone.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        confirmButtonText: 'Yes, delete it!'
    });
    
    if (!result.isConfirmed) return;

    const res = await apiCall(`/admin/rules/${id}`, 'DELETE');
    if (res && (res.ok || res.status === 204)) {
        showToast('Rule deleted', 'success');
        loadRules();
    }
}
