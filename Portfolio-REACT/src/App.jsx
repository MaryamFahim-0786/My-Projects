import React, { useEffect, useRef, useState } from "react";
import { portfolioData as d } from "./data";

import "./styles/variables.css";
import "./styles/style.css";
import "./styles/components.css";
import "./styles/animations.css";
import "./styles/chatbot.css";
import "./styles/responsive-react.css";


/* ==========================================================
   ASSETS
========================================================== */

const profileImage = "/assets/images/profile.png";
const resumeUrl = "/assets/resume/resume.pdf";


/* ==========================================================
   BACKGROUND PARTICLE NETWORK
========================================================== */

function Background() {

  const canvasRef = useRef(null);

  useEffect(() => {

    const canvas = canvasRef.current;

    if (!canvas) return;

    const ctx = canvas.getContext("2d");

    let animationFrame;
    let particles = [];

    const mouse = {
      x: -9999,
      y: -9999,
      radius: 180
    };


    /* ======================================================
       RESIZE CANVAS
    ====================================================== */

    const resize = () => {

      const dpr = window.devicePixelRatio || 1;

      canvas.width = window.innerWidth * dpr;
      canvas.height = window.innerHeight * dpr;

      canvas.style.width = `${window.innerWidth}px`;
      canvas.style.height = `${window.innerHeight}px`;

      ctx.setTransform(
        dpr,
        0,
        0,
        dpr,
        0,
        0
      );


      /* Particle count */

      const count = Math.min(
        95,
        Math.max(
          55,
          Math.floor(window.innerWidth / 14)
        )
      );


      particles = Array.from(
        { length: count },
        () => ({

          x:
            Math.random() *
            window.innerWidth,

          y:
            Math.random() *
            window.innerHeight,

          size:
            Math.random() * 1.8 + 0.7,

          vx:
            (Math.random() - 0.5) * 0.28,

          vy:
            (Math.random() - 0.5) * 0.28

        })
      );

    };


    /* ======================================================
       MOUSE MOVE
    ====================================================== */

    const onMove = (e) => {

      mouse.x = e.clientX;
      mouse.y = e.clientY;

    };


    /* ======================================================
       MOUSE LEAVE
    ====================================================== */

    const onLeave = () => {

      mouse.x = -9999;
      mouse.y = -9999;

    };


    /* ======================================================
       DRAW ANIMATION
    ====================================================== */

    const draw = () => {

      ctx.clearRect(
        0,
        0,
        window.innerWidth,
        window.innerHeight
      );


      /* ====================================================
         UPDATE PARTICLES
      ==================================================== */

      particles.forEach((p) => {

        p.x += p.vx;
        p.y += p.vy;


        /* Screen boundaries */

        if (p.x < -20) {
          p.x = window.innerWidth + 20;
        }

        if (p.x > window.innerWidth + 20) {
          p.x = -20;
        }

        if (p.y < -20) {
          p.y = window.innerHeight + 20;
        }

        if (p.y > window.innerHeight + 20) {
          p.y = -20;
        }


        /* ==================================================
           CURSOR REPULSION
        ================================================== */

        const dx = p.x - mouse.x;
        const dy = p.y - mouse.y;

        const distance = Math.sqrt(
          dx * dx + dy * dy
        );


        if (
          distance < mouse.radius &&
          distance > 0
        ) {

          const force =
            (mouse.radius - distance) /
            mouse.radius;

          p.x +=
            (dx / distance) *
            force *
            1.8;

          p.y +=
            (dy / distance) *
            force *
            1.8;

        }

      });


      /* ====================================================
         DRAW CONNECTIONS
      ==================================================== */

      for (
        let i = 0;
        i < particles.length;
        i++
      ) {

        const p = particles[i];


        for (
          let j = i + 1;
          j < particles.length;
          j++
        ) {

          const q = particles[j];

          const dx = p.x - q.x;
          const dy = p.y - q.y;

          const distance = Math.sqrt(
            dx * dx + dy * dy
          );


         if (distance < 155) {

  const opacity =
    0.32 *
    (1 - distance / 155);

  ctx.beginPath();

  ctx.moveTo(
    p.x,
    p.y
  );

  ctx.lineTo(
    q.x,
    q.y
  );

  ctx.strokeStyle =
    `rgba(79, 140, 255, ${opacity})`;

  ctx.lineWidth = 0.9;

  ctx.stroke();

}

        }

      }


      /* ====================================================
         DRAW PARTICLES
      ==================================================== */

      particles.forEach((p) => {

        const dx = p.x - mouse.x;
        const dy = p.y - mouse.y;

        const distance = Math.sqrt(
          dx * dx + dy * dy
        );


        let alpha = 0.38;
        let radius = p.size;


        /* Cursor influence */

        if (
          distance < mouse.radius &&
          distance > 0
        ) {

          const influence =
            1 -
            distance /
            mouse.radius;


          alpha =
            0.38 +
            influence *
            0.42;


          radius =
            p.size +
            influence *
            1.2;

        }


        ctx.beginPath();

        ctx.arc(
          p.x,
          p.y,
          radius,
          0,
          Math.PI * 2
        );

        ctx.fillStyle =
          `rgba(79,140,255,${alpha})`;

        ctx.fill();

      });


      /* ====================================================
         CONTINUE ANIMATION
      ==================================================== */

      animationFrame =
        requestAnimationFrame(draw);

    };


    /* ======================================================
       INITIALIZE
    ====================================================== */

    resize();

    window.addEventListener(
      "resize",
      resize
    );

    window.addEventListener(
      "mousemove",
      onMove
    );

    window.addEventListener(
      "mouseleave",
      onLeave
    );

    draw();


    /* ======================================================
       CLEANUP
    ====================================================== */

    return () => {

      cancelAnimationFrame(
        animationFrame
      );

      window.removeEventListener(
        "resize",
        resize
      );

      window.removeEventListener(
        "mousemove",
        onMove
      );

      window.removeEventListener(
        "mouseleave",
        onLeave
      );

    };

  }, []);


  return (

    <div
      className="background-wrapper"
      aria-hidden="true"
    >

      <canvas
        id="particles"
        ref={canvasRef}
      />

      <div className="gradient gradient-1" />
      <div className="gradient gradient-2" />
      <div className="gradient gradient-3" />

      <div className="grid-overlay" />
      <div className="noise-layer" />
      <div className="spotlight" />

    </div>

  );

}


