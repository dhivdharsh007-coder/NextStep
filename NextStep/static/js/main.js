// ===== SIDEBAR TOGGLE =====
const hamburger = document.getElementById('hamburgerBtn');
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('sidebarOverlay');

if (hamburger) {
  hamburger.addEventListener('click', () => {
    sidebar.classList.toggle('open');
    overlay.classList.toggle('show');
  });
}
if (overlay) {
  overlay.addEventListener('click', () => {
    sidebar.classList.remove('open');
    overlay.classList.remove('show');
  });
}

// ===== REMINDER POPUP =====
const reminders = [];
const reminderModal = document.getElementById('reminderModal');
const reminderMsg = document.getElementById('reminderMsg');
const closeReminder = document.getElementById('closeReminder');
const reminderBtn = document.getElementById('reminderBtn');

function showReminder(text) {
  if (reminderModal && text) {
    reminderMsg.textContent = text;
    reminderModal.classList.add('show');
    setTimeout(() => reminderModal.classList.remove('show'), 8000);
  }
}

if (closeReminder) {
  closeReminder.addEventListener('click', () => reminderModal.classList.remove('show'));
}
if (reminderBtn) {
  reminderBtn.addEventListener('click', () => {
    const goal = reminderBtn.getAttribute('data-goal');
    if (goal && goal.trim() !== '') {
      showReminder(`Reminder: Complete today's practice: ${goal}`);
    } else {
      showReminder("Reminder: Set a short-term goal on your Dashboard!");
    }
  });
}

// ===== DOMAIN BADGE =====
const domainBadge = document.getElementById('domainBadge');
if (domainBadge && !domainBadge.textContent.trim()) {
  domainBadge.style.display = 'none';
}

// ===== ANIMATE CARDS ON SCROLL =====
const observer = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.style.opacity = '1';
      e.target.style.transform = 'translateY(0)';
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.card-ns, .step-card, .company-card, .missing-skill-card').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(20px)';
  el.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
  observer.observe(el);
});

// ===== SCORE CIRCLE ANIMATION =====
const scoreCircle = document.querySelector('.score-circle');
if (scoreCircle) {
  const pct = getComputedStyle(scoreCircle).getPropertyValue('--pct');
  scoreCircle.style.setProperty('--pct', '0deg');
  setTimeout(() => {
    scoreCircle.style.transition = 'all 1.2s cubic-bezier(.4,0,.2,1)';
    scoreCircle.style.setProperty('--pct', pct);
  }, 300);
}
