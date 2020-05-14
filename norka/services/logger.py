# logger.py
#
# MIT License
#
# Copyright (c) 2020 Andrey Maksimov <meamka@ya.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import logging
import sys

from norka.define import APP_ID, DEBUG


class Logger:
    FORMAT = "[%(levelname)-s] %(asctime)s %(message)s"
    DATE = "%Y-%m-%d %H:%M:%S"
    _log = None

    @staticmethod
    def get_default():
        """Return default instance of :class:`Logger`

        :return: :class:`Logger`
        """
        if Logger._log is None:
            logger = logging.getLogger(APP_ID)

            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(Logger.FORMAT, Logger.DATE)
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)

            Logger._log = logging.getLogger(APP_ID)
        return Logger._log

    @staticmethod
    def warning(msg, *args):
        """Log warning message

        :param msg: message to log
        :type msg: str
        """
        Logger.get_default().warning(msg, *args)

    @staticmethod
    def debug(msg, *args):
        """Log debug message

        :param msg: message to log
        :type msg: str
        """
        if DEBUG:
            Logger.get_default().debug(msg, *args)

    @staticmethod
    def info(msg, *args):
        """Log info message

        :param msg: message to log
        :type msg: str
        """
        Logger.get_default().info(msg, *args)

    @staticmethod
    def error(msg, *args):
        """Log error message

        :param msg: message to log
        :type msg: str
        """
        Logger.get_default().error(msg, *args)
