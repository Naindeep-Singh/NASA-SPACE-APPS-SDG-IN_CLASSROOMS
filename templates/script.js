// Smooth scrolling for internal links (if you add anchor links later)
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      e.preventDefault();
  
      document.querySelector(this.getAttribute('href')).scrollIntoView({
        behavior: 'smooth'
      });
    });
  });
  
  // Placeholder functionality for SDG Score button
  document.querySelector('button:contains("SDG Score")').addEventListener('click', function() {
    alert('SDG Score page is under construction!');
  });
  
  // Placeholder functionality for Quiz button
  document.querySelector('button:contains("Quiz")').addEventListener('click', function() {
    alert('Quiz page is under construction!');
  });
  // JavaScript to handle the redirection for Mentor and Student buttons

document.getElementById('mentorBtn').addEventListener('click', function() {
    window.location.href = 'mentor-login.html'; // Redirects to the Mentor login page
  });
  
  document.getElementById('studentBtn').addEventListener('click', function() {
    window.location.href = 'student-login.html'; // Redirects to the Student login page
  });
  
  