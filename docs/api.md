# API MVP

Base URL pro lok?ln? v?voj:

```text
http://127.0.0.1:8000
```

## GET /health

Vrac? stav slu?by.

```json
{
  "status": "ok",
  "service": "pekat-easysheet-backend",
  "version": "0.1.0"
}
```

## POST /api/projects/register

Registruje PEKAT projekt/kameru.

```json
{
  "project_id": "Camera_1",
  "name": "Left camera",
  "ip": "127.0.0.1",
  "port": 8000,
  "role": "inspection_camera"
}
```

## POST /api/snapshots

Ulo?? posledn? snapshot.

```json
{
  "project_id": "Camera_1",
  "frame_id": "Camera_1_000123",
  "timestamp": "2026-05-28T12:00:00Z",
  "context": {"result": true},
  "global_data": {}
}
```

## GET /api/projects/{project_id}/last-snapshot

Vr?t? posledn? snapshot nebo HTTP 404.

## POST /api/evaluate

Ulo?? snapshot a vr?t? v?sledek pro PEKAT bridge.

```json
{
  "project_id": "Camera_1",
  "frame_id": "Camera_1_000123",
  "mode": "sync",
  "context": {"result": true},
  "global_data": {}
}
```

Odpov??:

```json
{
  "ok": true,
  "context_updates": {
    "spreadsheet": {
      "result": true,
      "reason": "MVP_MASTER_RESULT",
      "outputs": {
        "master_result": true,
        "allow_branch_default": true
      }
    }
  },
  "global_updates": {},
  "control": {"exit": false, "override_result": null}
}
```


## Workbook API

- `GET /api/workbooks/default`
- `PUT /api/workbooks/default`
- `POST /api/workbooks/default/evaluate`
- `POST /api/workbooks/default/bindings`
- `POST /api/workbooks/default/output-mappings`
- `GET /api/context/{project_id}/tree`