/* ==========================================================
   CUSTOM CURSOR
========================================================== */

function CustomCursor() {

  const dotRef = useRef(null);
  const ringRef = useRef(null);


  useEffect(() => {

    if (
      window.matchMedia(
        "(max-width: 991px)"
      ).matches
    ) {
      return;
    }


    const dot = dotRef.current;
    const ring = ringRef.current;


    if (!dot || !ring) {
      return;
    }


    let x = 0;
    let y = 0;

    let rx = 0;
    let ry = 0;

    let raf;


    const move = (e) => {

      x = e.clientX;
      y = e.clientY;

      dot.style.left = `${x}px`;
      dot.style.top = `${y}px`;

    };


    const animate = () => {

      rx +=
        (x - rx) *
        0.15;

      ry +=
        (y - ry) *
        0.15;


      ring.style.left =
        `${rx}px`;

      ring.style.top =
        `${ry}px`;


      raf =
        requestAnimationFrame(
          animate
        );

    };


    const mouseDown = () => {

      ring.classList.add(
        "click"
      );

    };


    const mouseUp = () => {

      ring.classList.remove(
        "click"
      );

    };


    const enter = () => {

      dot.classList.add(
        "active"
      );

      ring.classList.add(
        "active"
      );

    };


    const leave = () => {

      dot.classList.remove(
        "active"
      );

      ring.classList.remove(
        "active"
      );

    };


    document.addEventListener(
      "mousemove",
      move
    );

    document.addEventListener(
      "mousedown",
      mouseDown
    );

    document.addEventListener(
      "mouseup",
      mouseUp
    );


    const interactiveElements =
      document.querySelectorAll(
        "a, button, .btn, .project-card, .service-card, .hero-frame"
      );


    interactiveElements.forEach(
      (el) => {

        el.addEventListener(
          "mouseenter",
          enter
        );

        el.addEventListener(
          "mouseleave",
          leave
        );

      }
    );


    animate();


    return () => {

      cancelAnimationFrame(
        raf
      );

      document.removeEventListener(
        "mousemove",
        move
      );

      document.removeEventListener(
        "mousedown",
        mouseDown
      );

      document.removeEventListener(
        "mouseup",
        mouseUp
      );


      interactiveElements.forEach(
        (el) => {

          el.removeEventListener(
            "mouseenter",
            enter
          );

          el.removeEventListener(
            "mouseleave",
            leave
          );

        }
      );

    };

  }, []);


  return (

    <>

      <div
        className="cursor-dot"
        ref={dotRef}
      />

      <div
        className="cursor-ring"
        ref={ringRef}
      />

      <div className="cursor-glow" />

    </>

  );

}


