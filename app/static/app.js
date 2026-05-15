document.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-copy]");
  if (!button) return;

  const original = button.textContent;
  try {
    await navigator.clipboard.writeText(button.dataset.copy || "");
    button.textContent = "Copied";
    window.setTimeout(() => {
      button.textContent = original;
    }, 1400);
  } catch {
    button.textContent = "Copy failed";
  }
});
