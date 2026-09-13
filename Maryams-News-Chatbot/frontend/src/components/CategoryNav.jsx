const CATEGORIES = [
  { id: "general", label: "Top Stories" },
  { id: "business", label: "Business" },
  { id: "technology", label: "Technology" },
  { id: "sports", label: "Sports" },
  { id: "health", label: "Health" },
  { id: "science", label: "Science" },
  { id: "entertainment", label: "Entertainment" },
];

export default function CategoryNav({ active, onChange, disabled }) {
  return (
    <nav className="category-nav">
      {CATEGORIES.map((c) => (
        <button
          key={c.id}
          className={c.id === active ? "active" : ""}
          onClick={() => onChange(c.id)}
          disabled={disabled}
        >
          {c.label}
        </button>
      ))}
    </nav>
  );
}
