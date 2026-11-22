from fastapi.testclient import TestClient
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import app
c = TestClient(app)
def test_assignment():
    r = c.post("/api/tasks", json={"project_id":1,"title":"Ship v1","priority":"high","assignee":"Bob","due":"2026-12-01"}, headers={"X-User":"Ada"})
    assert r.status_code == 200, r.text
    assert r.json()["assignee"] == "Bob"
def test_viewer_cannot_create():
    r = c.post("/api/tasks", json={"project_id":1,"title":"Nope"}, headers={"X-User":"Cara"})
    assert r.status_code == 403
def test_viewer_cannot_move():
    t = c.post("/api/tasks", json={"project_id":1,"title":"MoveMe"}, headers={"X-User":"Ada"}).json()
    r = c.patch(f"/api/tasks/{t['id']}", json={"status":"doing","version":t["version"]}, headers={"X-User":"Cara"})
    assert r.status_code == 403
def test_concurrent_conflict():
    t = c.post("/api/tasks", json={"project_id":1,"title":"Race"}, headers={"X-User":"Ada"}).json()
    r1 = c.patch(f"/api/tasks/{t['id']}", json={"status":"doing","version":t["version"]}, headers={"X-User":"Ada"})
    assert r1.status_code == 200
    r2 = c.patch(f"/api/tasks/{t['id']}", json={"status":"done","version":t["version"]}, headers={"X-User":"Bob"})
    assert r2.status_code == 409
def test_drag_drop_status():
    t = c.post("/api/tasks", json={"project_id":1,"title":"Drag"}, headers={"X-User":"Ada"}).json()
    r = c.patch(f"/api/tasks/{t['id']}", json={"status":"done","version":t["version"]}, headers={"X-User":"Bob"})
    assert r.json()["status"] == "done"
def test_filters_search():
    c.post("/api/tasks", json={"project_id":1,"title":"UniqueFilterXYZ","priority":"high"}, headers={"X-User":"Ada"})
    r = c.get("/api/projects/1/tasks?q=UniqueFilterXYZ")
    assert len(r.json()) >= 1
    r2 = c.get("/api/projects/1/tasks?priority=high")
    assert all(x["priority"] == "high" for x in r2.json())
def test_comments_activity():
    t = c.post("/api/tasks", json={"project_id":1,"title":"Talk"}, headers={"X-User":"Ada"}).json()
    c.post(f"/api/tasks/{t['id']}/comments", json={"author":"Bob","text":"hello"}, headers={"X-User":"Bob"})
    assert len(c.get(f"/api/tasks/{t['id']}/comments").json()) >= 1
    assert len(c.get("/api/projects/1/activity").json()) >= 1
