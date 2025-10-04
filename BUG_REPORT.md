# CRITICAL BUG: executeBash Tool Captures Shell Prompt Instead of Command Output

## Severity: CRITICAL - Blocks Agent Functionality

## Summary
The `executeBash` tool is capturing the shell prompt (PS1) instead of actual command stdout/stderr, making the AI agent completely unable to read command results. This renders bash-based diagnostics, system checks, and automation completely non-functional.

---

## Environment
- **OS:** macOS (darwin) - Apple Silicon M1/M2
- **Shell:** zsh
- **Kiro Version:** Beta
- **Python:** 3.13.5 (via pyenv)
- **Working Directory:** `/Volumes/NMVe M2/dev/sunchart` (external NVMe drive with space in path)
- **Username:** thomasoneill
- **Machine:** MacBook-M1-2063

---

## Steps to Reproduce

1. Open Kiro IDE Beta
2. Open any project (tested with project at `/Volumes/NMVe M2/dev/sunchart`)
3. Start AI agent chat session
4. Agent executes any bash command via `executeBash` tool
5. Example: `whoami`

---

## Expected Behavior

**Command:** `whoami`

**Expected tool response:**
```
Output:
thomasoneill

Exit Code: 0
```

**What user sees in their terminal:**
```
❯ whoami
thomasoneill
```

---

## Actual Behavior

**Command:** `whoami`

**Actual tool response received by agent:**
```
Output:
homasoneill@MacBook-M1-2063:/Volumes/NMVe M2/dev/sunchart

Exit Code: 0
```

### Key Observations:
1. **No stdout captured** - The actual output `thomasoneill` is completely missing
2. **Prompt captured instead** - Tool returns what appears to be the shell prompt (PS1)
3. **Username truncated** - Prompt shows `homasoneill` instead of `thomasoneill` (missing "t")
4. **Exit code correct** - Command does execute successfully (Exit Code: 0)
5. **User sees correct output** - In their terminal, the command works perfectly

---

## Additional Test Cases

### Test 1: Simple Echo
```bash
Command: echo "test output"
User sees: test output
Agent receives: homasoneill@MacBook-M1-2063:/Volumes/NMVe M2/dev/sunchart
```

### Test 2: Directory Listing
```bash
Command: ls -la
User sees: [full directory listing]
Agent receives: homasoneill@MacBook-M1-2063:/Volumes/NMVe M2/dev/sunchart
```

### Test 3: Docker Status
```bash
Command: docker ps -a
User sees: [container listing with headers and data]
Agent receives: homasoneill@MacBook-M1-2063:/Volumes/NMVe M2/dev/sunchart
```

### Test 4: Version Check
```bash
Command: python3 --version
User sees: Python 3.13.5
Agent receives: homasoneill@MacBook-M1-2063:/Volumes/NMVe M2/dev/sunchart
```

**Pattern:** Every command returns the same prompt line, regardless of actual output.

---

## Root Cause Analysis

The `executeBash` tool appears to be:
1. **Capturing from wrong stream** - Reading the prompt instead of stdout
2. **Timing issue** - Capturing before stdout is flushed, only getting prompt
3. **Buffer overwrite** - Prompt is overwriting the actual command output in the buffer
4. **File descriptor issue** - Reading from wrong FD (prompt stream vs stdout)

### Evidence:
- Exit codes are correct (commands execute successfully)
- User sees proper output in terminal (commands work)
- Agent consistently receives only prompt line (wrong stream captured)
- Username truncation suggests buffer/encoding issue

---

## Impact

### Blocks Critical Functionality:
- ❌ Cannot diagnose system state
- ❌ Cannot verify installed software/versions
- ❌ Cannot check Docker container status
- ❌ Cannot read directory contents
- ❌ Cannot debug application issues
- ❌ Cannot run tests or builds
- ❌ Cannot verify file operations
- ❌ Cannot chain commands based on output
- ❌ Cannot perform any bash-based automation

### Result:
**Agent is effectively blind to system state and command results**, making Kiro unusable for any workflow requiring bash command execution.

---

## Workaround
None available. User must manually run all commands and paste output back to agent, defeating the purpose of autonomous agent execution.

---

## Technical Investigation Needed

### 1. Output Capture Mechanism
- How is stdout/stderr being captured from executed commands?
- Is a PTY (pseudo-terminal) being used?
- Are file descriptors being properly redirected?

### 2. Prompt Handling
- Why is the shell prompt appearing in the output?
- Is the prompt being written to stdout instead of stderr?
- Is there a terminal emulation layer interfering?

### 3. Buffer Management
- Why is the username truncated (`homasoneill` vs `thomasoneill`)?
- Is there a buffer offset or alignment issue?
- Are buffers being cleared/flushed properly?

### 4. Shell Integration
- How is zsh being invoked?
- Are shell initialization files (.zshrc) interfering?
- Is the prompt configuration being respected?

### 5. Platform-Specific Issues
- Is this specific to macOS?
- Is this specific to Apple Silicon?
- Is this related to external drive mounting?
- Are there macOS accessibility/permission issues?

---

## Suggested Fixes

### Immediate Investigation:
1. Add verbose logging to `executeBash` tool showing:
   - Exact command being executed
   - How subprocess is spawned
   - What streams are being captured
   - Raw buffer contents before processing

2. Test with minimal shell environment:
   - Try with `bash -c "command"` instead of interactive zsh
   - Try with `sh -c "command"`
   - Disable all shell initialization files

3. Verify stream capture:
   - Explicitly capture stdout to file and read it
   - Test with `command 2>&1` to merge streams
   - Test with `command > /tmp/output.txt` and read file

### Potential Solutions:
1. Use `subprocess.run()` with `capture_output=True` in Python
2. Explicitly redirect stdout/stderr to files and read them
3. Use `script` command to capture terminal session
4. Disable PTY if being used, or fix PTY configuration
5. Strip prompt from output using regex/parsing

---

## Priority
**CRITICAL** - This bug makes the AI agent's bash execution capability completely non-functional. Without the ability to see command output, the agent cannot perform basic system administration, diagnostics, or automation tasks.

---

## Reporter Information
- **User:** thomasoneill
- **Date:** April 10, 2025
- **Session:** Sunchart application diagnostics
- **Kiro Version:** Beta

---

## Additional Notes
- All file-based tools (readFile, listDirectory, fileSearch, etc.) work correctly
- Only `executeBash` tool is affected
- Issue is 100% reproducible across all bash commands
- User confirms they see correct output in their terminal
- This is a show-stopper bug for production use of Kiro
