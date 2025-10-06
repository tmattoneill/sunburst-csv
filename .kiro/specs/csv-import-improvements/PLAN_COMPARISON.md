# Plan Comparison: CLAUDE_CODE_PLAN vs Kiro Spec

## Overview
Both plans address the same three core features but with different approaches. This document aligns them into a unified implementation strategy.

---

## ✅ Areas of Agreement

### 1. Header Row Detection
- **Both plans:** Show preview rows, allow user selection
- **Both plans:** Support skipping title rows
- **Both plans:** Maintain backward compatibility

### 2. Type Detection
- **Both plans:** Detect percentages, currency, dates, numbers
- **Both plans:** Convert percentages (3% → 0.03)
- **Both plans:** Handle currency symbols ($, €, £)
- **Both plans:** Clean formatted numbers (1,000 → 1000)

### 3. Display Names
- **Both plans:** Auto-generate from technical names
- **Both plans:** Allow user editing
- **Both plans:** Use in UI while preserving originals
- **Both plans:** Handle snake_case and camelCase

---

## 🔄 Key Differences & Resolution

### Difference 1: Wizard vs Inline Approach

**CLAUDE_CODE_PLAN:**
- Adds "Step 1.5" to existing modal
- Inline configuration within current flow
- Simpler, incremental changes

**Kiro Spec:**
- Separate 3-step wizard component
- More comprehensive, standalone experience
- Better for complex configurations

**RESOLUTION: Hybrid Approach**
- Use CLAUDE's inline approach for MVP (faster to implement)
- Keep Kiro's wizard architecture for future enhancement
- Start with Step 1.5 in FileLoaderModal, can extract to wizard later

### Difference 2: Preview Row Count

**CLAUDE_CODE_PLAN:** 15 rows
**Kiro Spec:** 10 rows

**RESOLUTION:** Use 10 rows (faster, sufficient)

### Difference 3: Type Detection Scope

**CLAUDE_CODE_PLAN:**
- 5 types: text, numeric, currency, percentage, date
- Simpler, focused on common cases

**Kiro Spec:**
- 7 types: adds boolean, integer (separate from float)
- More comprehensive

**RESOLUTION:** Start with CLAUDE's 5 types for MVP, add boolean/integer in Phase 2

### Difference 4: Error Handling Detail

**CLAUDE_CODE_PLAN:**
- Basic error handling mentioned
- Focus on happy path

**Kiro Spec:**
- Extensive error handling requirements
- Specific user messages for every scenario
- Graceful failure mandated

**RESOLUTION:** Use Kiro's comprehensive error handling (critical requirement)

### Difference 5: Template System

**CLAUDE_CODE_PLAN:**
- Not mentioned

**Kiro Spec:**
- Full template save/load/match system
- Template management UI

**RESOLUTION:** Templates are Phase 2 feature (not MVP)

---

## 🎯 Unified Implementation Plan

### MVP Scope (Phase 1)

#### Backend
1. **Header Row Detection**
   - New endpoint: `GET /api/file-preview` (returns first 10 rows)
   - Modify `/api/analyze` to accept `headerRow` and `skipRows` params
   - Update `GenericProcessor` to use these params
   - _From: CLAUDE_CODE_PLAN_

2. **Type Detection**
   - Implement `detect_column_type()` with 5 types
   - Fix `clean_numeric_value()` for percentages and currency
   - Update `analyze_columns()` to return type info
   - _From: CLAUDE_CODE_PLAN with Kiro's error handling_

3. **Display Names**
   - Add `prettify_column_name()` utility
   - Store display names in metadata
   - Update tree building to use display names
   - _From: CLAUDE_CODE_PLAN_

4. **Error Handling**
   - Implement structured error responses
   - Add user-friendly messages for all error cases
   - Log technical details server-side only
   - _From: Kiro Spec (CRITICAL)_

