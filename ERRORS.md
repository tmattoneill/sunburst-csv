# ERRORS.md - Pre-Launch Code Review

**Date:** 2025-01-04
**Status:** FIXED

## Critical Errors Found (Pre-Launch)

### 1. TypedDict Constructor Usage - generic_processor.py ❌ CRITICAL

**Location:** `backend/app/dataproc/generic_processor.py` lines 222-226, 251-254, 258-262

**Issue:**
Incorrect usage of TypedDict - attempting to use as constructor:
```python
child = TreeNode(
    name=str(value),
    value=float(node_value),
    children=child_nodes
)
```

**Problem:**
TypedDict is only for type hinting, not for creating instances. This will raise a TypeError at runtime.

**Fix:**
Replace with dict literals:
```python
child = {
    'name': str(value),
    'value': float(node_value),
    'children': child_nodes
}
```

**Impact:** Application crashes when processing any file
**Severity:** CRITICAL - Blocks all functionality

---

### 2. Required Props in Generic Mode - DataTable.vue ❌ CRITICAL

**Location:** `frontend/src/components/DataTable.vue` lines 112-118

**Issue:**
Props `dateStart` and `dateEnd` are marked as `required: true`:
```javascript
dateStart: {
  type: String,
  required: true  // ❌ Problem
},
dateEnd: {
  type: String,
  required: true  // ❌ Problem
}
```

**Problem:**
In generic mode, these values are empty strings and not provided as props. Vue will throw prop validation errors.

**Fix:**
Change to optional with defaults:
```javascript
dateStart: {
  type: String,
  required: false,
  default: ''
},
dateEnd: {
  type: String,
  required: false,
  default: ''
}
```

**Impact:** Vue prop validation errors prevent DataTable from rendering
**Severity:** CRITICAL - Blocks UI rendering

---

### 3. Bootstrap Modal Null Reference - FileLoaderModal.vue ❌ CRITICAL

**Location:** `frontend/src/components/FileLoaderModal.vue` line 445

**Issue:**
Calling `.hide()` on potentially null bootstrap modal instance:
```javascript
const modal = bootstrap.Modal.getInstance(document.getElementById('mdl-load'))
modal.hide()  // ❌ Will crash if modal is null
```

**Problem:**
If modal hasn't been initialized yet or element doesn't exist, `getInstance()` returns null.

**Fix:**
Add null check:
```javascript
const modal = bootstrap.Modal.getInstance(document.getElementById('mdl-load'))
if (modal) {
  modal.hide()
}
```

**Impact:** JavaScript error crashes when closing modal
**Severity:** CRITICAL - Breaks modal functionality

---

## Warnings (Non-Critical)

### 4. Suboptimal Import Pattern - routes.py ⚠️ WARNING

**Location:** `backend/app/api/routes.py` lines 93, 147

**Issue:**
Pandas imported inside functions instead of module level:
```python
def upload_file():
    # ...
    import pandas as pd  # ⚠️ Should be at top
```

**Problem:**
Minor performance overhead on every function call.

**Fix:**
Move to top of file with other imports.

**Impact:** Minor performance degradation
**Severity:** LOW - Optimization opportunity

---

## Resolution Status

- [x] Error 1: Fixed - TypedDict replaced with dict literals
- [x] Error 2: Fixed - Props made optional
- [x] Error 3: Fixed - Added null check
- [x] Warning 4: Fixed - Moved pandas import to top

**All critical errors resolved. Application ready for testing.**
