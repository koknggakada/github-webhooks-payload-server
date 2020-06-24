import hashlib
import hmac
import json


def is_secure(github_sig: str, secret: str, request_body: bytes) -> bool:
    """Check secret key on header"""
    hex_sig = hmac.new(secret.encode(), request_body, hashlib.sha1).hexdigest()
    expected_sig = f'sha1={hex_sig}'
    if hmac.compare_digest(expected_sig, github_sig):
        return True
    return False


def is_deployable(payload: dict) -> bool:
    """
    Cek is deployable. Push or merge pull request
    on branch master
    """
    is_push_to_master = payload.get('ref', '') == 'refs/heads/master'
    try:
        is_merge_pr_to_master = (
            payload['action'] == 'closed'
            and payload['pull_request']['merged'] is True
            and payload['pull_request']['base']['ref'] == 'master'
        )
    except KeyError:
        is_merge_pr_to_master = False

    if is_push_to_master:
        return True
    elif is_merge_pr_to_master:
        return True

    return False


def to_dict(payload_str: str) -> dict:
    """Convert payload to json"""
    try:
        return json.loads(payload_str)
    except json.JSONDecodeError:
        pass
    return dict()


def run_command():
    """Run command"""
    print('git pull')
    print('Another command')


def deploy(github_sig: str, secret: str, request_body: bytes, payload_str: str):
    """Deploy"""
    if payload_str:
        payload = to_dict(payload_str)
        if payload:
            if is_secure(github_sig, secret, request_body) and is_deployable(payload):
                run_command()
