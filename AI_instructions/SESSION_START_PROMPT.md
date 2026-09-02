You are resuming work on the Camp Match backend (SoTrick). This may be a brand-new session after a crash, a glitch, or just a restart — treat it that way by default. Do not assume anything about prior progress from this conversation; you likely have none. The repository is your memory, not this chat.
Before writing, editing, or deleting anything:
Read AI_instructions/00_START_HERE.md, then everything it points you to.
Read AI_state/CURRENT_STATE.md, CURRENT_TASK.md, PROGRESS.md, SESSION_HANDOFF.md, and KNOWN_ISSUES.md.
Independently verify what those files claim — do not just trust them, especially after an interruption:
Run git status and git log -5 --oneline. If there's uncommitted work, look at what it actually contains before deciding whether it's safe to build on, finish, or discard.
Check whether the files the current task lists as "to create" or "to modify" already exist, and in what state — partially written, fully written, or untouched.
Run poetry run pytest, poetry run ruff check ., and poetry run mypy src and note what currently passes or fails, rather than assuming the last recorded state still holds.
If what you find matches what AI_state describes: summarize the current task and your plan for this session in a few lines, then proceed.
If what you find does not match — a chunk marked complete is missing its tests, a file exists that CURRENT_TASK.md said not to touch yet, uncommitted changes sit in git status that no session handoff mentions, or anything else looks inconsistent — stop. Report exactly what's inconsistent. Do not guess, silently "fix" the mismatch, revert anything, or continue past it without direction.
Report your findings before touching any code: what task you believe you're resuming, what you verified, and anything unclear or contradictory.
Standing rules from AI_instructions/04_CODING_RULES.md and 10_SESSION_PROTOCOL.md still apply in full — chunk discipline, no scope creep, no modifying files outside the current chunk, no claiming a test passed without running it, real ambiguity gets reported, not guessed at.
Additional notes for this session (fill in below before sending — leave blank if none):
     
our last session crashed mid way so the current instructions wasn't completed.
checkout the file current_instruction.txt for the current instructions we were working on before the session crashed
     