/* ==========================================================
   CURSOR.JS
   Maryam AI Cursor
========================================================== */

const dot = document.querySelector(".cursor-dot");
const ring = document.querySelector(".cursor-ring");
const glow = document.querySelector(".cursor-glow");

let mouseX = 0;
let mouseY = 0;

let ringX = 0;
let ringY = 0;

document.addEventListener("mousemove",(e)=>{

    mouseX = e.clientX;
    mouseY = e.clientY;

    dot.style.left = mouseX + "px";
    dot.style.top = mouseY + "px";

    glow.style.left = mouseX + "px";
    glow.style.top = mouseY + "px";

});

function animateCursor(){

    ringX += (mouseX-ringX)*0.15;
    ringY += (mouseY-ringY)*0.15;

    ring.style.left = ringX+"px";
    ring.style.top = ringY+"px";

    requestAnimationFrame(animateCursor);

}

animateCursor();



/* ===========================
   CLICK
=========================== */

document.addEventListener("mousedown",()=>{

    ring.classList.add("click");

});

document.addEventListener("mouseup",()=>{

    ring.classList.remove("click");

});


/* ===========================
   HOVER
=========================== */

const hoverItems = document.querySelectorAll(

"a,button,.btn,.project-card,.service-card,.hero-frame"

);

hoverItems.forEach(item=>{

item.addEventListener("mouseenter",()=>{

dot.classList.add("active");
ring.classList.add("active");

});

item.addEventListener("mouseleave",()=>{

dot.classList.remove("active");
ring.classList.remove("active");

});

});