#### Frontend
1. **Header Selection UI**
   - Add Step 1.5 to FileLoaderModal
   - Show 10-row preview table with row numbers
   - Allow row selection and skip rows input
   - _From: CLAUDE_CODE_PLAN_

2. **Type Display**
   - Show type icons in ColumnSelector
   - Display confidence scores
   - Allow type override (collapsed by default)
   - _From: CLAUDE_CODE_PLAN_

3. **Display Name Editing**
   - Add expandable "Customize Display Names" section in Step 2
   - Pre-fill with prettified names
   - Allow inline editing
   - _From: CLAUDE_CODE_PLAN_

4. **Error Display**
   - Create reusable ErrorMessage component
   - Show user-friendly errors with suggestions
   - Preserve user work on errors
   - _From: Kiro Spec (CRITICAL)_

5. **Update All Components**
   - SunburstChart: Use display names
   - DataTable: Use display names in headers
   - PageHeader: Use display names in breadcrumbs
   - DataPane: Use display names
   - _From: CLAUDE_CODE_PLAN_

### Phase 2 Features (Future)
- Template save/load/match system
- Template management UI
- Boolean and integer types
- Multi-sheet Excel support
- Column reordering
- Advanced validation rules

---

## 📋 Revised Task List (MVP Only)

### Backend Tasks

- [ ] 1. Create `/api/file-preview` endpoint
  - Return first 10 rows as array of arrays
  - Handle encoding issues gracefully
  - _Estimated: 2 hours_

- [ ] 2. Update `/api/analyze` endpoint
  - Accept `headerRow` and `skipRows` parameters
  - Pass to GenericProcessor
  - Return enhanced column metadata with types
  - _Estimated: 3 hours_

- [ ] 3. Implement type detection in `generic_processor.py`
  - Add `detect_column_type()` function
  - Support: text, numeric, currency, percentage, date
  - Return confidence scores
  - _Estimated: 4 hours_

- [ ] 4. Fix `clean_numeric_value()` in `generic_processor.py`
  - Handle percentages: 3% → 0.03
  - Handle currency: $1,000 → 1000
  - Handle formatted numbers: 1,000.00 → 1000
  - _Estimated: 2 hours_

- [ ] 5. Add `prettify_column_name()` utility
  - Convert snake_case to Title Case
  - Convert camelCase to Title Case
  - Handle acronyms (ID, URL, API)
  - _Estimated: 1 hour_

- [ ] 6. Update metadata structure
  - Add `display_names` object
  - Add `column_types` object
  - Add `header_row` and `skip_rows`
  - Maintain backward compatibility
  - _Estimated: 2 hours_

- [ ] 7. Update tree building to use display names
  - Modify `build_tree_recursive()` to use display names for labels
  - Keep original names in data structure
  - _Estimated: 2 hours_

- [ ] 8. Implement comprehensive error handling
  - Create error code to message mapping
  - Return structured error responses
  - Add user-friendly messages for all scenarios
  - Log technical details server-side
  - _Estimated: 4 hours_

**Backend Total: ~20 hours**

### Frontend Tasks

- [ ] 9. Add Step 1.5 to FileLoaderModal
  - Create header selection UI
  - Show 10-row preview table
  - Allow row selection with visual highlight
  - Add "Skip rows" input
  - Call `/api/file-preview`
  - _Estimated: 4 hours_

- [ ] 10. Update ColumnSelector component
  - Add type icons (💵 📊 % 📅 📝)
  - Show confidence scores
  - Add collapsible type override dropdown
  - _Estimated: 3 hours_

- [ ] 11. Add display name editing to FileLoaderModal
  - Create expandable "Customize Display Names" section
  - Show table: Original → Display Name
  - Pre-fill with prettified names
  - Allow inline editing
  - Validate for duplicates/empty
  - _Estimated: 4 hours_

