import logging

LOG = logging.getLogger(__name__)

class SymbolTable:
    def __init__(self):
        self.table = {}

    def addEntry(self, symbol, value):
        LOG.debug(f'Adding {symbol} to table with value {value}')
        self.table[symbol] = value

    def contains(self, symbol):
        LOG.debug(f'Checking if {symbol} is in table')
        return symbol in self.table

    def getAddress(self, symbol):
        LOG.debug(f'Getting {symbol} from table')
        if symbol not in self.table:
            raise Exception(f'Error: {symbol} not found in table')
        return self.table[symbol]