/* ==========================================================
   HEADER
========================================================== */

function Header() {

  const [open, setOpen] =
    useState(false);

const [theme, setTheme] = useState(() => {
  return localStorage.getItem("portfolio-theme") || "dark";
});

useEffect(() => {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("portfolio-theme", theme);
}, [theme]);
  const navigation = [

    ["home", "Home"],

    ["mission", "Who I Am"],

    ["journey", "Journey"],

    ["skills", "Skills"],

    ["projects", "Projects"],

    ["education", "Education"],

    ["resume", "Resume"],

    ["contact", "Contact"]

  ];


  return (

    <header id="header">

      <nav className="navbar">


        {/* LOGO */}

        <a
          href="#home"
          className="logo"
          onClick={() =>
            setOpen(false)
          }
        >

          <img
            className="profile-avatar"
            src={profileImage}
            alt="Maryam Fahim"
          />

          <div className="brand-info">

            <h3>
              {d.name}
            </h3>

          </div>

        </a>


        {/* NAVIGATION */}

        <ul
          className={`nav-menu ${
            open ? "active" : ""
          }`}
        >

          {navigation.map(
            ([id, label]) => (

              <li key={id}>

                <a
                  href={`#${id}`}
                  onClick={() =>
                    setOpen(false)
                  }
                >
                  {label}
                </a>

              </li>

            )
          )}

        </ul>


        {/* CV BUTTON */}
<button
  className="theme-toggle"
  type="button"
  aria-label={`Switch to ${
    theme === "dark" ? "light" : "dark"
  } mode`}
  onClick={() =>
    setTheme((current) =>
      current === "dark"
        ? "light"
        : "dark"
    )
  }
>
  <i
    className={
      theme === "dark"
        ? "fas fa-sun"
        : "fas fa-moon"
    }
  />
</button>
        <a
          href={resumeUrl}
          download="Maryam_Fahim_Resume.pdf"
          className="header-cv-btn"
        >

          <i className="fas fa-download" />

          <span>
            Download CV
          </span>

        </a>


        {/* MOBILE MENU */}

        <button
          className={`menu-toggle ${
            open ? "active" : ""
          }`}
          aria-label="Toggle menu"
          onClick={() =>
            setOpen(
              (value) => !value
            )
          }
        >

          <i
            className={
              open
                ? "fas fa-xmark"
                : "fas fa-bars"
            }
          />

        </button>

      </nav>

    </header>

  );

}


/* ==========================================================
   HERO
========================================================== */

function Hero() {

  const [typed, setTyped] =
    useState("");


  useEffect(() => {

    const text =
      "AI Engineer • Full Stack Developer";

    let i = 0;


    const id =
      setInterval(() => {

        i++;

        setTyped(
          text.slice(0, i)
        );


        if (
          i >= text.length
        ) {

          clearInterval(id);

        }

      }, 55);


    return () =>
      clearInterval(id);

  }, []);


  return (

    <section
      className="hero"
      id="home"
    >

      <div className="container">


        {/* HERO CONTENT */}

        <div className="hero-content">


          <div className="hero-label">

            <i className="fas fa-circle" />

            Available for Opportunities

          </div>


          <h1 className="hero-title">

            BUILDING{" "}

            <span className="gradient-text">
              INTELLIGENT
            </span>{" "}

            DIGITAL EXPERIENCES

          </h1>


          <h2 className="hero-name">

            I'm Maryam Fahim

          </h2>


          <h3 className="typing-text">

            <span>
              {typed}
            </span>

            <span className="cursor">
              |
            </span>

          </h3>


          <p className="hero-description">

            A passionate AI Engineer and
            Full Stack Developer creating
            modern, interactive, and
            intelligent web applications.
            I enjoy blending clean design
            with advanced technology to
            build memorable digital
            experiences.

          </p>


          <div className="hero-buttons">

            <a
              href="#projects"
              className="btn btn-primary"
            >
              View Projects
            </a>


            <a
              href="#contact"
              className="btn btn-secondary"
            >
              Let's Talk
            </a>

          </div>


          {/* STATUS */}

          <div className="hero-status">


            <div className="status-card">

              <span className="status-title">
                STATUS
              </span>

              <span className="status-value online">
                ● ONLINE
              </span>

            </div>


            <div className="status-card">

              <span className="status-title">
                FOCUS
              </span>

              <span className="status-value">
                AI & Full Stack
              </span>

            </div>


            <div className="status-card">

              <span className="status-title">
                LOCATION
              </span>

              <span className="status-value">
                {d.location}
              </span>

            </div>


          </div>

        </div>


        {/* HERO IMAGE */}

        <div className="hero-image">

          <div className="image-wrapper">

            <div className="image-glow" />

            <div className="orbit orbit-1" />
            <div className="orbit orbit-2" />
            <div className="orbit orbit-3" />
            <div className="orbit orbit-4" />


            <div className="hero-frame">

              <img
                src={profileImage}
                alt="Maryam Fahim"
              />

            </div>

          </div>

        </div>


      </div>

    </section>

  );

}


