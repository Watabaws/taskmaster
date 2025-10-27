// Fetch and display tasks
function loadTasks() {
  fetch('/api/tasks')
    .then(res => res.json())
    .then(tasks => {
      const list = document.getElementById('tasks-list');
      list.innerHTML = '';
      tasks.forEach(task => {
        const li = document.createElement('li');
        li.textContent = `${task.title} [${task.completed ? "Done" : "Pending"}]`;
        list.appendChild(li);
      });
    });
}

// Add new task
document.getElementById('task-form').onsubmit = function(e) {
  e.preventDefault();
  const title = document.getElementById('task-input').value;
  fetch('/api/tasks', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title })
  })
  .then(res => res.json())
  .then(task => {
    document.getElementById('task-input').value = '';
    loadTasks();
  });
};

// Initial load
loadTasks();