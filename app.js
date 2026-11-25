const form = document.getElementById("advisor-form");
const nameInput = document.getElementById("student-name");
const apiKeyInput = document.getElementById("api-key");
const rowsEl = document.getElementById("subject-rows");
const addRowBtn = document.getElementById("add-row-btn");
const errorEl = document.getElementById("error-msg");
const submitBtn = document.getElementById("submit-btn");

const placeholderEl = document.getElementById("placeholder");
const resultBoxEl = document.getElementById("result-box");
const resAvgEl = document.getElementById("res-avg");
const resGradeEl = document.getElementById("res-grade");
const resGpaEl = document.getElementById("res-gpa");
const resStrongEl = document.getElementById("res-strong");
const resWeakEl = document.getElementById("res-weak");
const resAdviceEl = document.getElementById("res-advice");
const resSourceEl = document.getElementById("res-source");

function addSubjectRow(subject = "", score = "") {
  const row = document.createElement("div");
  row.className = "subject-row";

  const subjInput = document.createElement("input");
  subjInput.type = "text";
  subjInput.placeholder = "Subject";
  subjInput.value = subject;
  subjInput.required = true;

  const scoreInput = document.createElement("input");
  scoreInput.type = "number";
  scoreInput.min = "0";
  scoreInput.max = "100";
  scoreInput.step = "0.1";
  scoreInput.placeholder = "Score";
  scoreInput.value = score;
  scoreInput.required = true;

  const removeBtn = document.createElement("button");
  removeBtn.type = "button";
  removeBtn.className = "remove-btn";
  removeBtn.textContent = "×";
  removeBtn.addEventListener("click", () => {
    if (rowsEl.children.length > 1) row.remove();
  });

  row.append(subjInput, scoreInput, removeBtn);
  rowsEl.appendChild(row);
}

function getGradeAndGpa(avg) {
  if (avg >= 90) return { letter: "A", gpa: 4.0 };
  if (avg >= 80) return { letter: "B", gpa: 3.0 };
  if (avg >= 70) return { letter: "C", gpa: 2.0 };
  if (avg >= 60) return { letter: "D", gpa: 1.0 };
  return { letter: "F", gpa: 0.0 };
}

function buildOfflineAdvice(name, avg, letter, strong, weak) {
  let standing = "Needs immediate focus—let's build a structured recovery plan.";
  if (avg >= 90) standing = "Excellent work! You are performing at an honors level.";
  else if (avg >= 80) standing = "Strong performance! You have a solid grasp of the material.";
  else if (avg >= 70) standing = "Good progress, with clear room to push into the B/A range.";
  else if (avg >= 60) standing = "You are passing, but consistent review will make a big difference.";

  return [
    `AI Study Coach Report for ${name}`,
    `Overall: ${avg.toFixed(2)} (${letter}) — ${standing}`,
    "",
    "Recommended Action Plan:",
    `1. Prioritize ${weak[0]} (${weak[1].toFixed(1)}/100) with 30–45 minutes of active recall daily.`,
    `2. Leverage your momentum in ${strong[0]} (${strong[1].toFixed(1)}/100) to keep confidence high.`,
    "3. Practice past problems under timed conditions and review mistakes in a short error log.",
  ].join("\n");
}

async function fetchGeminiAdvice(apiKey, name, scores, avg, letter, strong, weak) {
  const prompt = `You are a supportive academic coach. Give a concise 4-line study plan for ${name} based on these scores: ${JSON.stringify(scores)}. Average: ${avg.toFixed(2)} (${letter}). Strongest: ${strong[0]} (${strong[1]}). Weakest: ${weak[0]} (${weak[1]}).`;
  const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${encodeURIComponent(apiKey)}`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }] }),
  });
  if (!res.ok) throw new Error("API error");
  const data = await res.json();
  return data.candidates[0].content.parts[0].text.trim();
}

addRowBtn.addEventListener("click", () => addSubjectRow());

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  errorEl.hidden = true;

  const name = nameInput.value.trim();
  if (!name) {
    errorEl.textContent = "Student name cannot be empty.";
    errorEl.hidden = false;
    return;
  }

  const scores = {};
  for (const row of rowsEl.querySelectorAll(".subject-row")) {
    const [subjEl, scoreEl] = row.querySelectorAll("input");
    const subj = subjEl.value.trim();
    const val = Number(scoreEl.value);
    if (!subj || Number.isNaN(val) || val < 0 || val > 100) {
      errorEl.textContent = "Please enter valid subject names and scores (0–100).";
      errorEl.hidden = false;
      return;
    }
    scores[subj] = val;
  }

  const entries = Object.entries(scores);
  const avg = entries.reduce((acc, [, v]) => acc + v, 0) / entries.length;
  const { letter, gpa } = getGradeAndGpa(avg);
  const strong = entries.reduce((a, b) => (b[1] > a[1] ? b : a));
  const weak = entries.reduce((a, b) => (b[1] < a[1] ? b : a));

  resAvgEl.textContent = avg.toFixed(2);
  resGradeEl.textContent = letter;
  resGpaEl.textContent = gpa.toFixed(1);
  resStrongEl.textContent = `Strongest: ${strong[0]} (${strong[1]})`;
  resWeakEl.textContent = `Focus Area: ${weak[0]} (${weak[1]})`;

  const apiKey = apiKeyInput.value.trim();
  let advice = "";
  let source = "Built-in Smart Advisor";

  if (apiKey) {
    submitBtn.disabled = true;
    submitBtn.textContent = "Generating with Gemini...";
    try {
      advice = await fetchGeminiAdvice(apiKey, name, scores, avg, letter, strong, weak);
      source = "Gemini API (gemini-2.0-flash)";
    } catch {
      advice = buildOfflineAdvice(name, avg, letter, strong, weak);
      source = "Built-in Smart Advisor (API fallback)";
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Generate AI Study Plan";
    }
  } else {
    advice = buildOfflineAdvice(name, avg, letter, strong, weak);
  }

  resAdviceEl.textContent = advice;
  resSourceEl.textContent = `Source: ${source}`;
  placeholderEl.hidden = true;
  resultBoxEl.hidden = false;
});

addSubjectRow("Math", "88");
addSubjectRow("Python", "94");
addSubjectRow("Statistics", "72");
