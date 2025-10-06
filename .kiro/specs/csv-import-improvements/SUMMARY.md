# CSV Import Improvements - Plan Summary

## Overview

This plan transforms the rigid CSV import process into a flexible, user-guided wizard that handles real-world data files intelligently while maintaining backward compatibility with existing security report workflows.

## Key Features

### 1. **Flexible Header Detection**
- Shows first 10 rows for user review
- Auto-suggests header row using heuristics
- Allows manual override
- Validates header selection

### 2. **Intelligent Type Detection**
- Automatically detects: percentages, currency, formatted numbers, dates
- Converts "3%" → 0.03, "$1,000" → 1000, etc.
- Shows confidence scores
- Allows manual override
- Handles conversion errors gracefully

### 3. **User-Friendly Display Names**
- Auto-generates readable names: "num_widgets" → "Num Widgets"
- Handles snake_case, camelCase, acronyms
- Fully editable by user
- Used in UI while preserving technical names in data

### 4. **Template System**
- Save import configurations for reuse
- Auto-match templates to similar files
- Import/export templates for team sharing
- Edit and manage saved templates

### 5. **Backward Compatibility**
- Existing security report format still works
- Auto-detects and offers automatic processing
- Option to use wizard for security reports too

## User Experience Flow

```
1. Upload File
   ↓
2. System analyzes file
   ↓
3. Is it a security report?
   ├─ Yes → Offer automatic processing OR wizard
   └─ No → Launch wizard
   ↓
4. WIZARD STEP 1: Select header row
   - View first 10 rows
   - System suggests row 2 (for example)
   - User confirms or overrides
   ↓
5. WIZARD STEP 2: Configure data types
   - System shows detected types with confidence
   - User reviews/overrides
   - Configure error handling
   ↓
6. WIZARD STEP 3: Set display names & review
   - Edit display names
   - Review final configuration
   - Option to save as template
   ↓
7. Import & Process
   - Show progress
   - Display success with stats
   - Redirect to visualization
```

## Technical Architecture

### Backend (Python/Flask)
```
New Modules:
- file_analyzer.py      → Detect structure, preview data
- type_detector.py      → Detect and convert data types
- display_name_generator.py → Generate readable names
- import_config.py      → Manage templates
- data_transformer.py   → Apply transformations

New Endpoints:
- POST /api/analyze           → Analyze uploaded file
- POST /api/detect-types      → Detect column types
- POST /api/process-import    → Execute import with config
- GET/POST/PUT/DELETE /api/templates → Template CRUD
```

### Frontend (Vue 3)
```
New Components:
- ImportWizard.vue           → Main wizard container
- Step1HeaderSelection.vue   → Header row selection
- Step2TypeConfiguration.vue → Type detection & config
- Step3DisplayNames.vue      → Display names & review
- TemplateManager.vue        → Template management UI

Enhanced Components:
- FileLoaderModal.vue  → Trigger wizard after upload
- DataTable.vue        → Use display names
- SunburstChart.vue    → Use display names
```

## Implementation Phases

### Phase 1: Backend Foundation (Tasks 1-5)
- File analysis and preview
- Type detection and conversion
- Display name generation
- Template management
- Data transformation engine

**Estimated Time:** 2-3 weeks

### Phase 2: Frontend Wizard (Tasks 6-10)
- Wizard shell and navigation
- Three-step configuration UI
- Template management UI
- Integration with backend APIs

**Estimated Time:** 2-3 weeks

### Phase 3: Integration & Polish (Tasks 11-14)
- Backward compatibility
- Visualization updates
- Error handling
- Documentation

**Estimated Time:** 1-2 weeks

### Phase 4: Testing & Optimization (Tasks 15-17)
- Unit tests
- Integration tests
- Performance optimization
- User acceptance testing

**Estimated Time:** 1-2 weeks

**Total Estimated Time:** 6-10 weeks

## Key Design Decisions

### 1. **Why 10 rows for preview?**
- Enough to see structure without overwhelming
- Fast to load even for large files
- Can be adjusted if needed

### 2. **Why sample 100 rows for type detection?**
- Balance between accuracy and performance
- Configurable if needed
- Sufficient for most data patterns

### 3. **Why JSON for template storage?**
- Human-readable and editable
- Easy to export/import
- No database schema changes needed
- Can migrate to DB later if needed

### 4. **Why three-step wizard?**
- Logical progression: structure → types → names
- Each step builds on previous
- Not too many steps to feel tedious
- Can skip steps with "Accept all" options

### 5. **Why keep original column names in data?**
- Maintains data integrity
- Allows re-export with original names
- Display names are presentation layer only
- Easier to debug and trace data

## Risks & Mitigations

### Risk 1: Performance with Large Files
**Mitigation:** 
- Stream files instead of loading entirely
- Sample data for type detection
- Show progress indicators
- Set reasonable file size limits

### Risk 2: Ambiguous Date Formats
**Mitigation:**
- Ask user to specify format when ambiguous
- Remember preference for future imports
- Provide clear examples

### Risk 3: Breaking Existing Workflows
**Mitigation:**
- Maintain backward compatibility
- Auto-detect security reports
- Offer both old and new flows
- Gradual migration path

### Risk 4: Template Complexity
**Mitigation:**
- Start with simple templates
- Add advanced features incrementally
- Provide good defaults
- Clear documentation

### Risk 5: User Confusion
**Mitigation:**
- Clear step-by-step wizard
- Inline help text and tooltips
- Good defaults that work for most cases
- "Accept all suggestions" quick path

## Success Metrics

### User Experience
- [ ] 90%+ of imports complete without errors
- [ ] Average wizard completion time < 2 minutes
- [ ] Template reuse rate > 50% for repeat users
- [ ] User satisfaction score > 4/5

### Technical
- [ ] File analysis < 2 seconds for files up to 100MB
- [ ] Type detection < 5 seconds for 10,000 rows
- [ ] Zero breaking changes to existing security report flow
- [ ] 90%+ test coverage for new code

### Business
- [ ] Support for 10+ new data formats
- [ ] Reduced support tickets for import issues
- [ ] Increased user adoption of visualization features
- [ ] Positive user feedback on flexibility

## Open Questions for Discussion

1. **Should we support Excel formulas?**
   - Pro: More powerful
   - Con: Complex, security risk
   - **Recommendation:** No for MVP, evaluate later

2. **Should we allow column reordering?**
   - Pro: Nice to have
   - Con: Adds complexity
   - **Recommendation:** Phase 2 feature

3. **Should we support multi-sheet Excel files?**
   - Pro: Common use case
   - Con: Adds UI complexity
   - **Recommendation:** Yes, but ask user to select sheet

4. **Should templates be user-specific or global?**
   - Pro (user-specific): Privacy, personalization
   - Pro (global): Team collaboration
   - **Recommendation:** User-specific for MVP, add sharing later

5. **Should we validate data ranges (e.g., percentages 0-100)?**
   - Pro: Catches errors early
   - Con: May reject valid data
   - **Recommendation:** Warn but don't block

## Next Steps

1. **Review this plan** - Discuss and refine
2. **Prioritize features** - MVP vs nice-to-have
3. **Set timeline** - Realistic deadlines
4. **Assign tasks** - Who builds what
5. **Create mockups** - UI designs for wizard
6. **Start Phase 1** - Backend foundation

---

**Ready to proceed?** Review the detailed requirements, design, and tasks documents for full specifications.
