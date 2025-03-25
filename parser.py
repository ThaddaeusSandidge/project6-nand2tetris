"""
parser.py

Provides the Parser class for parsing Hack assembly commands and classifying
them as A-, C-, or L-instructions.
"""

import sys
import logging
from codemodule import CodeModule

LOG = logging.getLogger(__name__)

class Parser:
    """
    Parses each line of a Hack assembly file and provides convenient access
    to its components.
    """

    A_INSTRUCTION = "A_INSTRUCTION"
    C_INSTRUCTION = "C_INSTRUCTION"
    L_INSTRUCTION = "L_INSTRUCTION"

    def __init__(self, file_name: str):
        """
        Opens the input file and reads the first instruction.

        Args:
            file_name (str): Path to the Hack assembly file.
        """
        self.file_name = file_name
        self.current_instruction = None
        self.current_dest = None
        self.current_comp = None
        self.current_jump = None

        self.code_lookup = CodeModule()
        try:
            self.filestream = open(file_name, 'r')
        except FileNotFoundError:
            LOG.exception(f'Error: {file_name} not found')
            sys.exit(1)
        except IsADirectoryError:
            LOG.exception(f'Error: {file_name} is a directory')
            sys.exit(1)

        self._skip_comments_and_whitespace()
        LOG.debug(f'First instruction: {self.current_instruction}')
    
    def _skip_comments_and_whitespace(self):
        """
        Skips blank lines and comments to position at the next instruction.
        """
        in_multiline_comment = False

        while True:
            line = self.filestream.readline()
            if not line:
                self.current_instruction = None
                break

            stripped_line = line.strip()

            if in_multiline_comment:
                if '*/' in stripped_line:
                    in_multiline_comment = False
                continue

            if stripped_line.startswith('/*') or stripped_line.startswith('/**'):
                in_multiline_comment = True
                continue

            if stripped_line.startswith('//') or stripped_line == '':
                continue

            if '//' in stripped_line:
                stripped_line = stripped_line.split('//')[0].strip()

            self.current_instruction = stripped_line
            break
    
    def get_filestream(self):
        """Returns the current file stream."""
        return self.filestream
    
    def hasMoreCommands(self) -> bool:
        """Returns True if there are more instructions to parse."""
        return self.current_instruction is not None
    
    def advance(self):
        """
        Moves to the next instruction and parses its components (dest, comp, jump).
        """
        self._skip_comments_and_whitespace()
        LOG.debug(f'Current instruction: {self.current_instruction}')

        if self.current_instruction is not None:
            if '=' in self.current_instruction:
                self.current_dest = self.current_instruction.split('=')[0]
            else:
                self.current_dest = None
            
            if ';' in self.current_instruction:
                self.current_jump = self.current_instruction.split(';')[1]
            else:
                self.current_jump = None
            
            if '=' in self.current_instruction and ';' in self.current_instruction:
                comp_and_jump = self.current_instruction.split('=')[1]
                self.current_comp = comp_and_jump.split(';')[0]
            elif '=' in self.current_instruction:
                self.current_comp = self.current_instruction.split('=')[1]
            elif ';' in self.current_instruction:
                self.current_comp = self.current_instruction.split(';')[0]
            else:
                self.current_comp = self.current_instruction
            
            LOG.debug(f'Dest: {self.current_dest}')
            LOG.debug(f'Comp: {self.current_comp}')
            LOG.debug(f'Jump: {self.current_jump}')
        else:
            self.current_dest = None
            self.current_comp = None
            self.current_jump = None
            self.current_instruction = None
    
    def instructionType(self) -> str:
        """
        Determines the type of the current instruction.

        Returns:
            str: One of A_INSTRUCTION, C_INSTRUCTION, or L_INSTRUCTION.
        """
        if self.current_instruction.startswith('@'):
            return self.A_INSTRUCTION
        elif self.current_instruction.startswith('('):
            return self.L_INSTRUCTION
        else:
            return self.C_INSTRUCTION
    
    def symbol(self) -> str:
        """
        Extracts the symbol or decimal from an A- or L-instruction.

        Returns:
            str: The symbol (without @ or parentheses).

        Raises:
            Exception: If called on a C-instruction.
        """
        if self.instructionType() == self.A_INSTRUCTION:
            return self.current_instruction[1:]
        elif self.instructionType() == self.L_INSTRUCTION:
            return self.current_instruction[1:-1]
        else:
            raise Exception('Error: symbol() called on non-A or non-L instruction')

    def dest(self) -> str:
        """Returns binary code for dest part of C-instruction."""
        if self.instructionType() == self.C_INSTRUCTION:
            if self.current_dest is not None:
                return self.code_lookup.dest(self.current_dest)
            else:
                return None
        else:
            raise Exception('Error: dest() called on A or L instruction')
    
    def comp(self) -> str:
        """Returns binary code for comp part of C-instruction."""
        if self.instructionType() == self.C_INSTRUCTION:
            if self.current_comp is not None:
                return self.code_lookup.comp(self.current_comp)
            else:
                return None
        else:
            raise Exception('Error: comp() called on A or L instruction')
    
    def jump(self) -> str:
        """Returns binary code for jump part of C-instruction."""
        if self.instructionType() == self.C_INSTRUCTION:
            if self.current_jump is not None:
                return self.code_lookup.jump(self.current_jump)
            else:
                return None
        else:
            raise Exception('Error: jump() called on A or L instruction')
        
    def reset(self):
        """
        Resets the parser to the beginning of the file for the second pass.
        """
        self.filestream.seek(0)
        self._skip_comments_and_whitespace()
        LOG.debug(f'(SECOND PASS) First instruction: {self.current_instruction}')
