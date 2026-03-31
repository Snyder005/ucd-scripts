#!/usr/bin/env ccs-script
from java.time import Duration
from org.lsst.ccs.scripting import CCS as _JavaCCS

class CCSProxy(object):
    
    def __init__(self, ccs, subsystem, target=None):
        self._ccs = ccs
        self._subsystem = subsystem
        self._target = target
        self._targets = set(ccs.sendSynchCommand("getCommandTargets"))
        self._child_proxies = {}

    def __getattr__(self, name):
        if hasattr(self._ccs, name):
            return getattr(self._ccs, name)

        target_path = self._build_target(name, include_subsystem=True)
        if target_path in self._targets:
            if target_path not in self._child_proxies:
                target = self._build_target(name)
                self._child_proxies[target_path] = CCSProxy(self._ccs, self._subsystem, target=target)
            return self._child_proxies[target_path]

        def forward(*args, **kwargs):
            is_async = kwargs.get('is_async', False)
            timeout = kwargs.get('timeout', None)

            command = self._build_command(name)
            if is_async:
                return self._ccs.sendAsynchCommand(command, args) 
            if timeout is not None:
                timeout = self.parse_timeout(timeout)
                return self._ccs.sendSynchCommand(timeout, command, args)
            else:
                return self._ccs.sendSynchCommand(command, args)

        return forward

    def __repr__(self):
        return "<CCSProxy subsystem={0!r} target={1!r}>".format(self._subsystem, self._target)

    def _build_command(self, name):
        return " ".join(filter(None, [self._target, name]))

    def _build_target(self, name, include_subsystem=False):
        parts = [self._target, name]
        if include_subsystem:
            parts = [self._subsystem] + parts
        return "/".join(filter(None, parts))

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

_JavaCCS.attachProxy = staticmethod(attachProxy)
CCS = _JavaCCS
