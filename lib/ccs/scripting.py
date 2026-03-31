#!/usr/bin/env ccs-script
# are underscores necessary?
from java.time import Duration
from org.lsst.ccs.scripting import CCS as _JavaCCS

class CCSProxy(object):
    
    def __init__(self, ccs, subsystemName):
        self._ccs = ccs
        self._subsystem = subsystemName
        self._target = None
        self._targets = set(ccs.sendSynchCommand("getCommandTargets"))

    def __getattr__(self, name):
        if hasattr(self._ccs, name):
            return getattr(self._ccs, name)

        if self._build_target_path(name) in self._targets:
            def create_proxy():
                proxy = CCSProxy(self._ccs, self._subsystem)
                proxy._target = self._build_target(name)
                return proxy
            return create_proxy         

        def forward(*args, async_call=False, timeout=None):
            command = self._build_command(name) if self._target is not None else name
            if async_call:
                return self._ccs.sendAsynchCommand(command, args) 
            if timeout is not None:
                timeout = self.parse_timeout(timeout)
                return self._ccs.sendSynchCommand(timeout, command, args)
            else:
                return self._ccs.sendSynchCommand(command, args)

        return forward

    def __repr__(self):
        return "<CCSProxy subsystem={0!r} target={1!r}>" % (self._subsystem, self._target)

    def _build_command(self, name):
        return " ".join([self._target], name)

    def _build_target(self, name):
        return "/".join(filter(None, [self._target, name]))

    def _build_target_path(self, name):
        return "/".join(filter(None, [self._subsystem, self._target, name]))

    @staticmethod
    def parse_timeout(timeout):
        if isinstance(timeout, Duration):
            return timeout
        if isinstance(timeout, int):
            return Duration.ofSeconds(timeout)
        if isinstance(timeout, str):
            return Duration.parse(timeout)
        raise TypeError("Invalid timeout: {0!r}".format(timeout))

def attachProxy(key, level=0):
   return CCSProxy(_JavaCCS.attachSubsystem(key, level), key)

_JavaCCS.attachProxy = attachProxy

CCS = _JavaCCS
