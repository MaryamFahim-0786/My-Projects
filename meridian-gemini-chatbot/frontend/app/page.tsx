import Link from "next/link";

const capabilities = [
  {
    label: "Reads what you give it",
    body: "Upload contracts, notes, or research. Meridian indexes them and answers from your own material instead of guessing.",
  },
  {
    label: "Remembers the thread",
    body: "Every conversation carries its own memory, so you can pick a thought back up next week without repeating yourself.",
  },
  {
    label: "Reaches beyond the chat",
    body: "When the answer isn't in your documents, it can search the live web or run a calculation before it replies.",
  },
];

export default function LandingPage() {
  return (
    <main className="min-h-screen">
      <nav className="flex items-center justify-between px-8 py-6 border-b border-line">
        <span className="font-display italic text-xl tracking-tight">Meridian</span>
        <div className="flex gap-6 text-sm text-muted">
          <Link href="/login" className="hover:text-paper transition-colors">
            Log in
          </Link>
          <Link
            href="/signup"
            className="text-paper border border-line px-4 py-1.5 rounded hover:border-signal hover:text-signal transition-colors"
          >
            Sign up
          </Link>
        </div>
      </nav>

      <section className="px-8 pt-24 pb-20 max-w-3xl">
        <p className="text-beacon text-sm tracking-wide mb-4">A private line to Gemini</p>
        <h1 className="font-display text-5xl md:text-6xl leading-[1.1] mb-6">
          Ask everything you know,
          <br />
          <span className="italic text-muted">and some things you don&apos;t.</span>
        </h1>
        <p className="text-muted text-lg max-w-xl mb-10">
          Meridian pairs Google Gemini with your own documents, a memory that persists across
          sessions, and the ability to act — not just answer.
        </p>
        <Link
          href="/signup"
          className="inline-block bg-signal text-white px-6 py-3 rounded font-medium hover:opacity-90 transition-opacity"
        >
          Start a conversation
        </Link>
      </section>

      <section className="border-t border-line">
        <div className="grid md:grid-cols-3">
          {capabilities.map((item, i) => (
            <div
              key={item.label}
              className={`px-8 py-14 ${i > 0 ? "md:border-l border-line" : ""}`}
            >
              <h3 className="font-display italic text-xl mb-3">{item.label}</h3>
              <p className="text-muted text-sm leading-relaxed">{item.body}</p>
            </div>
          ))}
        </div>
      </section>

      <footer className="px-8 py-8 border-t border-line text-xs text-muted">
        Built on Gemini, LangChain, and Postgres — your data stays scoped to your account.
      </footer>
    </main>
  );
}
