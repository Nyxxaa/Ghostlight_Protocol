const button = document.querySelector("[data-signal-trigger]");
const statusLine = document.querySelector("[data-signal-status]");
const scriptUrl = new URL(document.currentScript.src);

function playRewardSignal() {
  const clips = [
    "reward_01.wav",
    "reward_02.wav",
    "reward_03.wav",
    "reward_04.wav",
    "reward_05.wav",
    "reward_06.wav",
    "reward_07.wav",
    "reward_08.wav",
    "reward_09.wav",
    "reward_10.wav",
  ];
  const seed = Array.from(window.location.pathname).reduce(
    (total, ch) => total + ch.charCodeAt(0),
    0,
  );
  const clip = clips[seed % clips.length];
  const audioUrl = new URL(`../assets/audio/${clip}`, scriptUrl);
  const audio = new Audio(audioUrl.href);
  audio.addEventListener("ended", () => {
    if (statusLine) statusLine.textContent = "voice signal complete";
  });
  audio.addEventListener("error", () => {
    if (statusLine) statusLine.textContent = "voice signal unavailable";
  });
  audio.play().then(() => {
    if (statusLine) statusLine.textContent = "voice signal playing";
  }).catch(() => {
    if (statusLine) statusLine.textContent = "voice signal blocked";
  });
}

if (button) {
  button.addEventListener("click", playRewardSignal);
}
