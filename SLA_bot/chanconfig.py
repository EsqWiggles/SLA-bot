import configparser

class ChanConfig:
    def __init__(self):
        self._cf = configparser.ConfigParser(allow_no_value = True)

    def parse(self):
        try:
            chans = self._cf.items('Channels')
        except configparser.NoSectionError:
            chans = []
        channels = []
        for c in chans:
            id = c[0]
            filters = c[1].split(',')
            parsed = [int(x) for x in filters]
            channels.append((id, parsed))
        return channels
    
    def read(self, file_path):
        self._cf.read(file_path)

    def set(self, id, filters):
        try:
            self._cf.add_section('Channels')
        except configparser.DuplicateSectionError:
            pass
        self._cf.set('Channels', id, filters)
        
    def delete(self, id):
        self._cf.remove_option('Channels', id)
        
    def write(self, file_path):
        with open(file_path, "w") as config_file:
            self._cf.write(config_file)