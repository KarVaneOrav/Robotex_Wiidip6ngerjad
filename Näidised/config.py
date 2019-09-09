from configparser import ConfigParser, NoSectionError, NoOptionError
from pathlib import Path
from ast import literal_eval

# Important directories
src_dir = Path(__file__).parent
root_dir = src_dir.parent

# Important files
config_filepath = root_dir.joinpath("config.ini")

# INI parser
parser = ConfigParser()
parser.read(config_filepath)

# Get value from config
def get(section, key, default=None):
    try:
        return literal_eval(parser.get(section, key))
    except NoSectionError:
        return default
    except NoOptionError:
        return default

# Set value in config
def set(section, key, value):
    try:
        parser.set(section, key, repr(value))
    except NoSectionError:
        parser.add_section(section)
        parser.set(section, key, repr(value))

# Save changes
def save():
    with open(config_filepath, "w") as file:
        parser.write(file)