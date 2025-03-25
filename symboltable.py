"""
symboltable.py

Contains the SymbolTable class for managing symbols and their addresses
during the assembly process.
"""

import logging

LOG = logging.getLogger(__name__)

class SymbolTable:
    """
    Represents the symbol table that keeps track of variable, label, and predefined addresses.
    """

    def __init__(self):
        """
        Initializes the symbol table with predefined Hack symbols.
        """
        self.table = {
            "R0": 0, "R1": 1, "R2": 2, "R3": 3,
            "R4": 4, "R5": 5, "R6": 6, "R7": 7,
            "R8": 8, "R9": 9, "R10": 10, "R11": 11,
            "R12": 12, "R13": 13, "R14": 14, "R15": 15,
            "SCREEN": 16384, "KBD": 24576,
            "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4
        }

    def addEntry(self, symbol, value):
        """
        Adds a new symbol and its address to the symbol table.

        Args:
            symbol (str): The symbol name.
            value (int): The corresponding memory address.
        """
        LOG.debug(f'Adding {symbol} to table with value {value}')
        self.table[symbol] = value

    def contains(self, symbol):
        """
        Checks if a symbol already exists in the table.

        Args:
            symbol (str): The symbol to check.

        Returns:
            bool: True if symbol is in the table, else False.
        """
        LOG.debug(f'Checking if {symbol} is in table')
        return symbol in self.table

    def getAddress(self, symbol):
        """
        Retrieves the address associated with a symbol.

        Args:
            symbol (str): The symbol name.

        Returns:
            int: The memory address associated with the symbol.

        Raises:
            Exception: If the symbol is not found in the table.
        """
        LOG.debug(f'Getting {symbol} from table')
        if symbol not in self.table:
            raise Exception(f'Error: {symbol} not found in table')
        return self.table[symbol]