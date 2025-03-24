import logging
import argparse
from parser import Parser
from symboltable import SymbolTable


LOG = logging.getLogger(__name__)

class Assembler:
    def __init__(self, file_name: str):
        self.file_name = file_name
        LOG.info(f"Assembler initialized with file: {file_name}")
        self.parser = Parser(file_name)
        self.symbol_table = SymbolTable()
        self.output_file = file_name.split('.')[0] + ".hack"
        self.output_stream = open(self.output_file, 'w')

    def assemble(self):
        LOG.info(f"Assembling file: {self.file_name}")
        # First pass to build symbol table
        self._first_pass()
        # Second pass to generate machine code
        self.parser.reset()
        self._second_pass()
        self.output_stream.close()
        LOG.info(f"Assembly complete. Output written to {self.output_file}")
    
    def _first_pass(self):
        LOG.info("Starting first pass")
        current_address = 0  # Tracks the address of the next instruction

        while self.parser.hasMoreCommands():
            if self.parser.instructionType() == Parser.L_INSTRUCTION:
                # Extract the label symbol (e.g., LOOP from (LOOP))
                symbol = self.parser.symbol()
                # Add the label to the symbol table with the current address
                self.symbol_table.addEntry(symbol, current_address)
            else:
                # Only increment the address for actual instructions (A or C)
                current_address += 1
            self.parser.advance()

        LOG.info("First pass complete")
        LOG.debug(f"Symbol table: {self.symbol_table.table}")
    
    def _second_pass(self):
        LOG.info("Starting second pass")
        next_available_address = 16  # First available address for variables

        while self.parser.hasMoreCommands():
            binary_instruction = ""  # Initialize the binary instruction

            if self.parser.instructionType() == Parser.A_INSTRUCTION:
                symbol = self.parser.symbol()
                if symbol.isdigit():
                    # Numeric address (e.g., @5)
                    address = int(symbol)
                else:
                    # Symbolic address (e.g., @LOOP or @i)
                    if not self.symbol_table.contains(symbol):
                        # Add new variable to the symbol table
                        self.symbol_table.addEntry(symbol, next_available_address)
                        next_available_address += 1
                    address = self.symbol_table.getAddress(symbol)

                # Convert the address to a 15-bit binary string and prepend '0'
                binary_instruction = f"0{address:015b}"
                LOG.debug(f"A-instruction resolved: {symbol} -> {binary_instruction}")
            elif self.parser.instructionType() == Parser.C_INSTRUCTION:
                # Build the C-instruction
                binary_instruction = "111"  # Start of every C-instruction
                binary_instruction += self.parser.comp() if self.parser.comp() else "000000"
                binary_instruction += self.parser.dest() if self.parser.dest() else "000"
                binary_instruction += self.parser.jump() if self.parser.jump() else "000"
                LOG.debug(f"C-instruction resolved: {binary_instruction}")
            
            elif self.parser.instructionType() == Parser.L_INSTRUCTION:
                # Ignore labels in the second pass
                pass
            LOG.debug(f"Writing binary instruction: {binary_instruction}")
            # Write the binary instruction to the output file if it's not empty
            if binary_instruction:
                self.output_stream.write(binary_instruction + "\n")

            self.parser.advance()

        LOG.info("Second pass complete")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Hack Assembler")
    parser.add_argument("file_name", help="The path to the Hack assembly file to assemble")
    args = parser.parse_args()

    # Initialize and run the assembler
    assembler = Assembler(args.file_name)
    assembler.assemble()


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,  # Set the logging level (e.g., DEBUG, INFO, WARNING)
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Log format
        datefmt="%Y-%m-%d %H:%M:%S"  # Date format
    )
    LOG.info(f"HACK Assembler starting")
    main()