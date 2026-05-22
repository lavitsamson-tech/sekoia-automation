from locaterisk_modules import LocateriskModule

from locaterisk_modules.connector import LocateriskConnector


if __name__ == "__main__":
    module = LocateriskModule()
    module.register(LocateriskConnector, "LocateriskConnector")
    module.run()
