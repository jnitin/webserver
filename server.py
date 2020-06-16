"""This is main server file"""
import os
from http.server import CGIHTTPRequestHandler, ThreadingHTTPServer
import logging
from sys import argv
from io import BytesIO
import threading

LOG_FILENAME = "webserverlog.txt"
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.FileHandler(filename=LOG_FILENAME)
# create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)


# -------------------------------------------------------------------------------

class ServerException(Exception):
    """For internal error reporting."""
    pass

# -------------------------------------------------------------------------------


class BaseCase:
    """Parent for case handlers."""

    @staticmethod
    def handle_file(handler, full_path):
        """This is static hanle file method with two args as handler and full_path"""

        try:
            with open(full_path, 'rb') as reader:
                content = reader.read()
            handler.send_content(content)
        except IOError as msg:
            msg = "'{0}' cannot be read: {1}".format(full_path, msg)
            handler.handle_error(msg)

    @staticmethod
    def index_path(handler):
        """This is static index path method with one args as handler"""
        return os.path.join(handler.full_path, 'index.html')

    @staticmethod
    def forms_path(handler):
        """This is static forms path method with one args as handler"""
        return os.path.join(handler.full_path, 'forms.html')

    @staticmethod
    def form_get_path(handler):
        """This is static form get path method with one args as handler"""
        return os.path.join(handler.full_path, 'form_get.html')

    def test(self, handler):
        """This is test method with one args as handler"""
        print("This will override from child classes", handler.full_path)

    def act(self, handler):
        """This is act method with one args as handler"""
        print("This will override from child classes", handler.full_path)


# -------------------------------------------------------------------------------
class CaseNoFile(BaseCase):
    """File or directory does not exist."""

    def test(self, handler):
        file_ath = handler.full_path.split("?", 1)
        path = file_ath[0]
        return not os.path.exists(path)

    def act(self, handler):
        raise ServerException("'{0}' not found".format(handler.path))


# -------------------------------------------------------------------------------
class CaseCgiFile(BaseCase):
    """cgi file exists"""

    @staticmethod
    def run_cgi(handler):
        """This is static run_cgi method with one args as handler"""
        cmd = "python " + handler.full_path
        child_stdin, child_stdout = os.popen(cmd)
        child_stdin.close()
        data = child_stdout.read()
        child_stdout.close()
        handler.send_content(data)

    def test(self, handler):
        return handler.is_cgi()

    def act(self, handler):
        handler.run_cgi()


# -------------------------------------------------------------------------------


class CaseExistingFile(BaseCase):
    """File exists."""

    def test(self, handler):
        return os.path.isfile(handler.full_path)

    def act(self, handler):
        self.handle_file(handler, handler.full_path)

# -------------------------------------------------------------------------------


class CaseDirectoryIndexFile(BaseCase):
    """Serve index.html page for a directory."""

    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
               os.path.isfile(self.index_path(handler))

    def act(self, handler):
        self.handle_file(handler, self.index_path(handler))


# -------------------------------------------------------------------------------

class CaseDirectoryNoIndexFile(BaseCase):
    """Serve listing for a directory without an index.html page."""

    # How to display a directory listing.
    Listing_Page = '''\
        <html>
        <body>
        <ul>
        {0}
        </ul>
        </body>
        </html>
        '''

    def list_dir(self, handler, full_path):
        """This is list_dir method with two args as handler and full_path"""
        try:
            entries = os.listdir(full_path)
            bullets = ['<li>{0}</li>'.format(e) for e in entries if not e.startswith('.')]
            page = self.Listing_Page.format('\n'.join(bullets))
            handler.send_content(page.encode('utf-8'))
        except OSError as msg:
            msg = "'{0}' cannot be listed: {1}".format(self.path, msg)
            handler.handle_error(msg)

    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
               not os.path.isfile(self.index_path(handler))

    def act(self, handler):
        self.list_dir(handler, handler.full_path)


# ------------------------------------------------------------------------------


class CaseAlwaysFail(BaseCase):
    """Base case if nothing else worked."""

    def test(self, handler):
        return True

    def act(self, handler):
        raise ServerException("Unknown object '{0}'".format(handler.path))


# -------------------------------------------------------------------------------


# noinspection PyAttributeOutsideInit


