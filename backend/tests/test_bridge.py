from pekat_code_modules.spreadsheet_bridge_sync import main


def test_bridge_fallback_does_not_raise_when_backend_is_missing():
    context = {"result": True}
    main(
        context,
        {
            "backend_url": "http://127.0.0.1:9",
            "project_id": "Camera_1",
            "timeout_s": 0.01,
        },
    )
    assert "spreadsheet" in context
    assert context["spreadsheet"]["reason"] == "BACKEND_UNAVAILABLE"
    assert context["result"] is True
