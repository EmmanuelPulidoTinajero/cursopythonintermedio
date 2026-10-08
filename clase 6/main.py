from datetime import date
import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field


app = FastAPI(title="API de tareas")
TASKS_FILE = Path(__file__).with_name("tasks.json")


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    due_date: date | None = None


class Task(TaskCreate):
    id: int


def read_tasks() -> list[Task]:
    if not TASKS_FILE.exists():
        return []

    with TASKS_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return [Task.model_validate(task) for task in data]


def write_tasks(tasks: list[Task]) -> None:
    with TASKS_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            [task.model_dump(mode="json") for task in tasks],
            file,
            ensure_ascii=False,
            indent=2,
        )


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """
    <!doctype html>
    <html lang="es">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Mis tareas</title>
        <style>
          body { font-family: system-ui, sans-serif; line-height: 1.5; margin: 0 auto; max-width: 48rem; padding: 1rem; }
          form, .task { border: 1px solid #bbb; border-radius: .5rem; margin: 1rem 0; padding: 1rem; }
          label { display: block; font-weight: 600; margin-top: .75rem; }
          input, textarea, button { box-sizing: border-box; font: inherit; margin-top: .25rem; padding: .5rem; width: 100%; }
          button { background: #164e63; color: white; cursor: pointer; }
          .task h3 { margin-top: 0; }
          .error { color: #9b1c1c; }
        </style>
      </head>
      <body>
        <header>
          <h1>Gestor de tareas</h1>
          <p>Agrega una tarea y consulta la lista guardada en el servidor.</p>
        </header>

        <main>
          <form id="task-form">
            <h2 id="form-title">Crear tarea</h2>
            <label for="title">Título</label>
            <input id="title" name="title" required maxlength="100">

            <label for="description">Descripción</label>
            <textarea id="description" name="description" maxlength="500" rows="3"></textarea>

            <label for="due-date">Fecha de entrega</label>
            <input id="due-date" name="due_date" type="date">

            <button type="submit">Guardar tarea</button>
            <button id="cancel-button" type="button" hidden>Cancelar edición</button>
          </form>

          <p id="message" role="status" aria-live="polite"></p>
          <section aria-labelledby="tasks-title">
            <h2 id="tasks-title">Tareas guardadas</h2>
            <div id="tasks"></div>
          </section>
        </main>

        <script>
          const form = document.querySelector("#task-form");
          const tasksContainer = document.querySelector("#tasks");
          const message = document.querySelector("#message");
          const cancelButton = document.querySelector("#cancel-button");
          let editingId = null;

          function showMessage(text, isError = false) {
            message.textContent = text;
            message.className = isError ? "error" : "";
          }

          function renderTasks(tasks) {
            tasksContainer.innerHTML = "";
            if (tasks.length === 0) {
              tasksContainer.textContent = "Todavía no hay tareas.";
              return;
            }

            tasks.forEach((task) => {
              const article = document.createElement("article");
              article.className = "task";
              const title = document.createElement("h3");
              title.textContent = task.title;
              const description = document.createElement("p");
              description.textContent = task.description || "Sin descripción";
              const dueDate = document.createElement("p");
              dueDate.textContent = `Entrega: ${task.due_date || "Sin fecha"}`;
              const editButton = document.createElement("button");
              editButton.type = "button";
              editButton.textContent = "Editar tarea";
              editButton.addEventListener("click", () => startEditing(task));
              article.append(title, description, dueDate, editButton);
              tasksContainer.appendChild(article);
            });
          }

          async function loadTasks() {
            const response = await fetch("/tasks");
            if (!response.ok) throw new Error("No se pudieron cargar las tareas.");
            renderTasks(await response.json());
          }

          function startEditing(task) {
            editingId = task.id;
            form.title.value = task.title;
            form.description.value = task.description;
            form.due_date.value = task.due_date || "";
            document.querySelector("#form-title").textContent = "Editar tarea";
            form.querySelector("button[type=submit]").textContent = "Actualizar tarea";
            cancelButton.hidden = false;
            form.title.focus();
          }

          function resetForm() {
            editingId = null;
            form.reset();
            document.querySelector("#form-title").textContent = "Crear tarea";
            form.querySelector("button[type=submit]").textContent = "Guardar tarea";
            cancelButton.hidden = true;
          }

          form.addEventListener("submit", async (event) => {
            event.preventDefault();
            const task = {
              title: form.title.value,
              description: form.description.value,
              due_date: form.due_date.value || null,
            };
            const url = editingId === null ? "/tasks" : `/tasks/${editingId}`;
            const method = editingId === null ? "POST" : "PUT";
            const response = await fetch(url, {
              method,
              headers: {"Content-Type": "application/json"},
              body: JSON.stringify(task),
            });
            if (!response.ok) {
              showMessage("Revisa los datos de la tarea.", true);
              return;
            }
            resetForm();
            showMessage("Tarea guardada.");
            await loadTasks();
          });

          cancelButton.addEventListener("click", resetForm);
          loadTasks().catch((error) => showMessage(error.message, true));
        </script>
      </body>
    </html>
    """


@app.get("/tasks", response_model=list[Task])
def list_tasks() -> list[Task]:
    return read_tasks()


@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task_data: TaskCreate) -> Task:
    tasks = read_tasks()
    next_id = max((task.id for task in tasks), default=0) + 1
    task = Task(id=next_id, **task_data.model_dump())
    tasks.append(task)
    write_tasks(tasks)
    return task


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task_data: TaskCreate) -> Task:
    tasks = read_tasks()
    for position, task in enumerate(tasks):
        if task.id == task_id:
            updated_task = Task(id=task_id, **task_data.model_dump())
            tasks[position] = updated_task
            write_tasks(tasks)
            return updated_task
    raise HTTPException(status_code=404, detail="Tarea no encontrada")
