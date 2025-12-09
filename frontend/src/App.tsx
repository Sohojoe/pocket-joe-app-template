import { useState } from "react";
import { sayHello, HelloResponse, ApiError } from "./api";

export default function App() {
  const [input, setInput] = useState("");
  const [response, setResponse] = useState<HelloResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const data = await sayHello(input);
      setResponse(data);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(`Error ${err.status}: ${err.statusText}`);
      } else {
        setError("Failed to connect to API");
      }
      setResponse(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900 text-white p-6">
      <div className="max-w-md w-full bg-slate-800 p-6 rounded-xl shadow-lg space-y-4">
        <h1 className="text-2xl font-bold">Pocket Joe App Template</h1>

        <form onSubmit={handleSubmit} className="space-y-3">
          <input
            className="w-full p-2 rounded bg-slate-700 border border-slate-600 focus:border-emerald-500 focus:outline-none"
            placeholder="Type something…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-emerald-500 hover:bg-emerald-600 disabled:bg-emerald-800 text-black py-2 rounded font-semibold transition-colors"
          >
            {loading ? "Loading…" : "Say Hello"}
          </button>
        </form>

        {error && (
          <div className="mt-4 p-4 bg-red-900/50 border border-red-700 rounded text-red-200">
            {error}
          </div>
        )}

        {response && (
          <div className="mt-4 p-4 bg-slate-700 rounded">
            {response.greeting}
          </div>
        )}
      </div>
    </div>
  );
}
