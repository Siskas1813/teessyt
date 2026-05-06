import os

from webmail import create_app


app = create_app()


def _get_bool_env(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)

    if value is None:
        return default

    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


if __name__ == '__main__':
    host = os.environ.get('APP_HOST', '127.0.0.1')
    port = int(os.environ.get('APP_PORT', '5000'))
    debug = _get_bool_env('APP_DEBUG', False)

    app.run(host=host, port=port, debug=debug)