/* ==========================================================
   MISSION
========================================================== */

function Mission() {

  return (

    <section
      id="mission"
      className="section reveal"
    >

      <div className="section-bg-text">
        MISSION
      </div>


      <div className="container">


        <div className="section-heading">

          <span className="section-tag">
            WHO I AM
          </span>

          <h2>
            Creating Technology That Makes An Impact
          </h2>

        </div>


        <div className="mission-container">


          <div className="mission-left">

            <h2>

              Turning Ideas Into{" "}

              <span className="gradient-text">
                Digital Reality
              </span>

            </h2>

          </div>


          <div className="mission-right">

            <p>

              I am a Computer Science undergraduate
              and aspiring AI Engineer & Full Stack
              Developer. My focus is Artificial
              Intelligence, Machine Learning,
              Full Stack Development and building
              scalable, user-centered solutions.

            </p>


            <div className="mission-tags">

              {d.focus.map(
                (x) => (

                  <span key={x}>
                    {x}
                  </span>

                )
              )}

            </div>

          </div>

        </div>

      </div>

    </section>

  );

}

/* ==========================================================
   AI ENGINEER DASHBOARD
========================================================== */

function AIDashboard() {

  const projectCount = d.projects?.length || 0;

  const technologyCount =
    d.skills?.reduce(
      (total, skill) =>
        total + (skill.items?.length || 0),
      0
    ) || 0;

  const systemsCount = 3;

  const focusAreas = [
    {
      name: "AI ENGINEERING",
      level: 88
    },
    {
      name: "FULL STACK DEVELOPMENT",
      level: 92
    },
    {
      name: "GENERATIVE AI",
      level: 72
    },
    {
      name: "AUTOMATION",
      level: 68
    }
  ];

  return (

    <section
      id="ai-dashboard"
      className="section reveal ai-dashboard-section"
    >

      <div className="section-bg-text">
        SYSTEM
      </div>


      <div className="container">


        {/* SECTION HEADING */}

        <div className="section-heading">

          <span className="section-tag">
            SYSTEM OVERVIEW
          </span>

          <h2>
            AI Engineer Dashboard
          </h2>

        </div>


        {/* DASHBOARD */}

        <div className="ai-dashboard">


          {/* TOP BAR */}

          <div className="dashboard-top">

            <div>

              <span className="dashboard-code">
                SYSTEM // MF-AI
              </span>

              <h3>
                Maryam AI Systems
              </h3>

            </div>


            <div className="system-status">

              <span className="status-pulse" />

              SYSTEM ONLINE

            </div>

          </div>


          {/* IDENTITY */}

          <div className="dashboard-identity">

            <div>

              <span>
                PRIMARY ROLE
              </span>

              <strong>
                AI ENGINEER
              </strong>

            </div>


            <div>

              <span>
                SECONDARY ROLE
              </span>

              <strong>
                FULL STACK DEVELOPER
              </strong>

            </div>


            <div>

              <span>
                BUILD STATUS
              </span>

              <strong>
                ACTIVELY BUILDING
              </strong>

            </div>

          </div>


          {/* STATISTICS */}

          <div className="dashboard-stats">


            <div className="dashboard-stat">

              <i className="fas fa-code" />

              <div>

                <strong>
                  {projectCount}
                </strong>

                <span>
                  PROJECTS
                </span>

              </div>

            </div>


            <div className="dashboard-stat">

              <i className="fas fa-layer-group" />

              <div>

                <strong>
                  {technologyCount}
                </strong>

                <span>
                  TECHNOLOGIES
                </span>

              </div>

            </div>


            <div className="dashboard-stat">

              <i className="fas fa-microchip" />

              <div>

                <strong>
                  {systemsCount}
                </strong>

                <span>
                  CORE SYSTEMS
                </span>

              </div>

            </div>

          </div>


          {/* FOCUS */}

       {/* ======================================================
    CURRENT FOCUS
====================================================== */}

<div className="dashboard-focus">

  <div className="dashboard-subheading">

    <span>
      CURRENT FOCUS
    </span>

    <small>
      2026 // DEVELOPMENT
    </small>

  </div>


  <div className="focus-grid">

    <div className="focus-card">

      <i className="fas fa-brain" />

      <div>

        <strong>
          AI ENGINEERING
        </strong>

        <span>
          Intelligent systems & AI applications
        </span>

      </div>

    </div>


    <div className="focus-card">

      <i className="fas fa-layer-group" />

      <div>

        <strong>
          FULL STACK
        </strong>

        <span>
          Modern web application development
        </span>

      </div>

    </div>


    <div className="focus-card">

      <i className="fas fa-wand-magic-sparkles" />

      <div>

        <strong>
          GENERATIVE AI
        </strong>

        <span>
          Exploring intelligent user experiences
        </span>

      </div>

    </div>


    <div className="focus-card">

      <i className="fas fa-gears" />

      <div>

        <strong>
          AUTOMATION
        </strong>

        <span>
          Smarter workflows & digital solutions
        </span>

      </div>

    </div>

  </div>

</div>


          {/* BOTTOM */}

          <div className="dashboard-footer">

            <span>
              <i className="fas fa-terminal" />
              BUILD • CREATE • INNOVATE
            </span>


            <a
              href="#projects"
              className="dashboard-link"
            >
              EXPLORE MY WORK
              <i className="fas fa-arrow-right" />
            </a>

          </div>


        </div>

      </div>

    </section>

  );

}
/* ==========================================================
   JOURNEY
========================================================== */

