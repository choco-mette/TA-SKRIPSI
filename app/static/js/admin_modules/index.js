import { state, updatePage } from './state.js';
import * as Rules from './rules.js';
import * as Personality from './personality.js';
import * as Environments from './environments.js';
import * as Docs from './documents.js';
import * as Knowledge from './knowledge.js';
import * as Evaluation from './evaluation.js';

// Expose functions to global scope for HTML event handlers
window.editRule = Rules.editRule;
window.deleteRule = Rules.deleteRule;
window.saveRule = Rules.saveRule;
window.openRuleModal = Rules.openRuleModal;

window.savePersonality = Personality.savePersonality;

window.editEnv = Environments.editEnv;
window.deleteEnv = Environments.deleteEnv;
window.saveEnv = Environments.saveEnv;
window.openEnvModal = Environments.openEnvModal;

window.deleteDoc = Docs.deleteDoc;
window.uploadDocument = Docs.uploadDocument;

window.viewKnowledge = Knowledge.viewKnowledge;

window.editQuestion = Evaluation.editQuestion;
window.deleteQuestion = Evaluation.deleteQuestion;
window.saveQuestion = Evaluation.saveQuestion;
window.openAddQuestionModal = Evaluation.openAddQuestionModal;
window.importQuestions = Evaluation.importQuestions;
window.runGenerativeEval = Evaluation.runGenerativeEval;
window.confirmRunGenerativeEval = Evaluation.confirmRunGenerativeEval;
window.loadGenerativeEval = Evaluation.loadGenerativeEval;
window.viewEvalDetail = Evaluation.viewEvalDetail;
window.loadEvaluationDashboard = Evaluation.loadEvaluationDashboard;

// Navigation & Initialization

document.addEventListener('DOMContentLoaded', async () => {
    // Auth Check
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

    // Navigation assignment to window
    window.showSection = showSection;
    window.toggleSidebar = toggleSidebar; // Already in HTML but good to have if moved
    window.nextPage = nextPage;
    window.prevPage = prevPage;
    window.refreshAll = refreshAll;

    // Initial Load based on URL or Default
    const initial = window.initialSection || 'overview';
    showSection(initial, false);

    // Initial Data Fetch
    await refreshAll();
    
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
        // Only push if different from current
        const currentPath = window.location.pathname;
        const newPath = sectionId === 'overview' ? '/admin' : `/admin/${sectionId}`;
        
        if (currentPath !== newPath) {
             history.pushState({ section: sectionId }, '', newPath);
        }
    }
}

async function refreshAll() {
    await Rules.loadRules();
    await Personality.loadPersonality();
    await Environments.loadEnvs();
    await Docs.loadDocs();
    await Knowledge.loadKnowledge();
    await Evaluation.loadQuestions();
    await Evaluation.loadGenerativeEval();
    await Evaluation.loadEvaluationDashboard();
}

async function nextPage(type) {
    state[type].page++;
    updatePage(type, state[type].page);
    await reloadByType(type);
}

async function prevPage(type) {
    if (state[type].page > 1) {
        state[type].page--;
        updatePage(type, state[type].page);
        await reloadByType(type);
    }
}

async function reloadByType(type) {
    if (type === 'rules') await Rules.loadRules();
    if (type === 'envs') await Environments.loadEnvs();
    if (type === 'docs') await Docs.loadDocs();
    if (type === 'knowledge') await Knowledge.loadKnowledge();
    if (type === 'questions') await Evaluation.loadQuestions();
    if (type === 'generative') await Evaluation.loadGenerativeEval();
    if (type === 'eval-dashboard') await Evaluation.loadEvaluationDashboard();
}

// Global Auth Helper (assuming isAuthenticated is global from http.js, but if not:)
function isAuthenticated() {
    // If http.js defines this globally, we are good. 
    // Otherwise check token existence.
    return !!localStorage.getItem('token');
}

// Ensure toggleSidebar is available (it was inline script in HTML, but we might want it here)
function toggleSidebar() {
    const drawer = document.getElementById('main-drawer');
    // ... logic is in HTML currently, keeping it there to avoid conflict or need to move it.
}
