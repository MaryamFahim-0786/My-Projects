/* ==========================================================
   ANIMATIONS.JS
   Premium Portfolio Animations
========================================================== */


/* ==========================================
   REVEAL ON SCROLL
========================================== */

const revealElements = document.querySelectorAll(
    ".section, .project-card, .service-card, .timeline-item"
);

const revealObserver = new IntersectionObserver(

(entries)=>{

entries.forEach(entry=>{

if(entry.isIntersecting){

entry.target.classList.add("active");

}

});

},

{

threshold:0.15

}

);

revealElements.forEach(element=>{

revealObserver.observe(element);

});


/* ==========================================
   HERO PARALLAX
========================================== */

const heroImage = document.querySelector(".image-wrapper");

document.addEventListener("mousemove",(e)=>{

if(!heroImage) return;

const x=(window.innerWidth/2-e.clientX)/35;

const y=(window.innerHeight/2-e.clientY)/35;

heroImage.style.transform=

`translate(${x}px,${y}px)`;

});


/* ==========================================
   BUTTON GLOW
========================================== */

const buttons=document.querySelectorAll(".btn");

buttons.forEach(button=>{

button.addEventListener("mousemove",(e)=>{

const rect=button.getBoundingClientRect();

const x=e.clientX-rect.left;

const y=e.clientY-rect.top;

button.style.setProperty("--x",x+"px");

button.style.setProperty("--y",y+"px");

});

});


/* ==========================================
   PROJECT CARD 3D
========================================== */

const cards=document.querySelectorAll(".project-card");

cards.forEach(card=>{

card.addEventListener("mousemove",(e)=>{

const rect=card.getBoundingClientRect();

const x=e.clientX-rect.left;

const y=e.clientY-rect.top;

const rotateY=((x-rect.width/2)/18);

const rotateX=((rect.height/2-y)/18);

card.style.transform=

`perspective(1000px)
rotateX(${rotateX}deg)
rotateY(${rotateY}deg)
translateY(-10px)`;

});

card.addEventListener("mouseleave",()=>{

card.style.transform=

"perspective(1000px) rotateX(0) rotateY(0)";

});

});


/* ==========================================
   SERVICE CARD 3D
========================================== */

const services=document.querySelectorAll(".service-card");

services.forEach(card=>{

card.addEventListener("mousemove",(e)=>{

const rect=card.getBoundingClientRect();

const x=e.clientX-rect.left;

const y=e.clientY-rect.top;

const rotateY=((x-rect.width/2)/22);

const rotateX=((rect.height/2-y)/22);

card.style.transform=

`perspective(1000px)
rotateX(${rotateX}deg)
rotateY(${rotateY}deg)
translateY(-8px)`;

});

card.addEventListener("mouseleave",()=>{

card.style.transform=

"perspective(1000px) rotateX(0) rotateY(0)";

});

});


/* ==========================================
   NAVBAR HIDE / SHOW
========================================== */

let lastScroll=0;

const header=document.getElementById("header");

window.addEventListener("scroll",()=>{

const current=window.pageYOffset;

if(current>lastScroll && current>150){

header.style.transform="translateY(-120%)";

}

else{

header.style.transform="translateY(0)";

}

lastScroll=current;

});


/* ==========================================
   HERO IMAGE FLOAT
========================================== */

let angle=0;

function floatHero(){

if(heroImage){

angle+=0.01;

heroImage.style.marginTop=

Math.sin(angle)*8+"px";

}

requestAnimationFrame(floatHero);

}

floatHero();


/* ==========================================
   CONSOLE MESSAGE
========================================== */

console.log(

"%cMaryam AI Portfolio Loaded 🚀",

"color:#4F8CFF;font-size:18px;font-weight:bold;"

);