document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Render (or re-render) a single activity card's contents
  function renderActivityCard(card, name, details) {
    const spotsLeft = details.max_participants - details.participants.length;
    const participantItems = details.participants.length > 0
      ? details.participants.map(p => `<li><span class="participant-email">${p}</span><button class="delete-participant" data-email="${p}" title="Unregister">&#10005;</button></li>`).join("")
      : "<li class='no-participants'>No participants yet</li>";

    card.innerHTML = `
      <h4>${name}</h4>
      <p>${details.description}</p>
      <p><strong>Schedule:</strong> ${details.schedule}</p>
      <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
      <div class="participants-section">
        <p class="participants-title">Participants (${details.participants.length}/${details.max_participants}):</p>
        <ul class="participants-list">${participantItems}</ul>
      </div>
    `;
  }

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";
        activityCard.dataset.activity = name;

        renderActivityCard(activityCard, name, details);
        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";

        // Instantly update the matching activity card
        const card = activitiesList.querySelector(`[data-activity="${CSS.escape(activity)}"]`);
        if (card) {
          const participantsList = card.querySelector(".participants-list");
          const noParticipants = participantsList.querySelector(".no-participants");
          if (noParticipants) noParticipants.remove();

          const newItem = document.createElement("li");
          newItem.innerHTML = `<span class="participant-email">${email}</span><button class="delete-participant" data-email="${email}" title="Unregister">&#10005;</button>`;
          newItem.classList.add("participant-new");
          participantsList.appendChild(newItem);

          // Update count & availability
          const countEl = card.querySelector(".participants-title");
          const availEl = card.querySelectorAll("p")[2];
          const currentCount = participantsList.querySelectorAll("li").length;
          const maxMatch = countEl.textContent.match(/\/(\d+)/);
          const max = maxMatch ? parseInt(maxMatch[1]) : "?";
          countEl.textContent = `Participants (${currentCount}/${max}):`;
          availEl.innerHTML = `<strong>Availability:</strong> ${max - currentCount} spots left`;

          // Fade out the highlight after a moment
          setTimeout(() => newItem.classList.remove("participant-new"), 2000);
        }

        signupForm.reset();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Handle delete (unregister) participant clicks
  activitiesList.addEventListener("click", async (event) => {
    const btn = event.target.closest(".delete-participant");
    if (!btn) return;

    const li = btn.closest("li");
    const card = btn.closest(".activity-card");
    const activity = card?.dataset.activity;
    const email = btn.dataset.email;
    if (!activity || !email) return;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        { method: "DELETE" }
      );

      if (response.ok) {
        const participantsList = card.querySelector(".participants-list");
        li.remove();

        const remaining = participantsList.querySelectorAll("li:not(.no-participants)").length;
        const countEl = card.querySelector(".participants-title");
        const availEl = card.querySelectorAll("p")[2];
        const maxMatch = countEl.textContent.match(/\/(\d+)/);
        const max = maxMatch ? parseInt(maxMatch[1]) : "?";
        countEl.textContent = `Participants (${remaining}/${max}):`;
        availEl.innerHTML = `<strong>Availability:</strong> ${max - remaining} spots left`;

        if (remaining === 0) {
          const noItem = document.createElement("li");
          noItem.className = "no-participants";
          noItem.textContent = "No participants yet";
          participantsList.appendChild(noItem);
        }
      }
    } catch (error) {
      console.error("Error unregistering participant:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
