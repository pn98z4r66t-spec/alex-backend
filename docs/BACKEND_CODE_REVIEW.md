================================================================================
BACKEND CODE REVIEW REPORT
================================================================================

STATISTICS
--------------------------------------------------------------------------------
Files Reviewed: 31
Total Lines: 6347
Average Lines per File: 204

ISSUES SUMMARY
--------------------------------------------------------------------------------
Total Issues Found: 34

HIGH Priority: 22 issues
MEDIUM Priority: 12 issues


BARE EXCEPT
--------------------------------------------------------------------------------
  • services/ai_providers/ollama.py:136 - Bare except clause
  • services/ai_providers/ollama.py:151 - Bare except clause

HARDCODED VALUES
--------------------------------------------------------------------------------
  • config/config.py:26 - Hardcoded localhost URL
  • config/config.py:33 - Hardcoded localhost URL
  • routes/ai_chat.py:339 - Hardcoded localhost URL
  • routes/files.py:416 - Hardcoded localhost URL
  • routes/task_instance.py:506 - Hardcoded localhost URL
  • routes/task_sharing.py:179 - Hardcoded localhost URL
  • routes/task_sharing.py:388 - Hardcoded localhost URL

LONG FUNCTIONS
--------------------------------------------------------------------------------
  • main.py:36 - create_app (62 lines)
  • models/chat_models.py:126 - to_dict (53 lines)
  • models/models.py:241 - to_dict (57 lines)
  • models/task_instance.py:54 - to_dict (65 lines)
  • routes/ai_chat.py:90 - send_ai_message (80 lines)
  • routes/email.py:19 - get_emails (79 lines)
  • routes/files.py:109 - upload_file (86 lines)
  • routes/files.py:395 - ai_analyze_file (65 lines)
  • routes/task_chat.py:68 - get_messages (53 lines)
  • routes/task_chat.py:269 - add_participant (56 lines)
  ... and 10 more

MISSING DOCSTRINGS
--------------------------------------------------------------------------------
  • middleware/optional_auth.py:18 - Function decorated missing docstring

SILENT EXCEPTIONS
--------------------------------------------------------------------------------
  • middleware/auth.py:53 - Silent exception (pass)
  • routes/ai_chat.py:243 - Silent exception (pass)
  • routes/task_chat.py:365 - Silent exception (pass)
  • routes/task_chat.py:417 - Silent exception (pass)

================================================================================