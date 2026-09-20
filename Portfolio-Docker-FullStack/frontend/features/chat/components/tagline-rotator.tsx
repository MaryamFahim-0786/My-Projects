"use client"

import { useEffect, useState, useCallback } from "react"
import { motion, AnimatePresence } from "framer-motion"

const SENTENCES = [
    "Turning prompts into products.",
    "Teaching LLMs to read my documents, politely.",
    "RAG: because guessing isn't a feature.",
    "Full-stack, with a healthy dose of AI.",
    "Pushes code, embeds documents, sips chai.",
    "Debugging my own code like it's someone else's.",
    "Retrieves relevant context, forgets where I left my keys.",
    "Good at naming variables... eventually.",
    "Compiles successfully, runs accidentally.",
    "Always one semicolon away from disaster.",
    "Vector search finds anything except my sleep schedule.",
    "Ships side projects faster than I ship excuses.",
    "Stack Overflow is my study buddy.",
    "Code reviews are my cardio.",
]

export function TaglineRotator() {
    const [currentIndex, setCurrentIndex] = useState(0)

    const rotateSentence = useCallback(() => {
        setCurrentIndex((prev) => (prev + 1) % SENTENCES.length)
    }, [])

    useEffect(() => {
        const interval = setInterval(rotateSentence, 7000)
        return () => clearInterval(interval)
    }, [rotateSentence])

    return (
        <div className="mt-3 text-center text-xs md:text-sm font-medium text-white/60">
            {/* mode="wait" ensures the old text fades out completely before the new text fades in */}
            <AnimatePresence mode="wait">
                <motion.p
                    key={currentIndex}
                    initial={{ opacity: 0, y: 5, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -5, scale: 0.95 }}
                    transition={{ duration: 0.6 }}
                >
                    {SENTENCES[currentIndex]}
                </motion.p>
            </AnimatePresence>
        </div>
    )
}