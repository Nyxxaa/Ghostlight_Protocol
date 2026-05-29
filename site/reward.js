const button = document.querySelector("[data-signal-trigger]");
const statusLine = document.querySelector("[data-signal-status]");

function playRewardSignal() {
  const AudioContext = window.AudioContext || window.webkitAudioContext;
  if (!AudioContext) {
    if (statusLine) statusLine.textContent = "audio unavailable";
    return;
  }

  const context = new AudioContext();
  const master = context.createGain();
  master.gain.setValueAtTime(0.0001, context.currentTime);
  master.gain.exponentialRampToValueAtTime(0.18, context.currentTime + 0.04);
  master.gain.exponentialRampToValueAtTime(0.0001, context.currentTime + 1.2);
  master.connect(context.destination);

  [196, 293.66, 392, 587.33].forEach((frequency, index) => {
    const osc = context.createOscillator();
    const gain = context.createGain();
    const start = context.currentTime + index * 0.12;
    osc.type = index % 2 ? "triangle" : "sine";
    osc.frequency.setValueAtTime(frequency, start);
    gain.gain.setValueAtTime(0.0001, start);
    gain.gain.exponentialRampToValueAtTime(0.22, start + 0.035);
    gain.gain.exponentialRampToValueAtTime(0.0001, start + 0.5);
    osc.connect(gain);
    gain.connect(master);
    osc.start(start);
    osc.stop(start + 0.55);
  });

  if (statusLine) statusLine.textContent = "reward signal played";
}

if (button) {
  button.addEventListener("click", playRewardSignal);
}