function Journey() {

  return (

    <section
      id="journey"
      className="section reveal"
    >

      <div className="section-bg-text">
        JOURNEY
      </div>


      <div className="container">


        <div className="section-heading">

          <span className="section-tag">
            TIMELINE
          </span>

          <h2>
            My Learning Journey
          </h2>

        </div>


        <div className="timeline">

          {d.journey.map(
            (item, i) => (

              <div
                className="timeline-item"
                key={`${item.year}-${item.title}`}
              >


                <div
                  className={`timeline-dot ${
                    i ===
                    d.journey.length - 1
                      ? "future-dot"
                      : ""
                  }`}
                />


                <div className="timeline-content">

                  <span className="timeline-year">
                    {item.year}
                  </span>

                  <h3>
                    {item.title}
                  </h3>

                  <p>
                    {item.description}
                  </p>

                </div>

              </div>

            )
          )}

        </div>

      </div>

    </section>

  );

}


/* ==========================================================
   SKILLS
========================================================== */

function Skills() {

  return (

    <section
      id="skills"
      className="section reveal"
    >

      <div className="section-bg-text">
        SKILLS
      </div>


      <div className="container">


        <div className="section-heading">

          <span className="section-tag">
            CAPABILITIES
          </span>

          <h2>
            Technology Arsenal
          </h2>

        </div>


        <div className="service-grid">

          {d.skills.map(
            (skill) => (

              <div
                className="service-card"
                key={skill.title}
              >


                <i
                  className={`fa-solid ${skill.icon}`}
                />


                <h3>
                  {skill.title}
                </h3>


                <p>

                  {skill.items.map(
                    (x, i) => (

                      <span key={x}>

                        {x}

                        {i <
                          skill.items.length - 1 && (
                          <br />
                        )}

                      </span>

                    )
                  )}

                </p>


              </div>

            )
          )}

        </div>

      </div>

    </section>

  );

}


/* ==========================================================
   EDUCATION
========================================================== */

function Education() {

  return (

    <section
      id="education"
      className="section reveal"
    >

      <div className="section-bg-text">
        EDUCATION
      </div>


      <div className="container">


        <div className="section-heading">

          <span className="section-tag">
            ACADEMIC BACKGROUND
          </span>

          <h2>
            Education
          </h2>

        </div>


        <div className="education-grid">

          {d.education.map(
            (e) => (

              <article
                className="education-card"
                key={e.degree}
              >

                <span className="edu-year">
                  {e.period}
                </span>

                <h3>
                  {e.degree}
                </h3>

                <p>
                  {e.institute}
                </p>

              </article>

            )
          )}

        </div>

      </div>

    </section>

  );

}


/* ==========================================================
   PROJECTS
========================================================== */

