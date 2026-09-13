import { useState } from "react";

const TODAY = new Date().toLocaleDateString(undefined, {
  weekday: "long",
  year: "numeric",
  month: "long",
  day: "numeric",
});

export default function Masthead({ onSearch, activeQuery, onClearSearch }) {
  const [value, setValue] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    if (value.trim()) onSearch(value.trim());
  }

  return (
    <header className="masthead">
      <div className="masthead-top">
        <div>
          <div className="masthead-date">{TODAY}</div>
          <h1 className="masthead-title">
            Maryam's <em>News</em>
          </h1>
          <p className="masthead-tagline">
            Live headlines, read alongside an AI briefing that explains what matters.
          </p>
        </div>
      </div>

      <form className="search-form" onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Search today's coverage…"
          value={value}
          onChange={(e) => setValue(e.target.value)}
        />
        <button type="submit" aria-label="Search">
          Search
        </button>
      </form>

      {activeQuery && (
        <div className="search-active-note">
          Showing results for “{activeQuery}”
          <button onClick={onClearSearch}>Clear</button>
        </div>
      )}
    </header>
  );
}
