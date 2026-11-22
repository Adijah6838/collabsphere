# app.py - CollabSphere API
from fastapi import FastAPI, Header, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import os
from db import Session
from models import Project, Task, Comment, Activity, Member
app = FastAPI(title="CollabSphere")
def log(pid, actor, action, detail=""):
    s = Session(); s.add(Activity(project_id=pid, actor=actor, action=action, detail=detail)); s.commit(); s.close()
def role_of(user):
    s = Session(); m = s.query(Member).filter_by(name=user).first(); s.close()
    return m.role if m else "viewer"
def require(user, need):
    r = role_of(user)
    rank = {"viewer": 0, "member": 1, "admin": 2}
    if rank.get(r, 0) < rank[need]:
        raise HTTPException(403, f"Requires {need}, you are {r}")
def task_out(t):
    return {"id": t.id, "project_id": t.project_id, "title": t.title, "desc": t.desc, "status": t.status, "priority": t.priority, "assignee": t.assignee, "due": t.due, "version": t.version}
class ProjectIn(BaseModel):
    name: str; desc: str = ""
class TaskIn(BaseModel):
    project_id: int; title: str; desc: str = ""; priority: str = "medium"; assignee: str = ""; due: str = ""
class TaskPatch(BaseModel):
    title: Optional[str] = None; status: Optional[str] = None; priority: Optional[str] = None; assignee: Optional[str] = None; due: Optional[str] = None; version: Optional[int] = None
class CommentIn(BaseModel):
    author: str = "anon"; text: str
class MemberIn(BaseModel):
    name: str; role: str = "member"
@app.get("/api/projects")
def list_projects():
    s = Session(); out = [{"id": p.id, "name": p.name, "desc": p.desc} for p in s.query(Project).all()]; s.close(); return out
@app.post("/api/projects")
def create_project(p: ProjectIn, x_user: str = Header("anon")):
    require(x_user, "member")
    s = Session(); proj = Project(name=p.name, desc=p.desc); s.add(proj); s.commit(); s.refresh(proj); s.close(); log(proj.id, x_user, "project_created", p.name); return {"id": proj.id, "name": p.name}
@app.get("/api/projects/{pid}/tasks")
def list_tasks(pid: int, q: str = "", priority: str = "", assignee: str = "", status: str = ""):
    s = Session(); rows = s.query(Task).filter_by(project_id=pid).all(); s.close()
    out = [task_out(t) for t in rows]
    if q: out = [t for t in out if q.lower() in t["title"].lower() or q.lower() in t["desc"].lower()]
    if priority: out = [t for t in out if t["priority"] == priority]
    if assignee: out = [t for t in out if t["assignee"] == assignee]
    if status: out = [t for t in out if t["status"] == status]
    return out
@app.post("/api/tasks")
def create_task(t: TaskIn, x_user: str = Header("anon")):
    require(x_user, "member")
    s = Session(); task = Task(project_id=t.project_id, title=t.title, desc=t.desc, priority=t.priority, assignee=t.assignee, due=t.due); s.add(task); s.commit(); s.refresh(task); s.close(); log(t.project_id, x_user, "task_created", t.title); return task_out(task)
@app.patch("/api/tasks/{tid}")
def patch_task(tid: int, p: TaskPatch, x_user: str = Header("anon")):
    require(x_user, "member")
    s = Session(); t = s.query(Task).filter_by(id=tid).first()
    if not t: s.close(); raise HTTPException(404, "not found")
    if p.version is not None and p.version != t.version: s.close(); raise HTTPException(409, "version conflict - reload")
    old_status = t.status
    if p.title is not None: t.title = p.title
    if p.status is not None: t.status = p.status
    if p.priority is not None: t.priority = p.priority
    if p.assignee is not None: t.assignee = p.assignee
    if p.due is not None: t.due = p.due
    t.version += 1; s.commit(); out = task_out(t); pid = t.project_id; s.close()
    if p.status is not None and p.status != old_status: log(pid, x_user, "task_moved", f"{out['title']} {old_status} -> {p.status}")
    return out
@app.delete("/api/tasks/{tid}")
def delete_task(tid: int, x_user: str = Header("anon")):
    require(x_user, "admin")
    s = Session(); t = s.query(Task).filter_by(id=tid).first()
    if t: pid = t.project_id; s.delete(t); s.commit(); s.close(); log(pid, x_user, "task_deleted", str(tid))
    return {"ok": True}
@app.get("/api/tasks/{tid}/comments")
def list_comments(tid: int):
    s = Session(); out = [{"id": c.id, "author": c.author, "text": c.text, "created": str(c.created)} for c in s.query(Comment).filter_by(task_id=tid).all()]; s.close(); return out
@app.post("/api/tasks/{tid}/comments")
def add_comment(tid: int, c: CommentIn, x_user: str = Header("anon")):
    require(x_user, "member")
    s = Session(); t = s.query(Task).filter_by(id=tid).first()
    if not t: s.close(); raise HTTPException(404, "not found")
    cm = Comment(task_id=tid, author=c.author, text=c.text); s.add(cm); s.commit(); pid = t.project_id; s.close(); log(pid, x_user, "comment_added", c.text[:50]); return {"ok": True}
@app.get("/api/members")
def list_members():
    s = Session(); out = [{"id": m.id, "name": m.name, "role": m.role} for m in s.query(Member).all()]; s.close(); return out
@app.post("/api/members")
def add_member(m: MemberIn, x_user: str = Header("anon")):
    require(x_user, "admin")
    s = Session(); mm = Member(name=m.name, role=m.role); s.add(mm); s.commit(); s.close(); log(0, x_user, "member_added", m.name); return {"ok": True}
@app.get("/api/projects/{pid}/activity")
def activity(pid: int):
    s = Session(); out = [{"id": a.id, "actor": a.actor, "action": a.action, "detail": a.detail, "created": str(a.created)} for a in s.query(Activity).filter_by(project_id=pid).order_by(Activity.id.desc()).limit(50).all()]; s.close(); return out
if os.path.exists("static"):
    app.mount("/", StaticFiles(directory="static", html=True), name="static")