function Projects() {

  return (

    <section
      id="projects"
      className="section reveal"
    >

      <div className="section-bg-text">
        PROJECTS
      </div>


      <div className="container">


        <div className="section-heading">

          <span className="section-tag">
            PORTFOLIO
          </span>

          <h2>
            Featured Projects
          </h2>

        </div>


        <div className="project-grid">

          {d.projects.map(
            (p) => (

              <article
                className="project-card"
                key={p.title}
              >

                <h3>

                  {p.icon}{" "}
                  {p.title}

                </h3>


                <p>
                  {p.description}
                </p>


                <span className="gradient-text">
                  {p.status}
                </span>

              </article>

            )
          )}

        </div>

      </div>

    </section>

  );

}


/* ==========================================================
   RESUME
========================================================== */

function Resume() {

  return (

    <section
      id="resume"
      className="section reveal"
    >

      <div className="section-bg-text">
        RESUME
      </div>


      <div className="container">


        <div className="section-heading">

          <span className="section-tag">
            MY CV
          </span>

          <h2>
            Professional Resume
          </h2>

        </div>


        <div className="resume-card">


          <div className="resume-icon">

            <i className="fas fa-file-alt" />

          </div>


          <h3>
            Maryam Fahim Resume
          </h3>


          <p>

            Explore my education,
            technical skills, projects,
            certifications and
            professional profile.

          </p>


          <div className="hero-buttons">


            <a
              href={resumeUrl}
              target="_blank"
              rel="noreferrer"
              className="btn btn-primary"
            >

              <i className="fas fa-eye" />

              View Resume

            </a>


            <a
              href={resumeUrl}
              download="Maryam_Fahim_Resume.pdf"
              className="btn btn-secondary"
            >

              <i className="fas fa-download" />

              Download CV

            </a>


          </div>

        </div>

      </div>

    </section>

  );

}


/* ==========================================================
   CONTACT
========================================================== */

function Contact() {

  const whatsappHref =
    "https://wa.me/923340079140";


  return (

    <section
      id="contact"
      className="section reveal"
    >

      <div className="section-bg-text">
        CONTACT
      </div>


      <div className="container">


        <div className="section-heading">

          <span className="section-tag">
            GET IN TOUCH
          </span>

          <h2>
            Let's Build Something Amazing
          </h2>

        </div>


        <div className="contact-card">


          <h3>
            Ready to collaborate?
          </h3>


          <p>

            I'm always interested in
            internships, freelance work,
            AI projects, web development
            opportunities, and exciting
            collaborations.

          </p>


          <div className="hero-buttons">


            <a
              href={`mailto:${d.email}`}
              className="btn btn-primary"
            >

              <i className="fas fa-envelope" />

              Send Email

            </a>


            <a
              href={d.github}
              target="_blank"
              rel="noreferrer"
              className="btn btn-secondary"
            >

              <i className="fab fa-github" />

              GitHub

            </a>


            <a
              href={d.linkedin}
              target="_blank"
              rel="noreferrer"
              className="btn btn-secondary"
            >

              <i className="fab fa-linkedin" />

              LinkedIn

            </a>


            <a
              href={whatsappHref}
              target="_blank"
              rel="noreferrer"
              className="btn whatsapp-btn"
            >

              <i className="fab fa-whatsapp" />

              WhatsApp

            </a>


          </div>

        </div>

      </div>

    </section>

  );

}


/* ==========================================================
   FOOTER
========================================================== */

function Footer() {

  return (

    <footer>

      <div className="container">


        <h2>
          Maryam Fahim
        </h2>


        <p>

          Building intelligent digital
          experiences with creativity,
          technology and Artificial
          Intelligence.

        </p>


        <div className="footer-social">


          <a
            href={d.github}
            target="_blank"
            rel="noreferrer"
            aria-label="GitHub"
          >

            <i className="fab fa-github" />

          </a>


          <a
            href={d.linkedin}
            target="_blank"
            rel="noreferrer"
            aria-label="LinkedIn"
          >

            <i className="fab fa-linkedin" />

          </a>


          <a
            href={`mailto:${d.email}`}
            aria-label="Email"
          >

            <i className="fas fa-envelope" />

          </a>


          <a
            href="https://wa.me/923340079140"
            target="_blank"
            rel="noreferrer"
            aria-label="WhatsApp"
          >

            <i className="fab fa-whatsapp" />

          </a>


        </div>


        <p>
          © 2026 Maryam Fahim • All Rights Reserved.
        </p>


      </div>

    </footer>

  );

}


