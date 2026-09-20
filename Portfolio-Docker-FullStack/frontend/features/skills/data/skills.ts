import { Code2, Database, Wrench, Layers } from "lucide-react"

export const skills = [
    {
        category: "Programming Languages",
        icon: Code2,
        color: "from-slate-400 to-slate-500",
        items: [
            { name: "Python" },
            { name: "JavaScript" },
            { name: "TypeScript" },
            { name: "Java" },
            { name: "C++" },
            { name: "SQL" },
        ],
    },
    {
        category: "AI & LLM Engineering",
        icon: Layers,
        color: "from-zinc-400 to-zinc-500",
        items: [
            { name: "LangChain" },
            { name: "LangGraph" },
            { name: "RAG" },
            { name: "Gemini" },
            { name: "OpenAI" },
            { name: "Groq" },
        ],
    },
    {
        category: "Web & Backend",
        icon: Wrench,
        color: "from-neutral-400 to-neutral-500",
        items: [
            { name: "FastAPI" },
            { name: "Flask" },
            { name: "React" },
            { name: "Next.js" },
            { name: "Node.js" },
            { name: "Tailwind CSS" },
        ],
    },
    {
        category: "Databases & Tools",
        icon: Database,
        color: "from-gray-400 to-gray-500",
        items: [
            { name: "PostgreSQL" },
            { name: "pgvector" },
            { name: "ChromaDB" },
            { name: "SQLite" },
            { name: "MongoDB" },
            { name: "Docker" },
            { name: "Git & GitHub" },
        ],
    },
]
