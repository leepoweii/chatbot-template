"""LAN/公網曝露檢查。這個 template 的教材本來就會教「改 host 部署到區網」（W5
Flask 課的教法），所以 0.0.0.0 不是我們要禁止的事，是預期用法——真正要攔的是
「開放給整個網段連、卻完全沒有密碼」這個組合。127.0.0.1/localhost 永遠不需要理它，
那本來就只有這台機器自己連得到。"""
import ipaddress


def _is_loopback(host: str) -> bool:
    if host == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def lan_exposure_warning(host: str) -> str | None:
    """回傳一句給使用者看的警告，或 None（loopback，沒事）。"""
    if _is_loopback(host):
        return None
    return (
        f"⚠️ 這個服務會綁在 {host}，同網段的人都連得到，不是只有你自己。"
        "如果這不是你要的（例如你只是想在本機測試），把 HOST 改回 127.0.0.1。"
    )


def require_basic_auth_if_exposed(host: str, auth_password: str | None, allow_insecure: bool) -> None:
    """曝露給網段卻沒密碼、也沒明確說「我知道風險」——直接擋住啟動，別讓它默默上線。

    不是自動幫你開 auth（那要真的接進 Flask app 的 before_request），
    這裡只負責「擋住裸奔的組合」，逼你在 .env 做一個明確的選擇。
    """
    if _is_loopback(host):
        return
    if auth_password:
        return
    if allow_insecure:
        return
    raise RuntimeError(
        f"拒絕啟動：HOST={host} 會開放給整個網段，但沒有設密碼保護。"
        "二選一：在 .env 設 BASIC_AUTH_PASSWORD（推薦），"
        "或明確設 ALLOW_INSECURE_LAN=true（如果你確定這個網路安全、知道自己在做什麼）。"
    )
