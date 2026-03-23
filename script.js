const optionInput = document.querySelector('#optionInput');
const wheel = document.querySelector('#wheel');
const resultText = document.querySelector('#resultText');
const updateButton = document.querySelector('#updateButton');
const spinButton = document.querySelector('#spinButton');
const sampleButton = document.querySelector('#sampleButton');
const shuffleButton = document.querySelector('#shuffleButton');
const clearButton = document.querySelector('#clearButton');

const palette = [
  ['#7c5cff', '#5d44d4'],
  ['#27c6ff', '#1799ff'],
  ['#ff7aa2', '#ff5d7d'],
  ['#ffb84c', '#ff8f3f'],
  ['#63e6be', '#2dcf9f'],
  ['#a78bfa', '#8b5cf6'],
  ['#f472b6', '#ec4899'],
  ['#38bdf8', '#0ea5e9'],
];

const sampleOptions = ['今天吃披薩', '今天吃壽司', '今天吃火鍋', '今天吃沙拉', '今天喝果汁', '今天喝氣泡水'];

let options = [];
let currentRotation = 0;
let isSpinning = false;

function normalizeOptions(rawValue) {
  return rawValue
    .split('\n')
    .map((item) => item.trim())
    .filter(Boolean)
    .slice(0, 16);
}

function buildWheel(nextOptions) {
  options = nextOptions;
  wheel.innerHTML = '';
  wheel.style.transform = `rotate(${currentRotation}deg)`;

  if (options.length < 2) {
    resultText.textContent = '請至少輸入兩個選項，才可以開始旋轉。';
    spinButton.disabled = true;
    return;
  }

  spinButton.disabled = false;
  resultText.textContent = `目前共有 ${options.length} 個選項，點擊「開始旋轉」抽出結果。`;

  const segmentAngle = 360 / options.length;

  options.forEach((label, index) => {
    const segment = document.createElement('div');
    segment.className = 'wheel-segment';
    segment.style.transform = `rotate(${index * segmentAngle}deg)`;
    segment.style.background = `linear-gradient(135deg, ${palette[index % palette.length][0]}, ${palette[index % palette.length][1]})`;

    const text = document.createElement('span');
    text.className = 'segment-label';
    text.textContent = label;
    text.style.transform = `rotate(${segmentAngle / 2}deg) translate(18%, -50%)`;

    segment.appendChild(text);
    wheel.appendChild(segment);
  });
}

function updateWheelFromInput() {
  buildWheel(normalizeOptions(optionInput.value));
}

function spinWheel() {
  if (isSpinning || options.length < 2) {
    return;
  }

  isSpinning = true;
  spinButton.disabled = true;
  updateButton.disabled = true;

  const winnerIndex = Math.floor(Math.random() * options.length);
  const segmentAngle = 360 / options.length;
  const pointerOffset = 270;
  const targetAngle = pointerOffset - (winnerIndex * segmentAngle + segmentAngle / 2);
  const extraTurns = 360 * (5 + Math.floor(Math.random() * 3));

  currentRotation += extraTurns + targetAngle - (currentRotation % 360);
  wheel.style.transform = `rotate(${currentRotation}deg)`;
  resultText.textContent = '轉盤旋轉中，祝你好運…';

  window.setTimeout(() => {
    resultText.textContent = `恭喜抽中：${options[winnerIndex]}`;
    spinButton.disabled = false;
    updateButton.disabled = false;
    isSpinning = false;
  }, 5600);
}

function shuffleOptions() {
  const shuffled = [...normalizeOptions(optionInput.value)].sort(() => Math.random() - 0.5);
  optionInput.value = shuffled.join('\n');
  updateWheelFromInput();
}

updateButton.addEventListener('click', updateWheelFromInput);
spinButton.addEventListener('click', spinWheel);
sampleButton.addEventListener('click', () => {
  optionInput.value = sampleOptions.join('\n');
  updateWheelFromInput();
});
shuffleButton.addEventListener('click', shuffleOptions);
clearButton.addEventListener('click', () => {
  optionInput.value = '';
  updateWheelFromInput();
});
optionInput.addEventListener('input', () => {
  if (optionInput.value.trim() === '') {
    buildWheel([]);
  }
});

updateWheelFromInput();
