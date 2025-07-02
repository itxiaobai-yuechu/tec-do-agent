from configparser import ConfigParser


class Config:
    def __init__(self):
        self.conf = ConfigParser()
        self.conf.read('env.ini')

    def get(self, config: str, environment: str = 'dev') -> str:
        return self.conf[environment][config]


conf = Config()
