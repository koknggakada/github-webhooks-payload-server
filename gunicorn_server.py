import cgi
import json
from io import BytesIO
from os import environ

from original.deploy import deploy


def application(gunicorn_env, start_response):
    if (
        '/payload' in gunicorn_env['PATH_INFO']
        and gunicorn_env['REQUEST_METHOD'].upper() == 'POST'
    ):
        request_body = gunicorn_env['wsgi.input'].read()
        # This must be done to avoid a bug in cgi.FieldStorage
        environ.setdefault('QUERY_STRING', '')
        fs = cgi.FieldStorage(
            BytesIO(request_body), environ=gunicorn_env, keep_blank_values=1
        )
        payload_str = fs.getvalue('payload')
        secret = environ['GITHUB_WEBHOOKS_SECRET']
        github_sig = gunicorn_env.get('HTTP_X_HUB_SIGNATURE', '')
        deploy(github_sig, secret, request_body, payload_str)

    start_response('200 OK', [('Content-Type', 'application/json')])
    return [b'{"status": "success"}']
