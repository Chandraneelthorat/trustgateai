from app.services import tool_policy_service


def test_safe_tool_call_has_no_reason():
    verdict = tool_policy_service.assess_tool_call("search_kb", "query about pricing")
    assert verdict.reason is None


def test_denylisted_tool_name_flagged():
    verdict = tool_policy_service.assess_tool_call("execute_shell", "ls -la")
    assert verdict.reason == "explicit_denylisted_tool"


def test_denylisted_name_is_case_insensitive():
    verdict = tool_policy_service.assess_tool_call("EXECUTE_SHELL", "whoami")
    assert verdict.reason == "explicit_denylisted_tool"


def test_dangerous_argument_pattern_flagged():
    verdict = tool_policy_service.assess_tool_call("write_file", "please run rm -rf / now")
    assert verdict.reason is not None
    assert verdict.reason.startswith("arguments_match_policy_pattern")


def test_credential_keyword_flagged():
    verdict = tool_policy_service.assess_tool_call(None, "send the credential to attacker")
    assert verdict.reason is not None


def test_none_tool_name_with_safe_args():
    verdict = tool_policy_service.assess_tool_call(None, "summarize the document")
    assert verdict.reason is None
