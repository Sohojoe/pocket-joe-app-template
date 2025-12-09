// In production, API is served from same origin
// In development, Vite dev server runs on :5173, API on :8000
const API_BASE = import.meta.env.VITE_API_BASE_URL ??
  (import.meta.env.DEV ? "http://localhost:8000" : "");

export type HelloResponse = { greeting: string };

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public statusText: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function sayHello(text?: string): Promise<HelloResponse> {
  const params = new URLSearchParams();
  if (text) params.set("text", text);

  const url = `${API_BASE}/api/hello?${params.toString()}`;
  const res = await fetch(url);

  if (!res.ok) {
    throw new ApiError(
      `API request failed: ${res.status} ${res.statusText}`,
      res.status,
      res.statusText
    );
  }

  return res.json();
}
