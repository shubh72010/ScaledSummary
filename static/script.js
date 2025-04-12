document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("videoUrl");
  const output = document.getElementById("summaryOutput");
  const buttons = document.querySelectorAll("button.summary-btn");
  const eggButtons = document.querySelectorAll(".easter-egg");

  buttons.forEach(button => {
    button.addEventListener("click", async () => {
      const url = input.value.trim();
      if (!url) {
        output.innerText = "Please enter a YouTube video URL!";
        return;
      }

      output.innerText = "Summarizing...";
      try {
        const res = await fetch("/summary", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url })
        });
        const data = await res.json();
        output.innerText = data.transcript || data.error || "No transcript found.";
      } catch (err) {
        output.innerText = "Error fetching summary.";
        console.error(err);
      }
    });
  });

  eggButtons.forEach((egg, index) => {
    egg.addEventListener("click", () => {
      const messages = [
        "Easter Egg Unlocked: Purple Potato Mode!",
        "Shhh... this button does secret AI stuff!",
        "Scaled & Icy but make it HTML.",
        "Clancy is watching...",
        "You're 1 click away from multiversal chaos."
      ];
      output.innerText = messages[index % messages.length];
    });
  });
});