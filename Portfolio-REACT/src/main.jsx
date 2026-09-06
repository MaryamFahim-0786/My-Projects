import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
/* ==========================================================
   3D INTERACTIVE NETWORK
   Cursor repels nearby nodes
========================================================== */

const canvas = document.getElementById("particles");

if (canvas) {

    const ctx = canvas.getContext("2d");

    let width;
    let height;

    const mouse = {
        x: null,
        y: null,
        radius: 150
    };

    const nodes = [];

    const NODE_COUNT = 90;
    const CONNECTION_DISTANCE = 150;

    function resizeCanvas() {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    }

    resizeCanvas();

    window.addEventListener("resize", resizeCanvas);

    window.addEventListener("mousemove", (e) => {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
    });

    window.addEventListener("mouseleave", () => {
        mouse.x = null;
        mouse.y = null;
    });

    class Node {

        constructor() {

            this.x = Math.random() * width;
            this.y = Math.random() * height;

            this.vx = (Math.random() - 0.5) * 0.35;
            this.vy = (Math.random() - 0.5) * 0.35;

            this.size = Math.random() * 1.5 + 0.5;
        }

        update() {

            this.x += this.vx;
            this.y += this.vy;

            if (this.x < 0 || this.x > width) {
                this.vx *= -1;
            }

            if (this.y < 0 || this.y > height) {
                this.vy *= -1;
            }

            /* Cursor REPULSION */

            if (mouse.x !== null && mouse.y !== null) {

                const dx = this.x - mouse.x;
                const dy = this.y - mouse.y;

                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < mouse.radius && distance > 0) {

                    const force =
                        (mouse.radius - distance) /
                        mouse.radius;

                    this.x += (dx / distance) * force * 2.5;
                    this.y += (dy / distance) * force * 2.5;
                }
            }
        }

        draw() {

            ctx.beginPath();

            ctx.arc(
                this.x,
                this.y,
                this.size,
                0,
                Math.PI * 2
            );

            ctx.fillStyle = "rgba(120,210,255,0.65)";

            ctx.fill();
        }
    }

    for (let i = 0; i < NODE_COUNT; i++) {
        nodes.push(new Node());
    }

    function connectNodes() {

        for (let i = 0; i < nodes.length; i++) {

            for (let j = i + 1; j < nodes.length; j++) {

                const dx = nodes[i].x - nodes[j].x;
                const dy = nodes[i].y - nodes[j].y;

                const distance = Math.sqrt(
                    dx * dx + dy * dy
                );

                if (distance < CONNECTION_DISTANCE) {

                    const opacity =
                        (1 - distance / CONNECTION_DISTANCE) * 0.22;

                    ctx.beginPath();

                    ctx.moveTo(
                        nodes[i].x,
                        nodes[i].y
                    );

                    ctx.lineTo(
                        nodes[j].x,
                        nodes[j].y
                    );

                    ctx.strokeStyle =
                        `rgba(100,200,255,${opacity})`;

                    ctx.lineWidth = 0.6;

                    ctx.stroke();
                }
            }
        }
    }

    function animate() {

        ctx.clearRect(0, 0, width, height);

        nodes.forEach(node => {
            node.update();
        });

        connectNodes();

        nodes.forEach(node => {
            node.draw();
        });

        requestAnimationFrame(animate);
    }

    animate();
}