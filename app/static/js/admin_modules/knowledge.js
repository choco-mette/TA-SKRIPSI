import { state } from './state.js';
import { truncate, escapeHtml } from './utils.js';

export async function loadKnowledge() {
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

export function viewKnowledge(encodedContent) {
    const content = decodeURIComponent(encodedContent);
    document.getElementById('knowledge-full-content').value = content;
    document.getElementById('knowledge_modal').showModal();
}
