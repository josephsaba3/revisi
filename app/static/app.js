(() => {
  document.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-copy]");
    if (!button) return;

    const original = button.textContent;
    try {
      await navigator.clipboard.writeText(button.dataset.copy || "");
      button.textContent = "Copied";
    } catch {
      button.textContent = "Copy failed";
    } finally {
      window.setTimeout(() => {
        button.textContent = original;
      }, 1400);
    }
  });

  const form = document.getElementById("scan-form");
  const urlInput = document.getElementById("url-input");
  const urlBox = document.getElementById("url-box");
  const urlHint = document.getElementById("url-hint");
  const urlStatus = document.getElementById("url-status");
  const drop = document.getElementById("drop");
  const fileInput = document.getElementById("file-input");
  const dropIcon = document.getElementById("drop-icon");
  const dropT1 = document.getElementById("drop-t1");
  const dropT2 = document.getElementById("drop-t2");
  const dropMeta = document.getElementById("drop-meta");
  const optionsGrid = document.getElementById("options");
  const depthInput = document.getElementById("depth-input");
  const submitBtn = document.getElementById("submit-btn");
  const loader = document.getElementById("loader");
  const logRows = document.querySelectorAll("#log .row");
  const progressBar = document.getElementById("progress-bar");

  if (!form || !urlInput) return;

  const state = {
    url: urlInput.value.replace(/^https?:\/\//i, ""),
    file: null,
    depth: depthInput ? depthInput.value : "scan",
  };

  const urlRe = /^([a-z0-9-]+\.)+[a-z]{2,}(\/.*)?$/i;

  function validateUrl(raw) {
    const value = raw.trim().replace(/^https?:\/\//i, "");
    if (!value) return null;
    return urlRe.test(value);
  }

  function renderUrlState() {
    const ok = validateUrl(state.url);
    urlBox?.classList.toggle("bad", ok === false);
    urlHint?.classList.remove("ok", "bad");
    urlStatus?.classList.remove("ok", "bad");

    if (ok === null) {
      if (urlHint) urlHint.textContent = "Required";
      if (urlStatus) urlStatus.textContent = "Awaiting";
    } else if (ok) {
      if (urlHint) {
        urlHint.textContent = "Looks good";
        urlHint.classList.add("ok");
      }
      if (urlStatus) {
        urlStatus.textContent = "Ready";
        urlStatus.classList.add("ok");
      }
    } else {
      if (urlHint) {
        urlHint.textContent = "Does not parse as a URL";
        urlHint.classList.add("bad");
      }
      if (urlStatus) {
        urlStatus.textContent = "Check";
        urlStatus.classList.add("bad");
      }
    }
  }

  function updateSubmitState() {
    if (submitBtn) submitBtn.disabled = validateUrl(state.url) !== true;
  }

  urlInput.addEventListener("input", (event) => {
    state.url = event.target.value.replace(/^https?:\/\//i, "");
    if (state.url !== event.target.value) event.target.value = state.url;
    renderUrlState();
    updateSubmitState();
  });

  document.querySelectorAll(".chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      state.url = chip.dataset.url || "";
      urlInput.value = state.url;
      renderUrlState();
      updateSubmitState();
    });
  });

  function escapeHtml(value) {
    return value.replace(/[&<>"']/g, (char) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      "\"": "&quot;",
      "'": "&#39;",
    }[char]));
  }

  function setFile(file) {
    state.file = file;
    drop?.classList.toggle("has-file", Boolean(file));

    if (!dropIcon || !dropT1 || !dropT2 || !dropMeta) return;

    if (file) {
      dropIcon.textContent = "OK";
      dropT1.innerHTML = `<em>${escapeHtml(file.name)}</em>`;
      dropT2.textContent = `${(file.size / 1024).toFixed(1)} KB, ready to cross-reference`;
      dropMeta.innerHTML = '<span>Parsed</span><button type="button" class="clear" id="clear-file">Remove</button>';
      document.getElementById("clear-file")?.addEventListener("click", (event) => {
        event.stopPropagation();
        clearFile();
      });
    } else {
      dropIcon.textContent = "MD";
      dropT1.textContent = "Drop design.md here, or click to pick a file.";
      dropT2.textContent = "We look for headings like Voice, Banned, Tone, Anti-references.";
      dropMeta.innerHTML = "<span>md / mdx / txt</span>";
    }
  }

  function clearFile() {
    if (fileInput) fileInput.value = "";
    setFile(null);
  }

  function isAllowedFile(file) {
    const name = file.name.toLowerCase();
    return [".md", ".mdx", ".txt", ".markdown", ".json"].some((suffix) => name.endsWith(suffix));
  }

  drop?.addEventListener("click", (event) => {
    if (event.target.closest(".clear")) return;
    fileInput?.click();
  });

  fileInput?.addEventListener("change", (event) => {
    const file = event.target.files?.[0];
    if (file) setFile(file);
  });

  drop?.addEventListener("dragover", (event) => {
    event.preventDefault();
    drop.classList.add("dragging");
  });

  drop?.addEventListener("dragleave", () => {
    drop.classList.remove("dragging");
  });

  drop?.addEventListener("drop", (event) => {
    event.preventDefault();
    drop.classList.remove("dragging");
    const file = event.dataTransfer.files?.[0];
    if (file && isAllowedFile(file)) {
      try {
        fileInput.files = event.dataTransfer.files;
      } catch {
        // Some browsers expose FileList as read-only; the visual state still updates.
      }
      setFile(file);
    }
  });

  optionsGrid?.addEventListener("click", (event) => {
    const button = event.target.closest(".opt");
    if (!button) return;
    state.depth = button.dataset.depth || "scan";
    if (depthInput) depthInput.value = state.depth;
    optionsGrid.querySelectorAll(".opt").forEach((option) => {
      option.classList.toggle("on", option === button);
    });
  });

  form.addEventListener("submit", () => {
    if (submitBtn) submitBtn.disabled = true;
    if (!loader) return;
    loader.classList.add("on");
    loader.setAttribute("aria-hidden", "false");
    runLoaderSequence();
  });

  function runLoaderSequence() {
    const total = logRows.length;
    let index = 0;

    const tick = () => {
      if (index > 0) logRows[index - 1].classList.add("done");
      if (index < total) {
        logRows[index].classList.add("on");
        logRows[index].querySelector(".num").textContent = "now";
        for (let row = 0; row < index; row += 1) {
          logRows[row].querySelector(".num").textContent = "done";
        }
        if (progressBar) progressBar.style.width = `${(index / total) * 100}%`;
        index += 1;
        window.setTimeout(tick, 480);
      } else if (progressBar) {
        progressBar.style.width = "100%";
      }
    };

    tick();
  }

  if (state.url) urlInput.value = state.url;
  renderUrlState();
  updateSubmitState();
})();
