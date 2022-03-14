from tempfile import SpooledTemporaryFile
from typing import AnyStr


class BinFile(SpooledTemporaryFile):
    """
    BinFile is a temporary binary file. Because BinFile converts strings to bytes in write operation, 
    it is useful when used for Django serialize (only supports str) and Azure Storage upload (only supports bytes).
    """

    def __init__(self, max_size=0):
        super().__init__(max_size=max_size)

    def write(self, s: AnyStr) -> int:
        if type(s) == str:
            return super().write(s.encode("utf8"))
        return super().write(s)