- [ ] 12. Create ErrorMessage component
  - Reusable error display with icon
  - Show title, explanation, suggestions
  - Include action buttons (Retry, Go Back, etc.)
  - _Estimated: 2 hours_

- [ ] 13. Add error handling throughout
  - File upload errors
  - Header detection errors
  - Type detection errors
  - Import processing errors
  - Preserve user work on errors (localStorage)
  - _Estimated: 4 hours_

- [ ] 14. Update SunburstChart to use display names
  - Accept displayNames prop
  - Use for chart labels
  - Show original in tooltips
  - _Estimated: 1 hour_

- [ ] 15. Update DataTable to use display names
  - Use display names in column headers
  - Map to original names for filtering
  - _Estimated: 2 hours_

- [ ] 16. Update PageHeader to use display names
  - Use display names in breadcrumbs
  - _Estimated: 1 hour_

- [ ] 17. Update DataPane to use display names
  - Use display names in labels
  - _Estimated: 1 hour_

- [ ] 18. Add loading states and progress
  - Spinner during file analysis
  - Progress bar during type detection
  - Progress during import
  - _Estimated: 2 hours_

**Frontend Total: ~24 hours**

### Testing Tasks

- [ ] 19. Test header row detection
  - Files with 0, 1, 2, 3+ title rows
  - Files with no headers
  - Files with duplicate column names
  - _Estimated: 2 hours_

- [ ] 20. Test type detection
  - Percentages: 3%, 0.03, 15.5%
  - Currency: $1,000, €500, £1,234.56
  - Dates: various formats
  - Mixed types in same column
  - _Estimated: 3 hours_

- [ ] 21. Test display names
  - snake_case, camelCase, UPPERCASE
  - Special characters
  - Very long names
  - Duplicate names
  - _Estimated: 2 hours_

- [ ] 22. Test error scenarios
  - Corrupted files
  - Invalid encoding
  - Conversion failures
  - Partial import success
  - _Estimated: 3 hours_

- [ ] 23. Test backward compatibility
  - Load old session JSONs
  - Ensure existing workflows unchanged
  - Security reports still auto-process
  - _Estimated: 2 hours_

**Testing Total: ~12 hours**

---

## 📊 Effort Estimate

| Phase | Hours | Days (6h/day) |
|-------|-------|---------------|
| Backend | 20 | 3.3 |
| Frontend | 24 | 4.0 |
| Testing | 12 | 2.0 |
| **Total** | **56** | **9.3** |

**With buffer (20%):** ~67 hours / ~11 days

---

## 🎯 Success Criteria

### Functional
- [ ] Can upload CSV with 3 title rows, select row 4 as header
- [ ] Percentages convert correctly (3% → 0.03)
- [ ] Currency displays with $ icon, converts to number
- [ ] Display names auto-generate and are editable
- [ ] All components use display names in UI
- [ ] Existing security reports still work unchanged

### Non-Functional
- [ ] File preview loads in < 2 seconds
- [ ] Type detection completes in < 5 seconds
- [ ] All errors show helpful messages (no stack traces)
- [ ] User work preserved on errors
- [ ] 90%+ test coverage for new code

---

## 🚀 Implementation Order

1. **Backend foundation** (Tasks 1-8) - Can work independently
2. **Frontend UI** (Tasks 9-11) - Depends on backend APIs
3. **Error handling** (Tasks 12-13) - Parallel with UI work
4. **Component updates** (Tasks 14-17) - After display names working
5. **Polish** (Task 18) - Final touches
6. **Testing** (Tasks 19-23) - Throughout and at end

---

## 📝 Notes

- **MVP focuses on core functionality** - No templates, no advanced features
- **CLAUDE's incremental approach** - Easier to implement and test
- **Kiro's error handling** - Critical for good UX, fully included
- **Backward compatibility** - Maintained throughout
- **Phase 2 features** - Documented but not implemented in MVP

**This unified plan takes the best of both approaches for a solid MVP!**
