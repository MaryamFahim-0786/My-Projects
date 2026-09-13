const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function handle(response) {
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail || detail;
    } catch {
      // response body wasn't JSON — fall back to statusText
    }
    throw new Error(detail);
  }
  return response.json();
}

export async function getTopHeadlines(category) {
  const params = new URLSearchParams();
  if (category && category !== "general") params.set("category", category);
  const res = await fetch(`${BASE_URL}/api/news/top?${params.toString()}`);
  return handle(res);
}

export async function searchNews(query) {
  const params = new URLSearchParams({ q: query });
  const res = await fetch(`${BASE_URL}/api/news/search?${params.toString()}`);
  return handle(res);
}

export async function summarizeArticle(title, content) {
  const res = await fetch(`${BASE_URL}/api/summarize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, content }),
  });
  return handle(res);
}

export async function sendChatMessage(message, history, articleContext) {
  const res = await fetch(`${BASE_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      history,
      article_context: articleContext || null,
    }),
  });
  return handle(res);
}
