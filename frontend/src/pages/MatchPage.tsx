import { useState } from "react";
import { Link } from "react-router-dom";
import { matchUnits, type MatchResult } from "../lib/api";

export default function MatchPage() {
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<MatchResult | null>(null);

  async function handleSubmit() {
    if (!description.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      setResult(await matchUnits(description));
    } catch (err) {
      setError(String(err instanceof Error ? err.message : err));
    } finally {
      setLoading(false);
    }
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
        className="mt-4 px-4 py-2 rounded bg-black text-white disabled:opacity-50"
        onClick={handleSubmit}
        disabled={loading || !description.trim()}
      >
        {loading ? "Thinking…" : "Find my fit"}
      </button>

      {error && <p className="mt-4 text-sm text-red-600">{error}</p>}

      {result && (
        <div className="mt-6 flex flex-col gap-4">
          {result.results.length === 0 && (
            <p className="text-sm text-gray-500">No units matched your budget or criteria.</p>
          )}
          {result.results.map((r) => (
            <div key={r.unit_id} className="border rounded p-4">
              <div className="flex items-center justify-between">
                <h2 className="font-semibold">{r.unit_id}</h2>
                <Link to={`/units/${r.unit_id}`} className="text-sm underline">
                  View unit
                </Link>
              </div>
              <p className="text-sm text-gray-600 mt-1">{r.explanation}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
