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

  button.addEventListener("click", async () => {
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
      if (status) status.textContent = "audio channel failed; visual signal only";
      window.setTimeout(() => setLaughing(button, false), 1800);
    }
  });
}

document.querySelectorAll("[data-audio-target]").forEach(bindAudioButton);
