INFO:     Application startup complete.

============================================================
[DEBUG AUTH] Incoming request authorization header: None
[DEBUG AUTH] Required backend format: 'Authorization: Bearer <your_jwt_token>'
[DEBUG AUTH] Validation checks: Present? False, Starts with 'Bearer '? False
============================================================

INFO:     127.0.0.1:54876 - "GET /api/v1/auth/me HTTP/1.1" 401 Unauthorized
{"identity_id": "1dcfc6e1-6a3d-4db1-8686-879b5bf87ba6", "event": "login_succeeded", "request_id": "213048cc-7ea7-4ea2-aa8e-932254930cbe", "level": "info", "timestamp": "2026-09-28T18:21:00.796872Z"}
INFO:     127.0.0.1:54912 - "POST /api/v1/auth/login HTTP/1.1" 200 OK

============================================================
[DEBUG AUTH] Incoming request authorization header: 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxZGNmYzZlMS02YTNkLTRkYjEtODY4Ni04NzliNWJmODdiYTYiLCJpYXQiOjE3OTA2MTk2NjAsImV4cCI6MTc5MDYyMDU2MCwidHlwZSI6ImFjY2VzcyJ9.OlW-_TJlCMFv0GFZzfyza4JBPCUFfM4peCqLZdM_iSw'
[DEBUG AUTH] Required backend format: 'Authorization: Bearer <your_jwt_token>'
[DEBUG AUTH] Validation checks: Present? True, Starts with 'Bearer '? True
============================================================

INFO:     127.0.0.1:55484 - "GET /api/v1/profiles/me HTTP/1.1" 200 OK

============================================================
[DEBUG AUTH] Incoming request authorization header: None
[DEBUG AUTH] Required backend format: 'Authorization: Bearer <your_jwt_token>'
[DEBUG AUTH] Validation checks: Present? False, Starts with 'Bearer '? False
============================================================

INFO:     127.0.0.1:55568 - "GET /api/v1/auth/me HTTP/1.1" 401 Unauthorized