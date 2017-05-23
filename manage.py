import sys
import os
import ssl

import click
from flask.cli import pass_script_info

from application import create_app

app = create_app()


@app.cli.command('runssl', short_help='Runs a development server.')
@click.option('--host', '-h', default='127.0.0.1',
              help='The interface to bind to.')
@click.option('--port', '-p', default=5000,
              help='The port to bind to.')
@click.option('--reload/--no-reload', default=None,
              help='Enable or disable the reloader.  By default the reloader '
              'is active if debug is enabled.')
@click.option('--debugger/--no-debugger', default=None,
              help='Enable or disable the debugger.  By default the debugger '
              'is active if debug is enabled.')
@click.option('--eager-loading/--lazy-loader', default=None,
              help='Enable or disable eager loading.  By default eager '
              'loading is enabled if the reloader is disabled.')
@click.option('--with-threads/--without-threads', default=False,
              help='Enable or disable multithreading.')
@pass_script_info
def run_command(info, host, port, reload, debugger, eager_loading,
                with_threads):
    """Runs a local development server for the Flask application.

    This local server is recommended for development purposes only but it
    can also be used for simple intranet deployments.  By default it will
    not support any sort of concurrency at all to simplify debugging.  This
    can be changed with the --with-threads option which will enable basic
    multithreading.

    The reloader and debugger are by default enabled if the debug flag of
    Flask is enabled and disabled otherwise.

    Runs https with self singed certificates for localhost.
    """

    # get certificates or exit
    base = os.path.abspath(os.path.dirname(__file__))
    keyfiles = set(['localhost.crt', 'localhost.key'])
    dirfiles = set(os.listdir(base))
    missing = keyfiles.difference(dirfiles)

    if not keyfiles.issubset(dirfiles):
        click.secho('{} not found.'.format(" and ".join(missing)), fg='red')
        click.echo('Create a certificate with the following command: ')
        click.secho('openssl req -nodes -x509 -subj "/CN=localhost" -sha256 '
                    '-newkey rsa:4096 -keyout localhost.key -out localhost.crt '
                    '-days 365', fg='yellow')
        return

    from flask.globals import _app_ctx_stack
    app = _app_ctx_stack.top.app
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(certfile='localhost.crt',
                            keyfile='localhost.key')

    from werkzeug.serving import run_simple
    from flask.cli import get_debug_flag, DispatchingApp

    debug = get_debug_flag()
    if reload is None:
        reload = bool(debug)
    if debugger is None:
        debugger = bool(debug)
    if eager_loading is None:
        eager_loading = not reload

    app = DispatchingApp(info.load_app, use_eager_loading=eager_loading)

    # Extra startup messages.  This depends a bit on Werkzeug internals to
    # not double execute when the reloader kicks in.
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        # If we have an import path we can print it out now which can help
        # people understand what's being served.  If we do not have an
        # import path because the app was loaded through a callback then
        # we won't print anything.
        if info.app_import_path is not None:
            print(' * Serving Flask app "%s"' % info.app_import_path)
        if debug is not None:
            print(' * Forcing debug mode %s' % (debug and 'on' or 'off'))

    run_simple(host, port, app, use_reloader=reload, ssl_context=context,
               use_debugger=debugger, threaded=with_threads)


@app.cli.command('test')
def test():
    """Runs the tests in 'tests'."""
    import unittest
    tests = unittest.TestLoader().discover('tests', pattern='*.py')
    unittest.TextTestRunner(verbosity=2).run(tests)


@app.cli.command('routes')
def routes():
    """Prints out all routes."""
    click.echo("{:50s} {:40s} {}".format('Endpoint', 'Methods', 'Route'))
    for route in app.url_map.iter_rules():
        methods = ','.join(route.methods)
        click.echo("{:50s} {:40s} {}".format(route.endpoint, methods, route))


@app.cli.command('ipython')
def ipython():
    """Runs a ipython shell in the app context."""
    try:
        import IPython
    except ImportError:
        click.echo("IPython not found. Install with: 'pip install ipython'")
        return
    from flask.globals import _app_ctx_stack
    app = _app_ctx_stack.top.app
    banner = 'Python %s on %s\nIPython: %s\nApp: %s%s\nInstance: %s\n' % (
        sys.version,
        sys.platform,
        IPython.__version__,
        app.import_name,
        app.debug and ' [debug]' or '',
        app.instance_path,
    )

    ctx = {}

    # Support the regular Python interpreter startup script if someone
    # is using it.
    startup = os.environ.get('PYTHONSTARTUP')
    if startup and os.path.isfile(startup):
        with open(startup, 'r') as f:
            eval(compile(f.read(), startup, 'exec'), ctx)

    ctx.update(app.make_shell_context())

    IPython.embed(banner1=banner, user_ns=ctx)
