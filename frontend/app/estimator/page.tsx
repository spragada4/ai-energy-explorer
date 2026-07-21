// frontend/app/estimator/page.tsx
"use client";

import { useState } from "react";

const ORGANIZATIONS = ["OpenAI", "Anthropic", "Google DeepMind", "Meta AI", "DeepSeek"];

type PredictResponse = {
  estimated_wh: number;
  model_version: string;
  confidence_note: string;
};

export default function EstimatorPage() {
  const [organization, setOrganization] = useState("OpenAI");
  const [inputTokens, setInputTokens] = useState(100);
  const [outputTokens, setOutputTokens] = useState(300);
  const [isLongPrompt, setIsLongPrompt] = useState(false);
  const [isReasoning, setIsReasoning] = useState(false);
  const [result, setResult] = useState<PredictResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/predict/energy`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          organization,
          input_tokens: inputTokens,
          output_tokens: outputTokens,
          is_long_prompt: isLongPrompt,
          is_reasoning_or_heavy: isReasoning,
        }),
      });

      if (!res.ok) {
        const body = await res.json();
        throw new Error(body.detail || "Request failed");
      }

      setResult(await res.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="max-w-xl mx-auto p-8">
      <h1 className="text-2xl font-semibold mb-6">Energy Estimator</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Organization</label>
          <select
            value={organization}
            onChange={(e) => setOrganization(e.target.value)}
            className="w-full border rounded px-3 py-2"
          >
            {ORGANIZATIONS.map((org) => (
              <option key={org} value={org}>{org}</option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Input tokens</label>
            <input
              type="number"
              value={inputTokens}
              onChange={(e) => setInputTokens(Number(e.target.value))}
              className="w-full border rounded px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Output tokens</label>
            <input
              type="number"
              value={outputTokens}
              onChange={(e) => setOutputTokens(Number(e.target.value))}
              className="w-full border rounded px-3 py-2"
            />
          </div>
        </div>

        <label className="flex items-center gap-2">
          <input type="checkbox" checked={isLongPrompt} onChange={(e) => setIsLongPrompt(e.target.checked)} />
          <span className="text-sm">Long prompt (10k+ input tokens)</span>
        </label>

        <label className="flex items-center gap-2">
          <input type="checkbox" checked={isReasoning} onChange={(e) => setIsReasoning(e.target.checked)} />
          <span className="text-sm">Reasoning / extended-thinking model</span>
        </label>

        <button
          type="submit"
          disabled={loading}
          className="bg-black text-white rounded px-4 py-2 disabled:opacity-50"
        >
          {loading ? "Estimating..." : "Estimate energy"}
        </button>
      </form>

      {error && (
        <p className="mt-6 text-red-600 text-sm">{error}</p>
      )}

      {result && (
        <div className="mt-6 p-4 border rounded bg-gray-50">
          <p className="text-3xl font-semibold">{result.estimated_wh} Wh</p>
          <p className="text-sm text-gray-600 mt-1">{result.confidence_note}</p>
          <p className="text-xs text-gray-400 mt-2">Model: {result.model_version}</p>
        </div>
      )}
    </main>
  );
}