import pytest

from Dodge import DODGE_ENDPOINT, dodge


class FakeResponse:
    def __init__(self, status_code, body=None):
        self.status_code = status_code
        self.body = body

    def json(self):
        if self.body is None:
            raise ValueError("no body")
        return self.body


class FakeRengar:
    def __init__(self, statuses):
        self.statuses = iter(statuses)
        self.calls = 0
        self.requests = []

    def lcu_request(self, method, endpoint, _body):
        self.calls += 1
        self.requests.append((method, endpoint))
        status = next(self.statuses)
        if isinstance(status, FakeResponse):
            return status
        return FakeResponse(status)


def test_dodge_uses_team_builder_quit_endpoint():
    api = FakeRengar([204] * 5)

    dodge(api)

    assert DODGE_ENDPOINT == "/lol-lobby-team-builder/champ-select/v1/session/quit"
    assert set(api.requests) == {("POST", DODGE_ENDPOINT)}


def test_dodge_sends_five_requests_after_success():
    api = FakeRengar([200] * 5)

    dodge(api)

    assert api.calls == 5


def test_dodge_succeeds_if_any_of_the_five_requests_succeeds():
    api = FakeRengar([500, 500, 204, 500, 500])

    dodge(api)

    assert api.calls == 5


def test_dodge_raises_after_bounded_attempts():
    api = FakeRengar([500] * 5)

    with pytest.raises(RuntimeError, match="HTTP 500"):
        dodge(api)

    assert api.calls == 5


def test_dodge_reports_client_error_message():
    not_in_champ_select = FakeResponse(
        404,
        {
            "errorCode": "RPC_ERROR",
            "httpStatus": 404,
            "message": "No champ select session in progress.",
        },
    )
    api = FakeRengar([not_in_champ_select] * 5)

    with pytest.raises(
        RuntimeError, match="HTTP 404: No champ select session in progress."
    ):
        dodge(api)
