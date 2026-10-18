import { useState } from "react";

export default function MatchPage() {
  const [description, setDescription] = useState("");

  async function handleSubmit() {
    // TODO: POST /match { description }, render ranked units with explanations
  }

  return (
    <div className="max-w-xl mx-auto p-4">
      <h1 className="text-2xl font-semibold mb-4">Describe your life</h1>
      <textarea
        className="w-full border rounded p-2"
        rows={5}
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="e.g. I work in KL, have two kids in primary school, hate the heat..."
      />
      <button
        type="button"
        className="mt-4 px-4 py-2 rounded bg-black text-white"
        onClick={handleSubmit}
      >
        Find my fit
      </button>
    </div>
  );
}
