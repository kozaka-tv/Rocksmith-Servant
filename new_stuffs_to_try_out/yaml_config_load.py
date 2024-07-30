import yaml


class Test1Class:
    def __init__(self, raw):
        self.minVolt = raw['minVolt']
        self.maxVolt = raw['maxVolt']


class Test2Class:
    def __init__(self, raw):
        self.curr = raw['curr']
        self.volt = raw['volt']


class Config:
    def __init__(self, raw):
        self.test1 = Test1Class(raw['test1'])
        self.test2 = Test2Class(raw['test2'])


yaml_file = yaml.safe_load(
    """
    test1:
        minVolt: -1
        maxVolt: 1
    test2:
        curr: 5
        volt: 5
    """
)

config = Config(yaml_file)

print(f"minVolt={config.test1.minVolt}")