/* ==========================================================
   CHATBOT KEYWORDS
========================================================== */

const domainKeywords = [

  "maryam",
  "portfolio",
  "skill",
  "technology",
  "tech",
  "project",
  "education",
  "degree",
  "university",
  "institute",
  "comsats",
  "semester",
  "cgpa",
  "study",
  "student",
  "journey",
  "experience",
  "intern",
  "internship",
  "resume",
  "cv",
  "contact",
  "email",
  "github",
  "linkedin",
  "whatsapp",
  "frontend",
  "backend",
  "react",
  "javascript",
  "python",
  "machine learning",
  "artificial intelligence",
  "ai",
  "node",
  "express",
  "mongodb",
  "mysql",
  "mongoose",
  "html",
  "css",
  "java",
  "flutter",
  "laravel",
  "php",
  "figma",
  "postman",
  "who is",
  "about"

];


/* ==========================================================
   CHATBOT RESPONSE ENGINE
========================================================== */

function getBotReply(raw) {

  const q =
    raw.toLowerCase().trim();


  const includes =
    (...words) =>
      words.some(
        (w) =>
          q.includes(w)
      );


  if (
    !domainKeywords.some(
      (k) =>
        q.includes(k)
    )
  ) {

    return (
      "That question is outside my domain. " +
      "I can help with Maryam Fahim's portfolio, " +
      "education, skills, projects, journey, " +
      "resume, experience and professional " +
      "contact information."
    );

  }


  if (includes("cgpa")) {

    return d.cgpa
      ? `Maryam's CGPA is ${d.cgpa}.`
      : "Maryam's CGPA is not included in the verified portfolio data yet, so I won't guess it.";

  }


  if (includes("semester")) {

    return d.semester
      ? `Maryam is currently in semester ${d.semester}.`
      : "Maryam's current semester is not included in the verified portfolio data yet, so I won't guess it.";

  }


  if (
    includes(
      "degree",
      "education",
      "university",
      "institute",
      "study"
    )
  ) {

    return (
      "Maryam is pursuing BS Computer Science " +
      "at COMSATS University Islamabad, Vehari, " +
      "from 2023–2027. Her earlier education " +
      "includes FSc Pre-Engineering at Government " +
      "Graduate College, Burewala (2021–2023) " +
      "and Matric at Allied School Canal Campus, " +
      "Burewala (2019–2021)."
    );

  }


  if (
    includes(
      "skill",
      "technology",
      "tech",
      "react",
      "python",
      "javascript",
      "machine learning",
      "artificial intelligence"
    )
  ) {

    return (
      "Maryam's portfolio focuses on HTML5, CSS3, " +
      "JavaScript, responsive design, Node.js, " +
      "Express.js, REST APIs, authentication, " +
      "MongoDB, MySQL, Mongoose, Machine Learning, " +
      "Python, Data Processing, React, Vite, Git, " +
      "GitHub, VS Code, Postman, Figma and Linux Basics."
    );

  }


  if (
    includes("project")
  ) {

    return (
      `Maryam's featured portfolio projects include ` +
      `an AI Project in development, a Full Stack Web App, ` +
      `and a Mobile/SaaS project. Her project work also ` +
      `includes ${d.additionalProjects.join(", ")}.`
    );

  }


  if (
    includes("journey")
  ) {

    return (
      "Maryam's journey shown on the portfolio timeline " +
      "starts with programming in 2022, web development " +
      "in 2023, advanced technologies in 2024, practical " +
      "portfolio development in 2025, and a future goal " +
      "of becoming an AI Engineer."
    );

  }


  if (
    includes(
      "resume",
      "cv"
    )
  ) {

    return (
      "Maryam's resume is available in the Resume " +
      "section, where you can view it or download the PDF."
    );

  }


  if (
    includes(
      "contact",
      "email",
      "github",
      "linkedin",
      "whatsapp"
    )
  ) {

    return (
      `You can contact Maryam at ${d.email}, ` +
      "or visit her GitHub and LinkedIn profiles " +
      "from the Contact section."
    );

  }


  if (
    includes(
      "who is",
      "maryam",
      "about"
    )
  ) {

    return (
      "Maryam Fahim is a Computer Science " +
      "undergraduate and aspiring AI Engineer & " +
      "Full Stack Developer focused on Artificial " +
      "Intelligence, Machine Learning, modern web " +
      "development and interactive digital experiences."
    );

  }


  return (
    "I can help with Maryam's portfolio, education, " +
    "skills, projects, journey, resume and professional " +
    "contact information. Please ask me one of those."
  );

}


