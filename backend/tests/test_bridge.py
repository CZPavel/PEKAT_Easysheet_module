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



def test_bridge_applies_global_updates_to_global_data():
    from pekat_code_modules.spreadsheet_bridge_sync import _apply_response

    context = {"result": True, "global_data": {"recipe": {"active_id": "A"}}}
    response = {
        "context_updates": {"spreadsheet": {"master_result": False}},
        "global_updates": {"spreadsheet": {"reject_reason": "MASTER_NG"}},
        "control": {"exit": True, "override_result": False},
    }
    _apply_response(context, response)
    assert context["spreadsheet"]["master_result"] is False
    assert context["global_data"]["spreadsheet"]["reject_reason"] == "MASTER_NG"
    assert context["exit"] is True
    assert context["result"] is False
