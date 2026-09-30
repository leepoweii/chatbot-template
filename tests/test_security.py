"""LAN/公網曝露檢查：這個 template 的教材本來就會教「部署到區網讓同事連進來」
（見 W5 那堂 Flask 課），host 從 127.0.0.1 改成 0.0.0.0 是預期用法，不是 bug——
但「開放給整個網段連」跟「完全沒有密碼保護」疊在一起，是我們要攔的組合。"""
import pytest

from chatbot_template.security import lan_exposure_warning, require_basic_auth_if_exposed


def test_loopback_host_has_no_warning():
    assert lan_exposure_warning("127.0.0.1") is None
    assert lan_exposure_warning("localhost") is None


def test_bind_all_interfaces_warns():
    warning = lan_exposure_warning("0.0.0.0")
    assert warning is not None
    assert "0.0.0.0" in warning


def test_bind_a_specific_lan_ip_also_warns():
    """0.0.0.0 不是唯一的曝露方式——直接綁自己的區網 IP 一樣是開放給整個網段。"""
    warning = lan_exposure_warning("192.168.1.23")
    assert warning is not None


def test_refuses_to_start_exposed_without_auth_unless_explicitly_overridden():
    with pytest.raises(RuntimeError, match="BASIC_AUTH_PASSWORD|ALLOW_INSECURE_LAN"):
        require_basic_auth_if_exposed(host="0.0.0.0", auth_password=None, allow_insecure=False)


def test_allows_exposed_start_when_auth_password_set():
    require_basic_auth_if_exposed(host="0.0.0.0", auth_password="s3cr3t", allow_insecure=False)  # no raise


def test_allows_exposed_start_when_explicitly_overridden():
    require_basic_auth_if_exposed(host="0.0.0.0", auth_password=None, allow_insecure=True)  # no raise


def test_loopback_never_needs_auth():
    require_basic_auth_if_exposed(host="127.0.0.1", auth_password=None, allow_insecure=False)  # no raise