/* ==========================================================
   CHATBOT
========================================================== */

function Chatbot() {

  const [open, setOpen] =
    useState(false);

  const [input, setInput] =
    useState("");


  const [messages, setMessages] =
    useState([

      {
        from: "bot",

        text:
          "Hello 👋 I'm Maryam AI. Ask me about Maryam's skills, education, projects, journey, resume or professional background."

      }

    ]);


  const inputRef =
    useRef(null);

  const bodyRef =
    useRef(null);


  /* Focus input */

  useEffect(() => {

    if (open) {

      setTimeout(() => {

        inputRef.current?.focus();

      }, 80);

    }

  }, [open]);


  /* Scroll chat */

  useEffect(() => {

    bodyRef.current?.scrollTo({

      top:
        bodyRef.current.scrollHeight,

      behavior:
        "smooth"

    });

  }, [messages]);


  /* Send */

  const send = () => {

    const text =
      input.trim();


    if (!text) {
      return;
    }


    setMessages(
      (prev) => [

        ...prev,

        {
          from: "user",
          text
        },

        {
          from: "bot",
          text: getBotReply(text)
        }

      ]
    );


    setInput("");


    setTimeout(() => {

      inputRef.current?.focus();

    }, 0);

  };


  return (

    <div className="ai-chatbot">


      {/* TOGGLE */}

      <button
        className="chat-toggle"
        aria-label="Open Maryam AI"
        onClick={() =>
          setOpen(
            (value) => !value
          )
        }
      >

        <i className="fas fa-robot" />

      </button>


      {/* CHAT WINDOW */}

      <div
        className={`chat-window ${
          open ? "active" : ""
        }`}
      >


        {/* HEADER */}

        <div className="chat-header">


          <div className="chat-header-left">


            <div className="header-avatar">

              <i className="fas fa-robot" />

            </div>


            <div>

              <h3>
                Maryam AI
              </h3>

              <span>

                <span className="status-dot" />

                Online Assistant

              </span>

            </div>


          </div>


          <button
            className="chat-close"
            aria-label="Close chat"
            onClick={() =>
              setOpen(false)
            }
          >
            ×
          </button>


        </div>


        {/* BODY */}

        <div
          className="chat-body"
          ref={bodyRef}
        >

          {messages.map(
            (m, i) => (

              <div
                className={`message-row ${
                  m.from === "user"
                    ? "user-row"
                    : "bot-row"
                }`}
                key={i}
              >


                {m.from === "bot" && (

                  <div className="msg-avatar">

                    <i className="fas fa-robot" />

                  </div>

                )}


                <div className="message-col">


                  <div
                    className={
                      m.from === "bot"
                        ? "bot-message"
                        : "user-message"
                    }
                  >

                    {m.text}

                  </div>


                </div>


              </div>

            )
          )}

        </div>


        {/* INPUT */}

        <form
          className="chat-input"
          onSubmit={(e) => {

            e.preventDefault();

            send();

          }}
        >


          <input
            ref={inputRef}
            value={input}
            onChange={(e) =>
              setInput(
                e.target.value
              )
            }
            type="text"
            placeholder="Ask about Maryam..."
            aria-label="Ask Maryam AI"
          />


          <button
            type="submit"
            aria-label="Send message"
          >

            <i className="fas fa-paper-plane" />

          </button>


        </form>


      </div>

    </div>

  );

}


/* ==========================================================
   MAIN APP
========================================================== */

export default function App() {


  /* ========================================================
     SCROLL REVEAL
  ======================================================== */

  useEffect(() => {

    const observer =
      new IntersectionObserver(

        (entries) => {

          entries.forEach(
            (entry) => {

              if (
                entry.isIntersecting
              ) {

                entry.target.classList.add(
                  "active"
                );

              }

            }
          );

        },

        {
          threshold: 0.12
        }

      );


    const revealElements =
      document.querySelectorAll(
        ".reveal"
      );


    revealElements.forEach(
      (el) =>
        observer.observe(el)
    );


    return () =>
      observer.disconnect();

  }, []);


  return (

    <>

      <CustomCursor />

      <Background />

      <Header />


      <main>

        <Hero />

        <Mission />

        <AIDashboard />

        <Journey />

        <Skills />

        <Education />

        <Projects />

        <Resume />

        <Contact />

      </main>


      <Footer />

      <Chatbot />

    </>

  );

}