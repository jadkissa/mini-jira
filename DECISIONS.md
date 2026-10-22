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

### Timezone-aware timestamps
**Chosen:** `DateTime(timezone=True)` / `timestamptz`, values in UTC.  
**Alternatives:** naive `timestamp` without timezone.  
**Why:** avoids ambiguous local times when computing `delivery_date` and for future reminders.
