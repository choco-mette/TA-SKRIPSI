export const state = {
    rules: { page: 1, limit: 10 },
    envs: { page: 1, limit: 10 },
    docs: { page: 1, limit: 10 },
    knowledge: { page: 1, limit: 10 },
    questions: { page: 1, limit: 10 },
    generative: { page: 1, limit: 100 }
};

export function updatePage(type, newPage) {
    state[type].page = newPage;
    updatePageInfo(type);
}

export function updatePageInfo(type) {
    const el = document.getElementById(`page-info-${type}`);
    if(el) el.innerText = `Page ${state[type].page}`;
}
