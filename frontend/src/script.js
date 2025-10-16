// --- Configuration & DOM Elements ---
const BACKEND_URL = '/api/tasks';
const taskForm = document.getElementById('task-form');
const taskInput = document.getElementById('task-input');
const tasksList = document.getElementById('tasks-list');
const loadingMessage = document.getElementById('loading-message');

// --- Core API Functions ---

/**
 * Fetches all tasks from the backend API (GET).
 */
async function fetchTasks() {
    loadingMessage.textContent = 'Loading tasks...';
    tasksList.classList.add('opacity-50');

    try {
        const response = await fetch(BACKEND_URL, { method: 'GET' });
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

        const tasks = await response.json();
        renderTasks(tasks);

    } catch (error) {
        console.error('Error fetching tasks:', error);
        tasksList.innerHTML = `<p class="text-center text-red-500 p-4">Error loading tasks: ${error.message}. Check backend connection.</p>`;
    } finally {
        tasksList.classList.remove('opacity-50');
        loadingMessage.style.display = 'none';
    }
}

/**
 * Adds a new task to the database via POST request.
 */
async function addTask(event) {
    event.preventDefault();
    const title = taskInput.value.trim();
    if (!title) return;

    const button = document.getElementById('add-button');
    button.textContent = 'Adding...';
    button.disabled = true;

    try {
        const response = await fetch(BACKEND_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: title })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }

        taskInput.value = '';
        await fetchTasks();

    } catch (error) {
        console.error('Error adding task:', error);
        alert(`Failed to add task: ${error.message}`);
    } finally {
        button.textContent = 'Add Task';
        button.disabled = false;
    }
}

/**
 * Deletes a task from the database via DELETE request.
 */
async function deleteTask(id) {
    if (!confirm("Are you sure you want to delete this task?")) return;

    try {
        const response = await fetch(`${BACKEND_URL}/${id}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        await fetchTasks();

    } catch (error) {
        console.error('Error deleting task:', error);
        alert(`Failed to delete task: ${error.message}`);
    }
}

/**
 * Updates a task's title via PUT request.
 */
async function updateTask(id, newTitle) {
    if (!newTitle.trim()) return alert("Task title cannot be empty.");

    try {
        const response = await fetch(`${BACKEND_URL}/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: newTitle })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }

        await fetchTasks();

    } catch (error) {
        console.error('Error updating task:', error);
        alert(`Failed to update task: ${error.message}`);
    }
}


// --- DOM Rendering & Interaction Logic ---

/**
 * Renders the list of tasks to the DOM with interaction buttons.
 */
function renderTasks(tasks) {
    tasksList.innerHTML = '';
    if (tasks.length === 0) {
        tasksList.innerHTML = '<p class="text-center text-gray-500 p-4">No tasks yet. Add one above!</p>';
        return;
    }

    tasks.forEach(task => {
        const item = document.createElement('div');
        item.className = 'flex items-center justify-between p-4 bg-gray-50 border border-gray-200 rounded-lg shadow-sm';
        item.setAttribute('data-id', task.id);

        const titleElement = document.createElement('span');
        titleElement.className = 'task-title text-gray-700 text-base font-medium truncate flex-grow';
        titleElement.textContent = task.title;

        // Implement inline editing on double click
        titleElement.ondblclick = () => {
            const newTitle = prompt("Edit Task:", task.title);
            if (newTitle !== null && newTitle !== task.title) {
                updateTask(task.id, newTitle);
            }
        };

        const deleteButton = document.createElement('button');
        deleteButton.className = 'ml-4 text-red-500 hover:text-red-700 p-2 rounded-full transition duration-150';
        deleteButton.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm4 0a1 1 0 10-2 0v6a1 1 0 102 0V8z" clip-rule="evenodd" />
                                  </svg>`;
        deleteButton.onclick = () => deleteTask(task.id);

        const actionsContainer = document.createElement('div');
        actionsContainer.className = 'flex items-center';
        actionsContainer.appendChild(deleteButton);

        item.appendChild(titleElement);
        item.appendChild(actionsContainer);
        tasksList.appendChild(item);
    });
}

// --- Initialization ---

// 1. Attach event listener to the form
taskForm.addEventListener('submit', addTask);

// 2. Load existing tasks on page load
window.onload = fetchTasks;
