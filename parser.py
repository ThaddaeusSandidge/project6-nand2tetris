import os
import sys
import logging

LOG = logging.getLogger(__name__)

class Parser:
    def __init__(self, file_name: str):
        self.file_name = file_name
        try:
            self.filestream = open(file_name, 'r')
        except FileNotFoundError:
            LOG.exception(f'Error: {file_name} not found')
            sys.exit(1)
        except IsADirectoryError:
            LOG.exception(f'Error: {file_name} is a directory')
            sys.exit(1)
    
    def get_filestream(self):
        return self.filestream
    
    def hasMoreCommands(self) -> bool:
        return self.filestream.readline() != ''