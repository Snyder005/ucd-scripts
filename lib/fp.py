## Interfaces with ucd-fp subsystem
from org.lsst.ccs.scripting import CCS
from org.lsst.ccs.bus.states import AlertState
from java.time import Duration
import logging

logger = logging.getLogger(__name__)

CLEARDELAY = 0.07
TIMEOUT = Duration.ofSeconds(60)

fp = CCS.attachProxy("ucd-fp")

def sanity_check(): # Change name to prevent collision with other systems?
    """Check state of the focal plane subsystem.
    """
    state = fp.getState()
    alert = state.getState(AlertState)
    if alert != AlertState.NOMINAL:
        agent_name = fp.getAgentProperty("agentName")
        logger.warning("{0} subsystem is in alert state {1}".format(agent_name, alert))

def clear(n=1):
    """Clear CCD a specific number of times.

    Parameters
    ----------
    n : `int`
        The number of clears (1 by default).
    """
    if n == 0:
        return
    logger.debug("Clearing CCDs {0:d}".format(n))
    fp.clear(n)
    fp.waitForSequencer(Duration.ofSeconds(2))

def take_exposure(expose_command=None, fits_header_data=None, locations=None, clears=1):
    """Take an exposure using specified options.

    Parameters
    ----------
    expose_command: # method
        Function that defineds the exposure.
    fits_header_data: `dict`
        Dictionary of stuff to go in the header.
    annotation: `str`
        Idk
    locations: `list` [`str`]
        A list of CCD names to used in the exposure.
    clears: `int`
        The number of clears (1 by default).
    """
    sanity_check()
    logger.debug("Setting Fits headers {0}".format(fits_header_data))
    fp.setHeaderKeywords(fits_header_data)
    clear(clears)
    fp.startIntegration(annotation, locations)

    if expose_command: # Why is this needed, shouldn't it be defined?
        extra_data = expose_command()
        if extra_data: # What does this do?
            fp.setHeaderKeywords(extra_data)

    try:
        fp.endIntegration()
        im = fp.waitForFitsFiles(TIMEOUT)
    except:
        raise # Make a specific eror here?

    return im # What is the format of this?
