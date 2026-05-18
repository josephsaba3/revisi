(() => {
  document.querySelectorAll("[data-mobile-menu]").forEach((menu) => {
    const toggle = menu.querySelector("[data-mobile-menu-toggle]");
    const panel = menu.querySelector("[data-mobile-menu-panel]");
    if (!toggle || !panel) return;

    toggle.addEventListener("click", () => {
      const isOpen = menu.classList.toggle("is-menu-open");
      toggle.setAttribute("aria-expanded", String(isOpen));
      toggle.setAttribute("aria-label", isOpen ? "Close menu" : "Open menu");
    });
  });

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

  document.addEventListener("click", async (event) => {
    const exportButton = event.target.closest("[data-export-pdf]");
    if (exportButton) {
      window.print();
      return;
    }

    const shareButton = event.target.closest("[data-share-report]");
    if (!shareButton) return;

    const original = shareButton.textContent;
    const shareData = {
      title: document.title || "Revisi audit report",
      text: "Revisi audit report",
      url: window.location.href,
    };

    try {
      if (navigator.share) {
        await navigator.share(shareData);
      } else {
        await navigator.clipboard.writeText(window.location.href);
        shareButton.textContent = "Link copied";
      }
    } catch (error) {
      if (error?.name !== "AbortError") {
        shareButton.textContent = "Share failed";
      }
    } finally {
      window.setTimeout(() => {
        shareButton.textContent = original;
      }, 1400);
    }
  });

  document.addEventListener("click", (event) => {
    document.querySelectorAll(".action-menu[open]").forEach((menu) => {
      if (menu.contains(event.target)) return;
      menu.removeAttribute("open");
    });
  });

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    document.querySelectorAll(".action-menu[open]").forEach((menu) => {
      menu.removeAttribute("open");
    });
  });

  document.querySelectorAll(".action-menu a, .action-menu button").forEach((item) => {
    item.addEventListener("click", () => {
      item.closest(".action-menu")?.removeAttribute("open");
    });
  });

  document.addEventListener("click", (event) => {
    const trigger = event.target.closest("[data-finding-trigger]");
    if (!trigger) return;

    const card = document.getElementById(trigger.dataset.findingTrigger || "");
    if (!card) return;

    const isOpen = trigger.getAttribute("aria-expanded") === "true";
    document.querySelectorAll("[data-finding-trigger][aria-expanded='true']").forEach((openTrigger) => {
      if (openTrigger === trigger) return;
      openTrigger.setAttribute("aria-expanded", "false");
      const openCard = document.getElementById(openTrigger.dataset.findingTrigger || "");
      if (openCard) openCard.hidden = true;
    });

    trigger.setAttribute("aria-expanded", String(!isOpen));
    card.hidden = isOpen;
  });

  document.querySelectorAll("[data-scorecard-toggle]").forEach((toggle) => {
    const workspace = toggle.closest(".audit-workspace");
    if (!workspace) return;

    const saved = window.localStorage.getItem("revisi-scorecard-collapsed") === "true";

    function setCollapsed(isCollapsed) {
      workspace.classList.toggle("is-scorecard-collapsed", isCollapsed);
      toggle.setAttribute("aria-pressed", String(isCollapsed));
      toggle.setAttribute("aria-label", isCollapsed ? "Expand voice scorecard" : "Collapse voice scorecard");
      window.localStorage.setItem("revisi-scorecard-collapsed", String(isCollapsed));
    }

    setCollapsed(saved);

    toggle.addEventListener("click", () => {
      setCollapsed(!workspace.classList.contains("is-scorecard-collapsed"));
    });
  });

  document.querySelectorAll("[data-pages-toggle]").forEach((toggle) => {
    const workspace = toggle.closest(".audit-workspace");
    if (!workspace) return;

    const saved = window.localStorage.getItem("revisi-pages-collapsed") === "true";

    function setCollapsed(isCollapsed) {
      workspace.classList.toggle("is-pages-collapsed", isCollapsed);
      toggle.setAttribute("aria-pressed", String(isCollapsed));
      toggle.setAttribute("aria-label", isCollapsed ? "Expand pages sidebar" : "Collapse pages sidebar");
      window.localStorage.setItem("revisi-pages-collapsed", String(isCollapsed));
    }

    setCollapsed(saved);

    toggle.addEventListener("click", () => {
      setCollapsed(!workspace.classList.contains("is-pages-collapsed"));
    });
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
  const log = document.getElementById("log");
  const progressBar = document.getElementById("progress-bar");
  const loaderError = document.getElementById("loader-error");
  const loaderErrorText = document.getElementById("loader-error-text");
  const loaderRetry = document.getElementById("loader-retry");
  const loaderBack = document.getElementById("loader-back");

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

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (submitBtn) submitBtn.disabled = true;
    if (!loader) return;
    loader.classList.add("on");
    loader.setAttribute("aria-hidden", "false");
    clearLoaderError();
    renderProgress({
      status: "queued",
      completed_steps: 0,
      steps: [{ label: "Starting the scan", status: "running", elapsed_seconds: null }],
    });

    try {
      const response = await fetch("/scan", {
        method: "POST",
        body: new FormData(form),
        headers: { Accept: "application/json" },
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(data.error || "The scan could not be started.");
      }
      if (!data.job_id) {
        throw new Error("The scan did not return a job id.");
      }
      pollProgress(data.job_id);
    } catch (error) {
      showLoaderError(error.message || "The scan failed before it could start.");
    }
  });

  async function pollProgress(jobId) {
    try {
      const response = await fetch(`/scan/progress/${encodeURIComponent(jobId)}`, {
        headers: { Accept: "application/json" },
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(data.error || "Could not read scan progress.");
      }
      renderProgress(data);

      if (data.status === "done" && data.report_url) {
        window.location.assign(data.report_url);
        return;
      }
      if (data.status === "error") {
        showLoaderError(data.error || "The scan failed.");
        return;
      }
      window.setTimeout(() => pollProgress(jobId), 700);
    } catch (error) {
      showLoaderError(error.message || "Could not read scan progress.");
    }
  }

  function renderProgress(data) {
    const steps = data.steps || [];
    if (log) {
      log.innerHTML = steps.map((step) => {
        const status = step.status || "pending";
        const label = step.label || "Working";
        const elapsed = formatElapsed(step.elapsed_seconds);
        const rowClass = status === "done" ? "row done" : status === "running" ? "row on" : status === "error" ? "row error" : "row";
        const marker = status === "done" ? "done" : status === "running" ? "now" : status === "error" ? "stop" : "wait";
        const suffix = step.key === "models" && status === "running" ? " This is usually the longest step." : "";
        return `<div class="${rowClass}"><span class="num">${marker}</span><span>${escapeHtml(label + suffix)}</span><span class="t">${elapsed}</span></div>`;
      }).join("");
    }

    if (progressBar) {
      const total = Math.max(steps.length, 1);
      const completed = data.completed_steps || steps.filter((step) => step.status === "done").length;
      progressBar.style.width = `${Math.min(100, Math.round((completed / total) * 100))}%`;
    }
  }

  function formatElapsed(seconds) {
    if (seconds === null || seconds === undefined) return "--:--";
    const safeSeconds = Math.max(0, Math.round(seconds));
    const minutes = String(Math.floor(safeSeconds / 60)).padStart(2, "0");
    const remainder = String(safeSeconds % 60).padStart(2, "0");
    return `${minutes}:${remainder}`;
  }

  function showLoaderError(message) {
    if (submitBtn) submitBtn.disabled = false;
    if (loaderErrorText) loaderErrorText.textContent = message;
    if (loaderError) loaderError.hidden = false;
  }

  function clearLoaderError() {
    if (loaderError) loaderError.hidden = true;
    if (loaderErrorText) loaderErrorText.textContent = "";
  }

  loaderRetry?.addEventListener("click", () => form.requestSubmit());
  loaderBack?.addEventListener("click", () => {
    loader?.classList.remove("on");
    loader?.setAttribute("aria-hidden", "true");
    if (submitBtn) submitBtn.disabled = validateUrl(state.url) !== true;
  });

  if (state.url) urlInput.value = state.url;
  renderUrlState();
  updateSubmitState();
})();
