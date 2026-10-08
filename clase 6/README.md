# Clase 6: primera API con FastAPI

Esta es una API de gestión de tareas pensada como primer ejercicio. Todo el
backend y la interfaz están en [`main.py`](main.py). Las tareas se guardan en
`tasks.json`, que se crea automáticamente al guardar la primera tarea.

## 1. Preparar el proyecto

Se recomienda usar un entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2. Iniciar el servidor

Desde esta carpeta:

```powershell
uvicorn main:app --reload
```

Después, abre <http://127.0.0.1:8000>. La interfaz usa HTML semántico,
etiquetas asociadas a sus campos, foco visible del navegador y una región
`aria-live` para avisar el resultado de las acciones a lectores de pantalla.

FastAPI también genera documentación interactiva:

- <http://127.0.0.1:8000/docs>
- <http://127.0.0.1:8000/redoc>

## 3. Acciones disponibles

| Método | URL | Uso |
| --- | --- | --- |
| `GET` | `/tasks` | Traer todas las tareas |
| `POST` | `/tasks` | Crear una tarea |
| `PUT` | `/tasks/{id}` | Actualizar una tarea |

Ejemplo de JSON para crear o actualizar:

```json
{
  "title": "Estudiar FastAPI",
  "description": "Leer los conceptos básicos de rutas",
  "due_date": "2026-10-15"
}
```

## 4. Cómo está organizado

1. `TaskCreate` describe los datos que recibe la API.
2. `Task` agrega un `id` a esos datos.
3. `read_tasks` y `write_tasks` leen y escriben el archivo JSON.
4. Cada función decorada con `@app.get`, `@app.post` o `@app.put` es una
   ruta HTTP.
5. La interfaz llama esas rutas con `fetch`.

## Ejercicio para la clase

1. Ejecuta la aplicación y crea dos tareas desde la interfaz.
2. Abre `tasks.json` y observa cómo se guardan.
3. Visita `/docs` y prueba las mismas rutas desde la documentación.
4. Cambia el proyecto para agregar una ruta `DELETE /tasks/{id}`.
5. Como siguiente paso, separa los modelos, las rutas y la interfaz en
   archivos diferentes.

## Nota didáctica

El archivo JSON es suficiente para practicar HTTP, rutas, modelos y
persistencia sin introducir todavía una base de datos. No está pensado para
varios usuarios ni para producción.
