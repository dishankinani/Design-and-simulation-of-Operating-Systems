class ProgramLoadError(Exception):
    def __str__(self):
        return "Error: Cannot load a new program while another program is already ready to run at the same location."