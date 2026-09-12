/* ==========================================================
   MARYAM AI PORTFOLIO
   Main Script
========================================================== */

document.addEventListener("DOMContentLoaded", () => {

    console.log("%c🚀 MARYAM AI PORTFOLIO INITIALIZED",
        "color:#4F8CFF;font-size:16px;font-weight:bold;"
    );

    initLoader();

    initNavbar();

    initScrollProgress();

    initSpotlight();

    initScrollReveal();

    initHeroAnimations();

});



/* ==========================================
   LOADER
========================================== */

function initLoader(){

    const loader = document.getElementById("loader");

    if(!loader) return;

    window.addEventListener("load",()=>{

        setTimeout(()=>{

            loader.style.opacity="0";

            loader.style.visibility="hidden";

        },1800);

    });

}



/* ==========================================
   NAVBAR
========================================== */

function initNavbar(){

    const header=document.getElementById("header");

    window.addEventListener("scroll",()=>{

        if(window.scrollY>80){

            header.classList.add("scrolled");

        }

        else{

            header.classList.remove("scrolled");

        }

    });

}



/* ==========================================
   SCROLL BAR
========================================== */

function initScrollProgress(){

    const progress=document.querySelector(".page-progress span");

    if(!progress) return;

    window.addEventListener("scroll",()=>{

        const total=

        document.documentElement.scrollHeight-

        window.innerHeight;

        const value=

        (window.scrollY/total)*100;

        progress.style.width=value+"%";

    });

}



/* ==========================================
   SPOTLIGHT
========================================== */

function initSpotlight(){

    const spotlight=document.querySelector(".spotlight");

    if(!spotlight) return;

    document.addEventListener("mousemove",(e)=>{

        spotlight.style.left=e.clientX+"px";

        spotlight.style.top=e.clientY+"px";

    });

}



/* ==========================================
   SCROLL REVEAL
========================================== */

function initScrollReveal(){

    const elements=document.querySelectorAll(

        ".section,.project-card,.service-card,.timeline-item"

    );

    const observer=new IntersectionObserver(

        entries=>{

            entries.forEach(entry=>{

                if(entry.isIntersecting){

                    entry.target.classList.add("show");

                }

            });

        },

        {

            threshold:.15

        }

    );

    elements.forEach(el=>observer.observe(el));

}



/* ==========================================
   HERO
========================================== */

function initHeroAnimations(){

    const hero=document.querySelector(".hero");

    if(!hero) return;

    window.addEventListener("mousemove",(e)=>{

        const x=(e.clientX/window.innerWidth-.5)*20;

        const y=(e.clientY/window.innerHeight-.5)*20;

        hero.style.transform=

        `translate(${x}px,${y}px)`;

    });

}
// ===============================
// SCROLL REVEAL ANIMATION
// ===============================

const reveals = document.querySelectorAll(".reveal");

const observer = new IntersectionObserver((entries)=>{

    entries.forEach(entry=>{

        if(entry.isIntersecting){

            entry.target.classList.add("active");

        }

    });

}, {
    threshold: 0.15
});


reveals.forEach(item=>{
    observer.observe(item);
});
/* ==========================================
   HERO TYPING EFFECT
========================================== */

function initTyping(){

    const textElement = document.getElementById("typing");

    if(!textElement) return;


    const text = "AI Engineer • Full Stack Developer";

    let index = 0;


    function type(){

        if(index < text.length){

            textElement.textContent += text.charAt(index);

            index++;

            setTimeout(type,80);

        }

    }


    type();

}


initTyping();
function animateText(){

    const elements = document.querySelectorAll(".animate-text");

    elements.forEach((element,index)=>{

        const text = element.innerText;

        element.innerText="";

        let i=0;


        setTimeout(()=>{

            function typing(){

                if(i < text.length){

                    element.innerText += text.charAt(i);

                    i++;

                    setTimeout(typing,60);

                }

            }

            typing();

        }, index * 1500);

    });

}


animateText();