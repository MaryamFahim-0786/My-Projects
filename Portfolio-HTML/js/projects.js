document.addEventListener("DOMContentLoaded",()=>{

    const projectContainer =
    document.querySelector(".project-grid");


    if(projectContainer){

        projectContainer.innerHTML = "";


        projectsData.forEach(project=>{


            const card = document.createElement("div");

            card.classList.add("project-card");


            card.innerHTML = `

            <h3>
            ${project.icon} ${project.title}
            </h3>


            <p>
            ${project.description}
            </p>


            <span class="gradient-text">
            ${project.status}
            </span>

            `;


            projectContainer.appendChild(card);


        });

    }


});