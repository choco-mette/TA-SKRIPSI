export function truncate(str, n){
  if(!str) return '';
  return (str.length > n) ? str.slice(0, n-1) + '...' : str;
}

export function escapeHtml(text) {
  if (!text) return '';
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

export function unescapeHtml(text) {
     if (!text) return '';
      const doc = new DOMParser().parseFromString(text, "text/html");
      return doc.documentElement.textContent;
}
