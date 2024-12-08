document.addEventListener("DOMContentLoaded", function () {
    const tabs = document.querySelectorAll(".tab-link");
    const contents = document.querySelectorAll(".tab-content");

    tabs.forEach(tab => {
        tab.addEventListener("click", function () {
            // Remove active class from all tabs
            tabs.forEach(t => t.classList.remove("active"));

            // Hide all tab contents by setting display: none
            contents.forEach(content => {
                content.classList.remove("active");
                content.style.display = 'none';
            });

            // Add active class to the clicked tab and corresponding content
            tab.classList.add("active");

            const activeContent = document.getElementById(tab.dataset.tab);
            activeContent.classList.add("active");
            activeContent.style.display = 'block';  // Explicitly show the clicked content
        });
    });
});
