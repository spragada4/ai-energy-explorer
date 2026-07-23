// frontend/app/page.tsx
import Link from "next/link";

export default function Home() {
  return (
    <main className="flex flex-col items-center justify-center min-h-screen px-8 text-center">
      <h1 className="text-3xl font-semibold mb-4">AI Energy Efficiency Explorer</h1>
      <p className="max-w-md text-zinc-600 mb-8">
        A small ML-powered dashboard exploring how much energy AI inference
        actually costs, trained on real public data from Epoch AI, Google, and
        academic energy-benchmarking research.
      </p>
      <Link
        href="/estimator"
        className="bg-black text-white rounded px-6 py-3 font-medium"
      >
        Try the energy estimator →
      </Link>
    </main>
  );
}