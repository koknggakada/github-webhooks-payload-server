import cgi
import logging
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from io import BytesIO
from logging import RootLogger
from os import environ

from deploy import deploy

LOGFILE = 'server.log'


def create_logger():
    """Create logger"""
    logger = logging.getLogger('deploy_server')
    file_handler = logging.FileHandler(LOGFILE)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)
    return logger


logger: RootLogger = create_logger()


class ServerHandler(BaseHTTPRequestHandler):
    def _set_response(self):
        """Set response"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def _send_response(self, message: str = '{"status": "failed"}'):
        """Send response"""
        self._set_response()
        self.wfile.write(message.encode('utf-8'))

    def do_POST(self):
        """Handle post request on /"""
        if not str(self.path).startswith('/payload'):
            self._send_response()
            return

        content_length = int(self.headers['Content-Length'])
        request_body = self.rfile.read(content_length)

        try:
            form = cgi.FieldStorage(
                BytesIO(request_body),
                headers=self.headers,
                environ={
                    'REQUEST_METHOD': 'POST',
                    'CONTENT_TYPE': self.headers['Content-Type'],
                },
            )
        except Exception as e:
            logger.info(f"Exception,\n" f"{e}")
            self._send_response()
            return

        payload_str = form.getvalue('payload')
        secret = environ['GITHUB_WEBHOOKS_SECRET']
        github_sig = self.headers.get('X-Hub-Signature', '')
        deploy(github_sig, secret, request_body, payload_str)

        logger.info(
            f"POST request,\n"
            f"Path: {str(self.path)}\n"
            f"Headers:\n{str(self.headers)}"
            f"Keys:{form.keys()}\n"
            f"payload data:{form.getlist('payload')}\n"
        )

        self._send_response('{"status": "success"}')


def run_server(server_class=HTTPServer, handler_class=ServerHandler, port=8080):
    """Run server"""
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logger.info('Starting httpd...')
    logger.info(f'Serving at port {port}\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logger.info('Stopping httpd...')


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run_server(port=int(argv[1]))
    else:
        run_server()
