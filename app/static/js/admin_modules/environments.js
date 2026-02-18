import { state } from './state.js';

export async function loadEnvs() {
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

export function openEnvModal() {
    document.getElementById('env-id').value = '';
    document.getElementById('env-name').value = '';
    document.getElementById('env-key').value = '';
    document.getElementById('env-url').value = '';
    document.getElementById('env-type').value = 'chat';
    document.getElementById('env-active').checked = false;
    document.getElementById('env-modal-title').innerText = 'Add Environment';
    document.getElementById('env_modal').showModal();
}

export function editEnv(id, name, url, type, active) {
    document.getElementById('env-id').value = id;
    document.getElementById('env-name').value = name;
    document.getElementById('env-url').value = url;
    document.getElementById('env-key').value = ''; 
    document.getElementById('env-type').value = type;
    document.getElementById('env-active').checked = active;
    document.getElementById('env-modal-title').innerText = 'Edit Environment';
    document.getElementById('env_modal').showModal();
}

export async function saveEnv(e) {
    if(e) e.preventDefault();
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

export async function deleteEnv(id) {
    const result = await Swal.fire({
        title: 'Delete Environment?',
        text: "This variable will be permanently removed.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        confirmButtonText: 'Yes, delete it!'
    });

    if (!result.isConfirmed) return;

    const res = await apiCall(`/admin/environments/${id}`, 'DELETE');
    if(res && (res.ok || res.status === 204)) {
        loadEnvs();
    }
}
