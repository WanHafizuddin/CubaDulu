import { useState } from "react";

type Message = { role: "user" | "assistant"; content: string };

export default function ChatPanel({ unitId }: { unitId: string }) {
  const [history, setHistory] = useState<Message[]>([]);
  const [input, setInput] = useState("");

  async function send() {
    // TODO: POST /units/{unitId}/chat { message: input, history }
    void unitId;
    void setHistory;
  }

  return (
    <div className="border rounded p-4 flex flex-col gap-2">
      <h3 className="font-semibold">Ask this unit</h3>
      <div className="flex-1 overflow-y-auto text-sm">
        {history.map((m, i) => (
          <p key={i}>
            <strong>{m.role}:</strong> {m.content}
          </p>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          className="flex-1 border rounded px-2"
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button type="button" onClick={send}>
          Send
        </button>
      </div>
    </div>
  );
}