class RequestHandler(CGIHTTPRequestHandler):
    """If the requested path maps to a file, that file is served.
    If anything goes wrong, an error page is constructed."""
    logger.info("Request handle is processed, in case of failure error page is constructed.")

    protocol_version = 'HTTP/1.1'
    logger.info("USing protocol version: %s", str(protocol_version))

    buffer = 1
    log_file = open(LOG_FILENAME, 'w', buffer)

    Cases = [CaseNoFile(),
             CaseCgiFile(),
             CaseExistingFile(),
             CaseDirectoryIndexFile(),
             CaseDirectoryNoIndexFile(),
             CaseAlwaysFail()]

    # How to display an error.
    Error_Page = """\
        <html>
        <body>
        <h1>Error accessing {path}</h1>
        <p>{msg}</p>
        </body>
        </html>
        """

    def guess_type(self, path):
        mimetype = CGIHTTPRequestHandler.guess_type(self, path)
        logger.info("Type of request handler: %s", str(mimetype))
        if mimetype == 'application/octet-stream':
            if path.endswith('manifest'):
                mimetype = 'text/cache-manifest'
        return mimetype

    # Classify and handle request.

    def do_HEAD(self):
        logger.info("Thread Count :%s ", threading.active_count())
        logger.info("\n%s\nPath: %s\nHeaders:\n%s",
                    str(self.requestline), str(self.path), str(self.headers))
        self.close_connection = True

    def do_GET(self):
        logger.info("Thread Count :%s ", threading.active_count())
        logger.info("\n%s\nPath: %s\nHeaders:\n%s",
                    str(self.requestline), str(self.path), str(self.headers))
        try:
            print("Get method call")
            self.full_path = os.getcwd() + self.path

            for case in self.Cases:
                if case.test(self):
                    logger.info("In case if test is successful action is processed at path: %s",
                                str(self.full_path))
                    case.act(self)
                    break

        except Exception as msg:
            logger.info("Exception occurred with msg: %s :", msg)
            self.handle_error(msg)

    def do_POST(self):
        logger.info("\n%s\nPath: %s\nHeaders:\n%s",
                    str(self.requestline), str(self.path), str(self.headers))
        print("Post method call")
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        logger.info(str(body))
        self.send_response(200)
        self.end_headers()
        response = BytesIO()
        logger.info("Response to be posted: %s", str(response))
        response.write(b'This is POST request. ')
        response.write(b'Received: ')
        response.write(body)
        self.wfile.write(response.getvalue())
        self.close_connection = True

    def do_PUT(self):
        """This is do_PUT method"""
        logger.info("\n%s\nPath: %s\nHeaders:\n%s",
                    str(self.requestline), str(self.path), str(self.headers))
        filename = os.path.basename(self.path)
        file_length = int(self.headers['Content-Length'])
        with open(filename, 'wb') as output_file:
            logger.info("File %s is opened to write response", str(filename))
            output_file.write(self.rfile.read(file_length))
        self.send_response(201, 'Created')
        self.end_headers()
        reply_body = 'Saved "%s"\n' % filename
        logger.info("Replying with: %d", str(reply_body))
        self.wfile.write(reply_body.encode('utf-8'))
        self.close_connection = True

    # Handle unknown objects.
    def handle_error(self, msg):
        """This is handler error method with one args as msg"""
        logger.info('handle_error msg %s', str(msg))
        content = self.Error_Page.format(path=self.path, msg=msg)
        self.send_content(content, 404)

    # Send actual content.
    def send_content(self, content, status=200):
        """This is send_content method with two args as content and status"""
        logger.info('send_content...\n')
        self.send_response(status)
        ctype = self.guess_type(path=self.full_path)
        if ctype == 'application/octet-stream':
            ctype = 'text/html'
        self.send_header("Content-type", ctype)
        logger.info("Header is sent with type: %s", ctype)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format, *args):
        self.log_file.write("%s - - [%s] %s\n" %
                            (self.client_address[0],
                             self.log_date_time_string(),
                             format % args))

# -------------------------------------------------------------------------------


def run(server_class=ThreadingHTTPServer, handler_class=RequestHandler, port=8080):
    """This is run method with three args as ThreadingHTTPServer,  RequestHandler, and port"""
    server_address = ('', port)
    server = server_class(server_address, handler_class)
    logger.info('Starting webserver...\n')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
    logger.info('Stopping webserver...\n')


if __name__ == '__main__':
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
