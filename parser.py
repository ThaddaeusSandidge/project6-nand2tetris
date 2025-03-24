import sys
import logging

from codemodule import CodeModule

LOG = logging.getLogger(__name__)



class Parser:

    A_INSTRUCTION = "A_INSTRUCTION"
    C_INSTRUCTION = "C_INSTRUCTION"
    L_INSTRUCTION = "L_INSTRUCTION"

    def __init__(self, file_name: str):
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

        # Perform a zero pass to skip comments and whitespace
        self._skip_comments_and_whitespace()
        LOG.debug(f'First instruction: {self.current_instruction}')
    
    def _skip_comments_and_whitespace(self):
        """Skip all comments and whitespace, positioning the file stream at the 
            first real line.
        """
        in_multiline_comment = False

        while True:
            line = self.filestream.readline()
            if not line:  # End of file
                self.current_instruction = None
                break

            stripped_line = line.strip()

            # Handle multi-line comments
            if in_multiline_comment:
                if '*/' in stripped_line:  # End of multi-line comment
                    in_multiline_comment = False
                continue

            if stripped_line.startswith('/*'):  # Start of multi-line comment
                in_multiline_comment = True
                continue

            # Skip single-line comments and empty lines
            if stripped_line.startswith('//') or stripped_line == '':
                continue

            # Skip doc comments (/** ... */)
            if stripped_line.startswith('/**'):
                in_multiline_comment = True
                continue

            # Found the first real line
            # ensure no comments at end of line
            if '//' in stripped_line:
                stripped_line = stripped_line.split('//')[0].strip()
            self.current_instruction = stripped_line
            break
    
    def get_filestream(self):
        return self.filestream
    
    def hasMoreCommands(self) -> bool:
        return self.current_instruction is not None
    
    def advance(self):
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
        if self.current_instruction.startswith('@'):
            return self.A_INSTRUCTION
        elif self.current_instruction.startswith('('):
            return self.L_INSTRUCTION
        else:
            return self.C_INSTRUCTION
    
    def symbol(self) -> str:
        if self.instructionType() == self.A_INSTRUCTION:
            return self.current_instruction[1:]
        elif self.instructionType() == self.L_INSTRUCTION:
            return self.current_instruction[1:-1]
        else:
            raise Exception('Error: symbol() called on non-A or non-L instruction')
    
    def symbol(self) -> str:
        if self.instructionType() == self.A_INSTRUCTION:
            return self.current_instruction[1:]
        elif self.instructionType() == self.L_INSTRUCTION:
            return self.current_instruction[1:-1]
        else:
            raise Exception('Error: symbol() called on non-A or non-L instruction')

    def dest(self) -> str:
        if self.instructionType() == self.C_INSTRUCTION:
            if self.current_dest is not None:
                LOG.debug(f'Dest: {self.current_dest}')
                return self.code_lookup.dest(self.current_dest)
            else:
                return None
        else:
            raise Exception('Error: dest() called on A or L instruction')
    def comp(self) -> str:
        if self.instructionType() == self.C_INSTRUCTION:
            if self.current_comp is not None:
                LOG.debug(f'Comp: {self.current_comp}')
                return self.code_lookup.comp(self.current_comp)
            else:
                return None
        else:
            raise Exception('Error: comp() called on A or L instruction')
    def jump(self) -> str:
        if self.instructionType() == self.C_INSTRUCTION:
            if self.current_jump is not None:
                LOG.debug(f'Jump: {self.current_jump}')
                return self.code_lookup.jump(self.current_jump)
            else:
                return None
        else:
            raise Exception('Error: jump() called on A or L instruction')
        
    def reset(self):
        self.filestream.seek(0)
        self._skip_comments_and_whitespace()
        LOG.debug(f'(SECOND PASS) First instruction: {self.current_instruction}')