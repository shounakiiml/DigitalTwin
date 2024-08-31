import yaml

""" Importing press list from the configuration file"""
def define_config():
    with open("E:/pythonProject/FloorMachineDashboard/config.yaml", 'r') as stream:
        config_loaded = yaml.safe_load(stream)
        return config_loaded