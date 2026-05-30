// GHOSTLIGHT PROTOCOL
// Public surface script.

console.log("GHOSTLIGHT PROTOCOL // status: listening");
console.log("instruction: do not force the lock; understand the signal");

const activeAudio = new Set();

function nearestStatus(button) {
  const panel = button.closest(".audio-panel, .ghost-card, .reward, .failure") || document;
  return panel.querySelector(".audio-status");
}

function stopAudio(audio, button) {
  audio.pause();
  audio.currentTime = 0;
  button.textContent = button.dataset.defaultText || "Play Signal";
  activeAudio.delete(audio);
}

function setLaughing(button, enabled) {
  const selector = button.dataset.laughTarget;
  if (!selector) return;
  document.querySelectorAll(selector).forEach((target) => {
    target.classList.toggle("is-laughing", enabled);
  });
}

function bindAudioButton(button) {
  const targetId = button.dataset.audioTarget;
  if (!targetId) return;

  const audio = document.getElementById(targetId);
  const status = nearestStatus(button);
  button.dataset.defaultText = button.textContent || "Play Signal";

  if (!audio) {
    button.addEventListener("click", () => {
      setLaughing(button, true);
      window.setTimeout(() => setLaughing(button, false), 1800);
      if (status) status.textContent = "audio channel failed; visual signal only";
    });
    return;
  }

  audio.addEventListener("ended", () => {
    button.textContent = button.dataset.defaultText;
    activeAudio.delete(audio);
    setLaughing(button, false);
  });

  audio.addEventListener("error", () => {
    button.textContent = button.dataset.defaultText;
    activeAudio.delete(audio);
    if (status) status.textContent = "audio channel failed; visual signal only";
    window.setTimeout(() => setLaughing(button, false), 1800);
  });

  async function openAudioChannel({ autoplay = false } = {}) {
    if (!audio.paused) {
      stopAudio(audio, button);
      setLaughing(button, false);
      return;
    }

    activeAudio.forEach((other) => {
      other.pause();
      other.currentTime = 0;
    });
    activeAudio.clear();
    document.querySelectorAll("[data-audio-target]").forEach((otherButton) => {
      otherButton.textContent = otherButton.dataset.defaultText || "Play Signal";
      setLaughing(otherButton, false);
    });

    setLaughing(button, true);
    audio.currentTime = 0;
    try {
      await audio.play();
      activeAudio.add(audio);
      button.textContent = button.dataset.playingText || "Pause Signal";
      if (status) status.textContent = "audio channel open";
    } catch {
      if (status) {
        status.textContent = autoplay
          ? "autoplay blocked by browser; tap Play Signal"
          : "audio channel failed; visual signal only";
      }
      window.setTimeout(() => setLaughing(button, false), 1800);
    }
  }

  button.addEventListener("click", () => openAudioChannel());
  button.openAudioChannel = openAudioChannel;
}

function cleanPacket(value) {
  return String(value || "").trim().replaceAll(" ", "_");
}

function addBranchAnswerForm() {
  const card = document.querySelector(".ghost-card");
  if (!card || document.getElementById("branch-answer-form")) return;

  const page = window.location.pathname.split("/").pop() || "";
  if (!(page === "start.html" || page.indexOf("start_gate_") === 0)) return;

  const isStart = page === "start.html";
  const prefix = isStart ? "start_gate_" : "start_reward_";
  const label = isStart ? "receiver packet" : "archive key";
  const hint = isStart ? "A" : "recovered_key";

  const section = document.createElement("section");
  section.className = "gate branch-answer-panel";
  section.innerHTML = '<h2>receiver input</h2><p>Enter the ' + label + '.</p><form id="branch-answer-form"><label for="branch-answer">answer packet</label><br><input id="branch-answer" name="answer" type="text" autocomplete="off" spellcheck="false" class="answer-input" placeholder="' + hint + '"> <button class="audio-button" type="submit">submit packet</button></form><p id="branch-answer-status" class="audio-status" aria-live="polite"></p>';

  const nav = card.querySelector(".nav-links");
  if (nav) card.insertBefore(section, nav);
  else card.appendChild(section);

  const form = document.getElementById("branch-answer-form");
  const input = document.getElementById("branch-answer");
  const status = document.getElementById("branch-answer-status");

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const packet = cleanPacket(input.value);
    if (!packet) {
      status.textContent = "empty packet";
      return;
    }
    status.textContent = "routing packet";
    window.location.href = prefix + packet + ".html";
  });
}

document.querySelectorAll("[data-audio-target]").forEach(bindAudioButton);
addBranchAnswerForm();

window.addEventListener("load", () => {
  const firstButton = document.querySelector("[data-audio-target]");
  if (firstButton && typeof firstButton.openAudioChannel === "function") {
    firstButton.openAudioChannel({ autoplay: true });
  }
});