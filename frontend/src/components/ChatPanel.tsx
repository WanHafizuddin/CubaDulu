import { useState } from "react";
import { chatWithUnit, type ChatMessage } from "../lib/api";

export default function ChatPanel({ unitId }: { unitId: string }) {
  const [history, setHistory] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function send() {
    const message = input.trim();
    if (!message || loading) return;
    setInput("");
    setError(null);
    const nextHistory = [...history, { role: "user" as const, content: message }];
    setHistory(nextHistory);
    setLoading(true);
    try {
      const { answer } = await chatWithUnit(unitId, message, history);
      setHistory([...nextHistory, { role: "assistant", content: answer }]);
    } catch (err) {
      setError(String(err instanceof Error ? err.message : err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="border rounded p-4 flex flex-col gap-2">
      <h3 className="font-semibold">Ask this unit</h3>
      <div className="flex-1 overflow-y-auto text-sm flex flex-col gap-1">
        {history.map((m, i) => (
          <p key={i}>
            <strong>{m.role === "user" ? "You" : "Unit"}:</strong> {m.content}
          </p>
        ))}
        {loading && <p className="text-gray-400">Thinking…</p>}
      </div>
      {error && <p className="text-xs text-red-600">{error}</p>}
      <div className="flex gap-2">
        <input
          className="flex-1 border rounded px-2"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          disabled={loading}
        />
        <button type="button" onClick={send} disabled={loading || !input.trim()}>
          Send
        </button>
      </div>
    </div>
  );
}
