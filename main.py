from helpers import settings
from .web import app, socket
from .trade import Trader
import logging

logging.basicConfig(format=settings.LOGGING_FORMAT)
logging.getLogger(__name__).setLevel(settings.LOGGING_LEVEL)

if __name__ == '__main__':
    socket.run(app, debug=False)
    trader = Trader()