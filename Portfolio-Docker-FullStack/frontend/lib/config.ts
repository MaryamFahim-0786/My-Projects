import { getAbsoluteUrl } from "@/lib/opengraph-utils";

/**
 * Single source of truth for contact / social links.
 * Update them here and every component (sidebar, mobile header, contact cards) follows.
 */
export const socialLinks = {
    github: 'https://github.com/MaryamFahim-0786',
    linkedin: 'https://www.linkedin.com/in/maryam-fahim-9b2111339',
    // wa.me link = +92 334 0079140. The number itself is never printed on the page.
    whatsapp: 'https://wa.me/923340079140',
} as const;

export const siteConfig = {
    name: 'Maryam Fahim',
    // We use the utility to get the absolute URL for the homepage
    url: getAbsoluteUrl("/"),
    title: 'Maryam Fahim | AI Full-Stack Developer',
    description: 'Skip the boring portfolio scroll. Chat with my AI assistant to explore my projects, skills, and experience through natural conversation.',
    author: 'Maryam Fahim',
    links: socialLinks,
    // Using the local image in public/og-image.png
    // We add ?v=2 to force social media platforms to clear their cache and fetch the new image
    ogImage: "/og-image.png?v=2",
};
