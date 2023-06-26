from waitress import serve
from app.app import app
import logging

if __name__ == "__main__":
    # Logging info
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    ip = "127.0.0.1"
    port = 5000
    logger.info(f'Starting server on http://{ip}:{port}')

    # Server
    serve(app, host=ip, port=port)
