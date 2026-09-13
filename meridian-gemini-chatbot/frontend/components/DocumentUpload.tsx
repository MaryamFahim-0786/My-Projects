"use client";

import { useRef, useState } from "react";
import { api } from "@/lib/api";

export function DocumentUpload() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [lastUploaded, setLastUploaded] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleFile(file: File) {
    setUploading(true);
    setError(null);
    try {
      await api.uploadDocument(file);
      setLastUploaded(file.name);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="border border-line rounded p-3">
      <p className="text-xs text-muted mb-2">Documents (for RAG)</p>
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.docx,.txt,.md,.csv"
        className="hidden"
        onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
      />
      <button
        onClick={() => inputRef.current?.click()}
        disabled={uploading}
        className="w-full text-sm text-left text-signal hover:underline disabled:opacity-50"
      >
        {uploading ? "Indexing…" : "+ Upload a document"}
      </button>
      {lastUploaded && <p className="text-xs text-muted mt-2 truncate">Indexed: {lastUploaded}</p>}
      {error && <p className="text-xs text-red-400 mt-2">{error}</p>}
    </div>
  );
}
