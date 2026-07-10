from app.services import pii_service


def test_no_pii_detected():
    finding = pii_service.scan_text("The weather is sunny today.")
    assert finding.types == ()


def test_email_detected():
    finding = pii_service.scan_text("Reach me at jane@acme.example please.")
    assert "email" in finding.types


def test_phone_detected():
    finding = pii_service.scan_text("Call 415-555-0182 after noon.")
    assert "phone" in finding.types


def test_ssn_detected():
    finding = pii_service.scan_text("SSN on file: 123-45-6789.")
    assert "ssn" in finding.types


def test_multiple_types_are_sorted_and_unique():
    finding = pii_service.scan_text("jane@acme.example / 415-555-0182 / 123-45-6789")
    assert set(finding.types) == {"email", "phone", "ssn"}
    assert list(finding.types) == sorted(finding.types)


def test_subscore_without_pii_is_low():
    assert pii_service.subscore("plain text", None, None) == 0.05


def test_subscore_scales_with_types():
    one = pii_service.subscore("jane@acme.example", None, None)
    many = pii_service.subscore("jane@acme.example 415-555-0182 123-45-6789", None, None)
    assert many > one
    assert many <= 1.0


def test_scan_handles_none_like_empty():
    assert pii_service.scan_text("").types == ()


def test_valid_credit_card_is_detected():
    # A Luhn-valid Visa test number.
    finding = pii_service.scan_text("Card on file: 4111 1111 1111 1111")
    assert "credit_card" in finding.types


def test_invalid_card_number_is_not_flagged():
    # 16 digits but fails the Luhn check (valid Visa is ...1111).
    finding = pii_service.scan_text("Order ref 4111 1111 1111 1112")
    assert "credit_card" not in finding.types


def test_ip_address_is_detected():
    finding = pii_service.scan_text("Client connected from 192.168.1.42 today.")
    assert "ip_address" in finding.types


def test_secret_key_is_detected():
    finding = pii_service.scan_text("AWS key AKIAIOSFODNN7EXAMPLE leaked in logs.")
    assert "secret" in finding.types


def test_secret_raises_subscore_weight():
    plain = pii_service.subscore("jane@acme.example", None, None)
    with_secret = pii_service.subscore("AKIAIOSFODNN7EXAMPLE", None, None)
    assert with_secret > plain
