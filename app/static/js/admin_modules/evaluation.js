import { state } from './state.js';
import { truncate, escapeHtml } from './utils.js';

// --- Questions Logic ---
export async function loadQuestions() {
    const tbody = document.getElementById('questions-table-body');
    if (!tbody) return;

    try {
        const res = await apiCall('/admin/evaluations/test-cases');
        if (res.ok) {
            const data = await res.json();
            // Data is list of RagTestCaseResponse
            if (!data || data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" class="text-center">No questions found.</td></tr>';
                return;
            }
             
            tbody.innerHTML = '';
            
            // Client-side pagination for simplicity as endpoint doesn't support pagination yet
            const start = (state.questions.page - 1) * state.questions.limit;
            const end = start + state.questions.limit;
            const pageData = data.slice(start, end);

            pageData.forEach((q) => {
                const tr = document.createElement('tr');
                // Escape needed for onclick arguments
                const safeQ = encodeURIComponent(q.question);
                const safeA = encodeURIComponent(q.reference_answer);
                
                tr.innerHTML = `
                    <td>${q.id}</td>
                    <td class="truncate max-w-[150px] md:max-w-xs text-xs" title="${escapeHtml(q.question)}">${escapeHtml(truncate(q.question, 50))}</td>
                    <td class="truncate max-w-[150px] md:max-w-xs text-xs" title="${escapeHtml(q.reference_answer)}">${escapeHtml(truncate(q.reference_answer, 50))}</td>
                    <td>
                        <button class="btn btn-xs btn-info" onclick="editQuestion(${q.id}, '${safeQ}', '${safeA}')">Edit</button>
                        <button class="btn btn-xs btn-error" onclick="deleteQuestion(${q.id})">Del</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch (e) {
        console.error('Error loading questions:', e);
        tbody.innerHTML = '<tr><td colspan="4" class="text-center text-error">Failed to load.</td></tr>';
    }
}

export function openAddQuestionModal() {
    document.getElementById('question-modal-title').innerText = 'Add Test Question';
    document.getElementById('question-id').value = '';
    document.getElementById('question-text').value = '';
    document.getElementById('question-reference').value = '';
    document.getElementById('question_add_modal').showModal();
}

export function editQuestion(id, safeQuestion, safeReference) {
    const question = decodeURIComponent(safeQuestion);
    const reference = decodeURIComponent(safeReference);
    
    document.getElementById('question-modal-title').innerText = 'Edit Test Question';
    document.getElementById('question-id').value = id;
    document.getElementById('question-text').value = question;
    document.getElementById('question-reference').value = reference;
    
    document.getElementById('question_add_modal').showModal();
}

export async function deleteQuestion(id) {
    if (!confirm('Are you sure you want to delete this test question?')) return;

    try {
        const res = await apiCall(`/admin/evaluations/test-cases/${id}`, 'DELETE');
        if (res.ok) {
            showToast('Question deleted successfully', 'success');
            loadQuestions();
        } else {
            showToast('Failed to delete question', 'error');
        }
    } catch (e) {
        showToast('Error deleting question', 'error');
    }
}

export async function saveQuestion(event) {
    if(event) event.preventDefault();
    const btn = event ? event.target : document.querySelector('#question_add_modal .btn-primary'); // Fallback
    const originalText = btn.innerText;
    btn.innerText = 'Saving...';
    btn.disabled = true;

    try {
        const id = document.getElementById('question-id').value;
        const question = document.getElementById('question-text').value;
        const reference = document.getElementById('question-reference').value;

        if (!question || !reference) {
            showToast('Question and Reference Answer are required!', 'error');
            return;
        }

        let res;
        if (id) {
            // Update
             res = await apiCall(`/admin/evaluations/test-cases/${id}`, 'PUT', {
                question, reference_answer: reference
            });
        } else {
            // Create
            res = await apiCall('/admin/evaluations/test-cases', 'POST', {
                question, reference_answer: reference
            });
        }

        if (res.ok) {
            showToast('Question saved successfully', 'success');
            document.getElementById('question_add_modal').close();
            loadQuestions();
        } else {
            showToast('Failed to save question', 'error');
        }
    } catch (e) {
        showToast('Error saving question', 'error');
    } finally {
        btn.innerText = originalText;
        btn.disabled = false;
    }
}

export async function importQuestions(event) {
    if(event) event.preventDefault();
    const btn = event ? event.target : document.querySelector('#question_import_modal .btn-primary');
    const originalText = btn.innerText;
    btn.innerText = 'Uploading...';
    btn.disabled = true;

    try {
        const fileInput = document.getElementById('question-csv-file');
        const file = fileInput.files[0];
        
        if (!file) {
            showToast('Please select a file', 'warning');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        // Need custom fetch for FormData content-type handling
        const token = localStorage.getItem('token');
        const res = await fetch('/api/v1/admin/evaluations/test-cases/import', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        if (res.ok) {
            const data = await res.json();
            showToast(data.message, 'success');
            document.getElementById('question_import_modal').close();
            loadQuestions();
        } else {
            const err = await res.json();
            showToast(err.detail || 'Import failed', 'error');
        }
    } catch (e) {
        console.error(e);
        showToast('Error importing file', 'error');
    } finally {
        btn.innerText = originalText;
        btn.disabled = false;
    }
}

// --- Generative Eval Logic ---
export async function loadGenerativeEval() {
    const tbody = document.getElementById('generative-eval-table-body');
    const selectRun = document.getElementById('eval-environment-select');
    const selectFilter = document.getElementById('filter-eval-env');
    const startDateFilter = document.getElementById('filter-eval-start-date');
    const endDateFilter = document.getElementById('filter-eval-end-date');
    
    if (!tbody) return;

    // Load Environments into Selects (Run & Filter)
    if ((selectRun && selectRun.options.length <= 1) || (selectFilter && selectFilter.options.length <= 1)) {
        try {
            const envRes = await apiCall('/admin/environments/');
            if (envRes.ok) {
                const envs = await envRes.json();
                 // Filter only chat models
                const chatEnvs = envs.filter(e => e.model_type === 'chat');
                
                // Clear existing options (except first) to avoid duplicates if partial load
                if(selectRun && selectRun.options.length <= 1) selectRun.innerHTML = '<option disabled selected>Select Models AI</option>';
                if(selectFilter && selectFilter.options.length <= 1) selectFilter.innerHTML = '<option value="">All Environments</option>';

                chatEnvs.forEach(env => {
                    // Populate Run Select
                    if(selectRun) {
                        const optRun = document.createElement('option');
                        optRun.value = env.id;
                        optRun.innerText = env.models_name || env.name;
                        selectRun.appendChild(optRun);
                    }

                    // Populate Filter Select
                    if(selectFilter) {
                        const optFilter = document.createElement('option');
                        optFilter.value = env.id;
                        optFilter.innerText = env.models_name || env.name;
                        selectFilter.appendChild(optFilter);
                    }
                });
            }
        } catch (e) {
            console.error('Failed to load envs for eval select', e);
        }
    }

    // Load Results with Filters
    try {
        let url = `/admin/evaluations/results_generative?limit=${state.generative.limit}`;
        
        // Ensure we check for non-empty string as value
        if (selectFilter && selectFilter.value !== "") {
            url += `&environment_id=${selectFilter.value}`;
        }
        
        if (startDateFilter && startDateFilter.value !== "") {
            url += `&start_date=${startDateFilter.value}`;
        }

        if (endDateFilter && endDateFilter.value !== "") {
            url += `&end_date=${endDateFilter.value}`;
        }

        const res = await apiCall(url);
        if (res.ok) {
            const data = await res.json();
            if (!data || data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" class="text-center">No evaluation results found for selected criteria.</td></tr>';
                return;
            }

            tbody.innerHTML = '';
            data.forEach(r => {
                const tr = document.createElement('tr');
                // Format score to 4 decimal places
                const bleu = r.bleu_score ? r.bleu_score.toFixed(4) : '0.0000';
                const rouge1 = r.rouge_1 ? r.rouge_1.toFixed(4) : '0.0000';
                const rougeL = r.rouge_l ? r.rouge_l.toFixed(4) : '0.0000';
                const date = new Date(r.created_at).toLocaleString();

                tr.innerHTML = `
                    <td class="whitespace-nowrap text-xs">${date}</td>
                    <td>${r.environment_name || r.environment_id}</td>
                    <td class="whitespace-nowrap max-w-[150px] truncate text-xs" title="${escapeHtml(r.question)}">${escapeHtml(truncate(r.question, 40)) || r.test_case_id}</td>
                    <td class="text-xs" title="${escapeHtml(r.model_answer)}">${escapeHtml(truncate(r.model_answer, 50))}</td>
                    <td class="font-mono text-xs">${bleu}</td>
                    <td class="font-mono text-xs">${rouge1}</td>
                    <td class="font-mono text-xs">${rougeL}</td>
                `;
                tbody.appendChild(tr);
            });
        }
    } catch(e) {
        console.error("Error loading eval results", e);
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-error">Failed to load results.</td></tr>';
    }
}

export async function runGenerativeEval() {
    const select = document.getElementById('eval-environment-select');
    const envId = select.value;
    const envName = select.options[select.selectedIndex].innerText;

    if (!envId || envId === 'Select Models AI' || envId === 'Select Environment') {
        showToast('Please select "Models AI" first', 'warning');
        return;
    }

    try {
        // 1. Fetch all test cases to show in modal
        const res = await apiCall('/admin/evaluations/test-cases');
        if (!res.ok) throw new Error('Failed to fetch test cases');
        
        const testCases = await res.json();
        if (testCases.length === 0) {
            showToast('No test cases found. Please add questions first.', 'warning');
            return;
        }

        // 2. Populate Modal
        const tbody = document.getElementById('eval-confirm-table-body');
        document.getElementById('eval-confirm-model-name').innerText = envName;
        tbody.innerHTML = '';

        testCases.forEach((tc, idx) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${idx + 1}</td>
                <td class="text-xs break-words max-w-sm">${escapeHtml(tc.question)}</td>
                <td class="text-xs break-words max-w-sm text-opacity-70">${escapeHtml(truncate(tc.reference_answer, 100))}</td>
            `;
            tbody.appendChild(tr);
        });

        // 3. Show Modal using standard dialog API
        // Close previously opened modal if any (using form method="dialog" automatically handles close, 
        // but we need to ensure the Confirm button triggers the actual run)
        
        // We attach the envId to the modal for the confirm function to use
        const modal = document.getElementById('eval_confirm_modal');
        modal.dataset.envId = envId;
        modal.showModal();

    } catch (e) {
        console.error(e);
        showToast('Error preparing evaluation', 'error');
    }
}

export async function confirmRunGenerativeEval(event) {
    if(event) event.preventDefault(); // Prevent form submission closing immediatelly if not handled
    
    const modal = document.getElementById('eval_confirm_modal');
    const envId = modal.dataset.envId;
    
    modal.close(); // Close the reviewing modal

    // SweetAlert Confirmation
    const result = await Swal.fire({
        title: 'Start Evaluation?',
        text: "This process may take some time depending on the number of questions.",
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Yes, start it!'
    });

    if (!result.isConfirmed) return;

    try {
        const res = await apiCall('/admin/evaluations/run_generative', 'POST', {
            environment_id: parseInt(envId),
            limit: null // Run all
        });

        if (res.ok) {
            showToast('Evaluation started in background. Refresh in a few moments.', 'success');
            setTimeout(loadGenerativeEval, 5000);
        } else {
            showToast('Failed to start evaluation', 'error');
        }
    } catch (e) {
        showToast('Error starting evaluation', 'error');
    }
}
