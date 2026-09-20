"use client"

import React from "react"
import Image from "next/image"
import { Button } from "@/components/ui/button"
import { FaGithub, FaLinkedin, FaEnvelope, FaWhatsapp } from "react-icons/fa"
import { useChatContext } from "@/features/chat/context/chat-context"
import { cn } from "@/lib/utils"
import { socialLinks } from "@/lib/config"
import type { IconType } from "react-icons"

interface SocialItem {
    icon: IconType
    label: string
    url?: string
    action?: "contact"
}

const SOCIAL_ITEMS: SocialItem[] = [
    { icon: FaGithub, label: "GitHub", url: socialLinks.github },
    { icon: FaLinkedin, label: "LinkedIn", url: socialLinks.linkedin },
    { icon: FaWhatsapp, label: "WhatsApp", url: socialLinks.whatsapp },
    { icon: FaEnvelope, label: "Email", action: "contact" }
]

export function ProfileHeader() {
    const { setIsContactDialogOpen, tourStep } = useChatContext();
    const handleClick = (item: SocialItem) => {
        if (item.action === "contact") {
            setIsContactDialogOpen(true);
        } else if (item.url) {
            window.open(item.url, "_blank", "noopener,noreferrer")
        }
    }

    return (
        <div className="relative z-10 flex flex-col pt-8 xl:pt-6 pb-2 xl:px-5">
            {/* Profile Image (replace public/profile.webp with your own photo any time) */}
            <div className="flex justify-center mb-2 md:mb-4">
                <div className="relative w-24 h-24 xl:w-28 xl:h-28 rounded-full overflow-hidden ring-2 ring-indigo-500/30 ring-offset-2 ring-offset-zinc-900">
                    <Image
                        src="/profile.webp"
                        alt="Maryam Fahim"
                        width={200}
                        height={200}
                        className="object-cover w-full h-full"
                        quality={95}
                        priority
                    />
                </div>
            </div>

            {/* Role Label */}
            <div className="mb-2 text-center">
                <span className="inline-block text-[12px] xl:text-[14px] font-bold tracking-[0.2em] uppercase text-indigo-400">
                    AI Full-Stack Developer
                </span>
            </div>

            {/* Name */}
            <h1 className="text-3xl xl:text-3xl font-bold text-white mb-2 tracking-tight text-center">
                Maryam Fahim
            </h1>

            {/* Bio */}
            <p className="text-base xl:text-base text-zinc-300 leading-snug md:leading-relaxed font-light mb-2 text-center px-3">
                I've built this AI assistant from my projects and experience.
                It answers from my own work, so you can explore my journey
                through conversation.
            </p>

            {/* Social Links */}
            <div
                id="tour-social-links"
                className="flex gap-3 xl:gap-6 justify-center mb-1 xl:mb-2"
            >
                {SOCIAL_ITEMS.map((item) => (
                    <Button
                        key={item.label}
                        variant="ghost"
                        size="icon"
                        className={cn(
                            "group h-12 w-12 xl:h-11 xl:w-11 rounded-xl hover:text-indigo-400 active:text-indigo-400 hover:scale-[1.12] active:scale-[1.12] hover:shadow-lg active:shadow-lg transition-all duration-300",
                            tourStep?.targetId === "tour-social-links" && "relative z-50 text-indigo-400"
                        )}
                        onClick={() => handleClick(item)}
                        aria-label={item.label}
                    >
                        <item.icon className="size-6 xl:size-7" />
                        <span className="sr-only">{item.label}</span>
                    </Button>
                ))}
            </div>

            {/* Gradient Separator */}
            <div className="h-px w-full bg-gradient-to-r from-white/10 via-white/5 to-transparent" />
        </div>
    )
}
