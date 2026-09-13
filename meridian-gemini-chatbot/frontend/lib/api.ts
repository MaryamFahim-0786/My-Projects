import Cookies from "js-cookie";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

async function request(path: string, options: RequestInit = {}) {
  const token = Cookies.get("access_token");

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      ...(options.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || "Request failed");
  }
  return res.json();
}

export const api = {
  signup: (email: string, password: string, full_name?: string) =>
    request("/auth/signup", { method: "POST", body: JSON.stringify({ email, password, full_name }) }),

  login: (email: string, password: string) =>
    request("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),

  me: () => request("/auth/me"),

  sendMessage: (message: string, conversation_id?: string, use_rag = true, use_tools = true) =>
    request("/chat/", {
      method: "POST",
      body: JSON.stringify({ message, conversation_id, use_rag, use_tools }),
    }),

  listConversations: () => request("/chat/conversations"),

  getMessages: (conversationId: string) => request(`/chat/conversations/${conversationId}/messages`),

  listDocuments: () => request("/documents/"),

  uploadDocument: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return request("/documents/upload", { method: "POST", body: formData });
  },
};
