import type { ProjectItem } from "@/features/projects/components/projects-carousel";

export const projects: ProjectItem[] = [
    {
        id: 1,
        title: "Meridian - Gemini Chatbot",
        category: "Full-Stack Generative AI",
        description:
            "A production-style Gemini chatbot with per-user document RAG, persistent memory, a tool-calling agent (web search, calculator) and JWT authentication.",
        techStack: ["Next.js", "FastAPI", "LangChain", "pgvector"],
        github: "https://github.com/MaryamFahim-0786/My-Projects/tree/main/meridian-gemini-chatbot",
        image: "/images/projects/meridian-chatbot.webp",
    },
    {
        id: 2,
        title: "AI Weather Platform",
        category: "AI + Full-Stack Web App",
        description:
            "Live weather, hourly and 7-day forecasts with an interactive map, plus a LangGraph agent that works out which city you mean and answers from fresh data.",
        techStack: ["FastAPI", "LangGraph", "Next.js", "Leaflet"],
        github: "https://github.com/MaryamFahim-0786/My-Projects/tree/main/AI-Weather-Platform",
        image: "/images/projects/ai-weather.webp",
    },
    {
        id: 3,
        title: "Crypto AI Assistant",
        category: "AI Dashboard + Desktop App",
        description:
            "Live crypto dashboard with price cards and history charts, and a LangChain agent with live-price, compare and trend tools. Ships as an Electron desktop app.",
        techStack: ["Flask", "LangChain", "Next.js", "Electron"],
        github: "https://github.com/MaryamFahim-0786/My-Projects/tree/main/Crypto-AI-Assistant",
        image: "/images/projects/crypto-assistant.webp",
    },
    {
        id: 4,
        title: "Maryam's News",
        category: "AI News Assistant",
        description:
            "Live headlines by category with one-click AI summaries and an \"AI Briefing\" chat panel for asking questions about the news.",
        techStack: ["FastAPI", "Gemini", "NewsAPI", "React (Vite)"],
        github: "https://github.com/MaryamFahim-0786/My-Projects/tree/main/Maryams-News-Chatbot",
        image: "/images/projects/marys-news.webp",
    },
    {
        id: 5,
        title: "Simple RAG Chatbot",
        category: "Retrieval-Augmented Generation",
        description:
            "Upload PDF, DOCX, TXT, MD or CSV files and chat with them. Uses pgvector similarity search, cites the chunks it used and keeps session history in Postgres.",
        techStack: ["FastAPI", "Gemini", "PostgreSQL", "pgvector"],
        github: "https://github.com/MaryamFahim-0786/My-Projects/tree/main/Simple-RAG-Chatbot",
        image: "/images/projects/simple-rag.webp",
    },
    {
        id: 6,
        title: "RAG Chatbot (CLI)",
        category: "Retrieval-Augmented Generation",
        description:
            "A modular, well-documented RAG pipeline: load documents, chunk, embed into ChromaDB and answer with grounded context from an interactive command line.",
        techStack: ["Python", "LangChain", "ChromaDB", "OpenAI"],
        github: "https://github.com/MaryamFahim-0786/My-Projects/tree/main/RAG-Chatbot",
        image: "/images/projects/rag-chatbot.webp",
    },
    {
        id: 7,
        title: "Bank Management System",
        category: "Python Desktop + CLI App",
        description:
            "Secure banking system with admin and customer portals, PBKDF2 password hashing, exact Decimal arithmetic, atomic transfers with rollback, CSV reports and tests.",
        techStack: ["Python", "SQLite", "Tkinter", "OOP"],
        github: "https://github.com/MaryamFahim-0786/My-Projects/tree/main/Bank-Management-System",
        image: "/images/projects/bank-system.webp",
    },
    {
        id: 8,
        title: "Library Management System",
        category: "Python CLI App",
        description:
            "Books, members, borrowing, returns, reservations and overdue fines through a structured terminal interface, with reports and CSV export.",
        techStack: ["Python", "SQLite", "OOP", "CSV"],
        github: "https://github.com/MaryamFahim-0786/My-Projects/tree/main/Library-Management-System",
        image: "/images/projects/library-system.webp",
    },
    {
        id: 9,
        title: "Car Rental System",
        category: "Python Desktop App",
        description:
            "Fleet management, booking, late-fee calculation, invoices, a payment ledger and revenue analytics with role-based access.",
        techStack: ["Python", "Tkinter", "SQLite", "OOP"],
        github: "https://github.com/MaryamFahim-0786/My-Projects/tree/main/Maryam-Fahim-Car-Rental-System",
        image: "/images/projects/car-rental.webp",
    },
    {
        id: 10,
        title: "AI Portfolio Assistant",
        category: "Full-Stack Generative AI",
        description:
            "This site: a RAG-powered chat portfolio. Adapted from an open-source template by Roy Amit and customised with my own knowledge base, prompt and branding.",
        techStack: ["FastAPI", "Next.js", "LangChain", "pgvector"],
        github: "https://github.com/MaryamFahim-0786/My-Projects",
        image: "/images/projects/ai-portfolio.webp",
    },
];
