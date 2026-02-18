export async function loadPersonality() {
    const res = await apiCall('/admin/personality/');
    if(res && res.ok) {
        const data = await res.json();
        const p = Array.isArray(data) ? data[0] : data;
        if (p) {
             document.getElementById('personality-input').value = p.content;
        }
    }
}

export async function savePersonality() {
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
