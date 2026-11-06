async function loadCourse(jsonUrl) {
  console.log(
    "Hi Hacker! Take whatever you want there is nothing to hide https://github.com/ChakerKhachlek/CKPortfolio"
  );
  document.getElementById("currentYear").textContent = new Date().getFullYear();

  try {
    // Set course title
    const courseTitle = document.getElementById("course-title");
    if (courseTitle) courseTitle.textContent = title;

    // Fetch JSON data
    const res = await fetch(jsonUrl);
    const data = await res.json();

    const container = document.getElementById("course-content");
    const summaryContainer = document.getElementById("course-summary");

    let summaryHTML = "";

    data.modules.forEach((module, moduleIndex) => {
      // Section header
      const sectionId = `section-${moduleIndex}`;
      const sectionTitle = document.createElement("h3");
      sectionTitle.className = "section-title";
      sectionTitle.id = sectionId;
      sectionTitle.textContent = module.title;
      container.appendChild(sectionTitle);

      // Add module to summary
      summaryHTML += `<button class="list-group-item list-group-item-action" data-target="#${sectionId}">${module.title}</button>`;

      // Lessons
      module.lessons.forEach((lesson, lessonIndex) => {
        const itemId = `item-${moduleIndex}-${lessonIndex}`;
        const card = document.createElement("div");
        card.className = "accordion-item p-2 mb-2"; // small spacing between lessons

        // Lesson title button
        const header = document.createElement("h2");
        header.className = "accordion-header";

        const button = document.createElement("button");
        button.className = "accordion-button"; // keep styling
        button.type = "button";
        button.setAttribute("data-bs-toggle", "collapse");
        button.setAttribute("data-bs-target", `#collapse-${itemId}`);
        button.setAttribute("aria-expanded", "true"); // open by default
        button.setAttribute("aria-controls", `collapse-${itemId}`);
        button.textContent = lesson.title;

        header.appendChild(button);
        card.appendChild(header);

        // Lesson body (independent collapsible)
        const collapseDiv = document.createElement("div");
        collapseDiv.id = `collapse-${itemId}`;
        collapseDiv.className = "accordion-collapse collapse show"; // open initially
        collapseDiv.setAttribute("aria-labelledby", `heading-${itemId}`);
        // remove data-bs-parent to allow multiple open

        const body = document.createElement("div");
        body.className = "accordion-body p-2";

        const note = document.createElement("p");
        note.className = "lesson-note";
        note.textContent = lesson.note;

        const pre = document.createElement("pre");
        const code = document.createElement("code");
        code.className = "language-bash"; // or language-php etc.
        code.textContent = lesson.code;

        pre.appendChild(code);
        body.appendChild(pre);
        collapseDiv.appendChild(note);
        collapseDiv.appendChild(body);
        card.appendChild(collapseDiv);

        container.appendChild(card);
      });
    });

    summaryContainer.innerHTML = summaryHTML;

    // Summary click scroll
    const summaryItems = summaryContainer.querySelectorAll(".list-group-item");
    summaryItems.forEach((item) => {
      item.addEventListener("click", () => {
        const targetSelector = item.getAttribute("data-target");
        const targetElement = document.querySelector(targetSelector);
        if (targetElement) {
          targetElement.scrollIntoView({ behavior: "smooth", block: "start" });
          summaryItems.forEach((i) => i.classList.remove("active"));
          item.classList.add("active");
        }
      });
    });

    // Highlight summary on scroll
    window.addEventListener("scroll", () => {
      let currentIndex = 0;
      for (let i = 0; i < summaryItems.length; i++) {
        const targetSelector = summaryItems[i].getAttribute("data-target");
        const targetElement = document.querySelector(targetSelector);
        if (targetElement) {
          const rect = targetElement.getBoundingClientRect();
          if (rect.top <= window.innerHeight / 3) currentIndex = i;
        }
      }
      summaryItems.forEach((item, idx) =>
        item.classList.toggle("active", idx === currentIndex)
      );
    });

    Prism.highlightAll();
  } catch (error) {
    console.error("Failed to load course data:", error);
  }
}
