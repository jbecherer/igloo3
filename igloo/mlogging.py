import logging

def get_logger(name, levelname):
    levels = dict(debug=logging.DEBUG,
                  info=logging.INFO,
                  warning=logging.WARNING,
                  error=logging.ERROR)

    logger = logging.getLogger("plotting")
    logger.setLevel(levels[levelname])
    ch = logging.StreamHandler()
    ch.setLevel(levels[levelname])
    fmt = logging.Formatter("%(levelname)s (%(name)s) : %(message)s")
    ch.setFormatter(fmt)
    logger.addHandler(ch)
    return logger
