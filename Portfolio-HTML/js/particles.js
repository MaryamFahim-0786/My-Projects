/* ==========================================================
   PARTICLES.JS
   Maryam AI Neural Background
========================================================== */

const canvas = document.getElementById("particles");

if(canvas){

const ctx = canvas.getContext("2d");

let particles = [];

const mouse = {

x:null,

y:null,

radius:170

};



function resize(){

canvas.width = window.innerWidth;

canvas.height = window.innerHeight;

}

resize();

window.addEventListener("resize",resize);



window.addEventListener("mousemove",(e)=>{

mouse.x = e.clientX;

mouse.y = e.clientY;

});



class Particle{

constructor(){

this.x = Math.random()*canvas.width;

this.y = Math.random()*canvas.height;

this.size = Math.random()*2+1;

this.speedX = (Math.random()-.5)*0.5;

this.speedY = (Math.random()-.5)*0.5;

}

update(){

this.x += this.speedX;

this.y += this.speedY;

if(this.x<0||this.x>canvas.width) this.speedX*=-1;

if(this.y<0||this.y>canvas.height) this.speedY*=-1;

const dx=this.x-mouse.x;

const dy=this.y-mouse.y;

const distance=Math.sqrt(dx*dx+dy*dy);

if(distance<mouse.radius){

this.x += dx/18;

this.y += dy/18;

}

}

draw(){

ctx.beginPath();

ctx.arc(this.x,this.y,this.size,0,Math.PI*2);

ctx.fillStyle="#4F8CFF";

ctx.fill();

}

}



function init(){

particles=[];

for(let i=0;i<120;i++){

particles.push(new Particle());

}

}

init();



function connect(){

for(let a=0;a<particles.length;a++){

for(let b=a;b<particles.length;b++){

const dx=particles[a].x-particles[b].x;

const dy=particles[a].y-particles[b].y;

const distance=Math.sqrt(dx*dx+dy*dy);

if(distance<120){

ctx.strokeStyle=`rgba(79,140,255,${
1-distance/120
})`;

ctx.lineWidth=.5;

ctx.beginPath();

ctx.moveTo(

particles[a].x,

particles[a].y

);

ctx.lineTo(

particles[b].x,

particles[b].y

);

ctx.stroke();

}

}

}

}



function animate(){

ctx.clearRect(

0,

0,

canvas.width,

canvas.height

);

particles.forEach(p=>{

p.update();

p.draw();

});

connect();

requestAnimationFrame(

animate

);

}

animate();

}