export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen max-w-3xl flex-col justify-center px-6 py-16 sm:px-10">
      <p className="mb-5 text-sm font-semibold uppercase tracking-widest text-emerald-800">
        Electronics review analysis
      </p>
      <h1 className="text-4xl font-semibold tracking-tight sm:text-6xl">ReviewTrust</h1>
      <p className="mt-6 max-w-xl text-lg leading-8 text-slate-700">
        Understand the patterns behind product reviews, with evidence you can inspect.
      </p>
      <section aria-labelledby="development-status" className="mt-10 rounded-2xl border border-emerald-900/15 bg-white p-6 sm:p-8">
        <h2 id="development-status" className="text-xl font-semibold">In development</h2>
        <p className="mt-3 leading-7 text-slate-700">
          The project foundation is ready. Review submission and analysis are not available yet.
        </p>
        <p className="mt-4 border-t border-slate-200 pt-4 text-sm leading-6 text-slate-600">
          ReviewTrust detects observable patterns, not proven deception. A Trust Score will not
          verify authenticity or measure product quality.
        </p>
      </section>
    </main>
  );
}
