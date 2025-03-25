"""
assembler.py

This module contains the Assembler class that coordinates the translation
of Hack assembly code into binary machine code using a two-pass algorithm.
"""

import logging
import argparse
from parser import Parser
from symboltable import SymbolTable

LOG = logging.getLogger(__name__)

class Assembler:
    """
    Assembler class for translating Hack assembly (.asm) files into binary (.hack) files.
    """

    def __init__(self, file_name: str):
        """
        Initializes the assembler with the given file.

        Args:
            file_name (str): The path to the Hack assembly file.
        """
        self.file_name = file_name
        LOG.info(f"Assembler initialized with file: {file_name}")
        self.parser = Parser(file_name)
        self.symbol_table = SymbolTable()
        self.output_file = file_name.split('.')[0] + ".hack"
        self.output_stream = open(self.output_file, 'w')

    def assemble(self):
        """
        Runs the two-pass assembly process and writes binary output to the .hack file.
        """
        LOG.info(f"Assembling file: {self.file_name}")
        self._first_pass()
        self.parser.reset()
        self._second_pass()
        self.output_stream.close()
        LOG.info(f"Assembly complete. Output written to {self.output_file}")
    
    def _first_pass(self):
        """
        First pass: Scans for label definitions (L-instructions) and populates the symbol table.
        """
        LOG.info("Starting first pass")
        current_address = 0

        while self.parser.hasMoreCommands():
            if self.parser.instructionType() == Parser.L_INSTRUCTION:
                symbol = self.parser.symbol()
                self.symbol_table.addEntry(symbol, current_address)
            else:
                current_address += 1
            self.parser.advance()

        LOG.info("First pass complete")
        LOG.debug(f"Symbol table: {self.symbol_table.table}")
    
    def _second_pass(self):
        """
        Second pass: Translates A- and C-instructions into binary and writes to output file.
        """
        LOG.info("Starting second pass")
        next_available_address = 16

        while self.parser.hasMoreCommands():
            binary_instruction = ""

            if self.parser.instructionType() == Parser.A_INSTRUCTION:
                symbol = self.parser.symbol()
                if symbol.isdigit():
                    address = int(symbol)
                else:
                    if not self.symbol_table.contains(symbol):
                        self.symbol_table.addEntry(symbol, next_available_address)
                        next_available_address += 1
                    address = self.symbol_table.getAddress(symbol)

                binary_instruction = f"0{address:015b}"
                LOG.debug(f"A-instruction resolved: {symbol} -> {binary_instruction}")
            elif self.parser.instructionType() == Parser.C_INSTRUCTION:
                binary_instruction = "111"
                binary_instruction += self.parser.comp() if self.parser.comp() else "000000"
                binary_instruction += self.parser.dest() if self.parser.dest() else "000"
                binary_instruction += self.parser.jump() if self.parser.jump() else "000"
                LOG.debug(f"C-instruction resolved: {binary_instruction}")
            elif self.parser.instructionType() == Parser.L_INSTRUCTION:
                pass

            if binary_instruction:
                self.output_stream.write(binary_instruction + "\n")

            self.parser.advance()

        LOG.info("Second pass complete")


def main():
    """
    Main entry point. Parses command-line arguments and runs the assembler.
    """
    parser = argparse.ArgumentParser(description="Hack Assembler")
    parser.add_argument("file_name", help="The path to the Hack assembly file to assemble")
    args = parser.parse_args()

    assembler = Assembler(args.file_name)
    assembler.assemble()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    LOG.info(f"HACK Assembler starting")
    main()
