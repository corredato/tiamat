from Rengar import Rengar


# The lcdsServiceProxy invoke route (/lol-login/v1/session/invoke) was removed from
# the LCU and now answers 404 RESOURCE_NOT_FOUND; this is its replacement.
DODGE_ENDPOINT = "/lol-lobby-team-builder/champ-select/v1/session/quit"
DODGE_REQUEST_COUNT = 5


def _error_message(response):
    try:
        return response.json().get("message") or None
    except Exception:
        return None


def dodge(rengar=None):
    api = rengar or Rengar()
    last_status = None
    last_message = None
    last_error = None
    succeeded = False
    for _ in range(DODGE_REQUEST_COUNT):
        try:
            response = api.lcu_request("POST", DODGE_ENDPOINT, "")
        except Exception as error:
            last_error = error
            continue
        last_status = response.status_code
        if 200 <= response.status_code < 300:
            succeeded = True
        else:
            last_message = _error_message(response)
    if succeeded:
        return
    if last_status is None and last_error is not None:
        raise RuntimeError(f"Could not dodge champion select ({last_error})")
    if last_message:
        raise RuntimeError(
            f"Could not dodge champion select (HTTP {last_status}: {last_message})"
        )
    raise RuntimeError(f"Could not dodge champion select (HTTP {last_status})")
