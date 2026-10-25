# Design decisions

Short log of important choices. Format: **chosen** / alternatives / why.

---

### Duration instead of calendar due date
**Chosen:** `duration_days` (int) + computed `delivery_date`.  
**Alternatives:** store only a calendar `due_date`.  
**Why:** simpler input (“5 days”); delivery is derived for display and later reminders.

### Skip long-lived in-memory Phase 1 store
**Chosen:** schemas/routers against Postgres once models existed.  
**Alternatives:** full in-memory CRUD, then rewrite for DB.  
**Why:** less throwaway code; still practiced validation and routing with real persistence.

### Cascade delete projects → tasks
**Chosen:** ORM `cascade="all, delete-orphan"` + FK `ON DELETE CASCADE`.  
**Alternatives:** block delete if tasks exist; soft-delete.  
**Why:** matches expected board behavior for this MVP; avoids orphaned tasks.

### Activity log lives on the task
**Chosen:** `activity_log.task_id` with `ON DELETE CASCADE`.  
**Alternatives:** keep rows after the task is deleted, with a nullable task id.  
**Why:** the log explains a task that still exists. Deleting the task removes its history with it.

### Who may use labels
**Chosen:** owners and admins create and delete labels. Any member can attach or remove one on a task, same as editing the task. Label names are unique per project.  
**Alternatives:** any member creates labels; labels are global.  
**Why:** labels are project vocabulary, so they follow "manage projects". Putting one on a task is task work.

### Timezone-aware timestamps
**Chosen:** `DateTime(timezone=True)` / `timestamptz`, values in UTC.  
**Alternatives:** naive `timestamp` without timezone.  
**Why:** avoids ambiguous local times when computing `delivery_date` and for future reminders.
