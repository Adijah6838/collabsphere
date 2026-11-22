# CollabSphere

Collaborative project management - Kanban, drag-drop, comments, activity, RBAC.

## Run
uvicorn app:app --port 8000

## Roles
Ada=admin, Bob=member, Cara=viewer (403 on write/move)

## Tests
7/7 passed - assignment, unauthorized, concurrent conflict, drag-drop, filters, comments
