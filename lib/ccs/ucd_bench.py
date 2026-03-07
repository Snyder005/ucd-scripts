import logging

from ccs.shutter import SciinTechPS500Device

logger = logging.getLogger(__name__)

class UCDBench(object):

    def __init__(self, shutter_id):
        self.shutter = SciinTechPS500Device(shutter_id)
