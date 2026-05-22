from sekoia_automation.module import Module
from locaterisk_modules.models import LocateriskModuleConfiguration


class LocateriskModule(Module):
    configuration: LocateriskModuleConfiguration
