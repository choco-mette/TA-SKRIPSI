import { state } from './state.js';

export async function loadDocs() {
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

export async function uploadDocument(e) {
    if(e) e.preventDefault();
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

export async function deleteDoc(id) {
     const result = await Swal.fire({
        title: 'Delete Document?',
        text: "Embeddings will also be removed. This cannot be undone.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        confirmButtonText: 'Yes, delete it!'
     });

     if (!result.isConfirmed) return;

      const res = await apiCall(`/admin/documents/${id}`, 'DELETE');
      if (res && res.ok) {
          showToast('Document deleted', 'success');
          loadDocs();
      }
}
