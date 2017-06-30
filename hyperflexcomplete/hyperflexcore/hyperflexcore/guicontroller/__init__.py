import os
import sys
import ConfigParser

path = os.path.dirname(os.path.realpath(sys.argv[0]))
slash_idx = path.rfind(os.path.sep)
sys.path.insert(1, path[0:slash_idx + 1])

parser = ConfigParser.ConfigParser()
files = parser.read([
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        os.path.pardir,
        os.path.pardir,
        'config.cfg'
        ),
    '/usr/local/etc/hyperflex/config.cfg'
    ])
file = parser.read(files[0])

global_config = {}
for section in parser.sections():
    global_config[section] = {}
    for item, value in parser.items(section):
        try:
            global_config[section][item] = parser.get_int(section, item)
        except:
            global_config[section][item] = parser.get(section, item).strip("'")

guicontroller_config = global_config['guicontroller']
status_publisher_config = global_config['statuspublisher']

