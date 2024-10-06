const questions = [
  {
    question: "What is the goal of SDG 1?",
    options: [
      "End poverty in all its forms everywhere",
      "Ensure healthy lives and promote well-being for all",
      "Ensure availability and sustainable management of water",
      "Achieve gender equality and empower all women and girls"
    ],
    answer: 0,
    sdg: "SDG 1: No Poverty"
  },
  {
    question: "Which SDG focuses on climate action?",
    options: [
      "SDG 5: Gender Equality",
      "SDG 10: Reduced Inequalities",
      "SDG 13: Climate Action",
      "SDG 17: Partnerships for the Goals"
    ],
    answer: 2,
    sdg: "SDG 13: Climate Action"
  }
  // Add other questions similarly
];

let currentQuestion = 0;
let selectedOption = null;
let score = 0;  // Track the user's score
const questionEl = document.querySelector('.question');
const optionsEl = document.querySelector('.options');
const nextButton = document.querySelector('.next-button');
const resultEl = document.querySelector('.result');

function loadQuestion() {
  const q = questions[currentQuestion];
  questionEl.textContent = q.question;
  optionsEl.innerHTML = '';
  resultEl.textContent = '';
  q.options.forEach((option, index) => {
    const li = document.createElement('li');
    li.textContent = option;
    li.onclick = () => selectOption(index);
    optionsEl.appendChild(li);
  });
  nextButton.style.display = 'none';
}

function selectOption(index) {
  selectedOption = index;
  const options = optionsEl.querySelectorAll('li');
  options.forEach(option => option.classList.remove('selected'));
  options[index].classList.add('selected');
  nextButton.style.display = 'inline-block';
}

nextButton.onclick = () => {
  const correctAnswer = questions[currentQuestion].answer;
  const options = optionsEl.querySelectorAll('li');
  if (selectedOption === correctAnswer) {
    options[selectedOption].classList.add('correct');
    resultEl.textContent = 'Correct!';
    score++;  // Increment score for correct answer
  } else {
    options[selectedOption].classList.add('incorrect');
    options[correctAnswer].classList.add('correct');
    resultEl.textContent = `Incorrect! The correct answer is: ${questions[currentQuestion].options[correctAnswer]}`;
  }
  nextButton.style.display = 'none';
  setTimeout(() => {
    if (currentQuestion < questions.length - 1) {
      currentQuestion++;
      loadQuestion();
    } else {
      // After the last question, redirect to the score page
      window.location.href = `quiz-score.html?score=${score}&total=${questions.length}`;
    }
  }, 2000);
};

loadQuestion();
