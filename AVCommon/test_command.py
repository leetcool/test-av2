from Command import Command

import os
import commands
import logging, sys
import logging.config

def test_commandAbstract():
    try:
        c = Command("START")
        assert("Should not be able to instance an abstract class" is False)
    except Exception:
        pass

def test_commandSerialize():
    c = Command.unserialize( ("START", False, "nothing") )
    s = c.serialize()
    cmd = Command.unserialize(s)
    assert(not cmd.success)

    logging.debug("cmd: %s %s", cmd, type(cmd))
    assert(str(cmd).startswith("START"))

    logging.debug("type: %s", type(cmd))
    assert(str(type(cmd)) == "<class 'Command_START.Command_START'>")

    Command.unserialize( ("START", None, None) )
    try:
        Command.unserialize( ("START", "", None) )
        assert(False)
    except:
        pass


def test_commandAnswer():
    c = Command.unserialize( ["START", True, ['whatever','end']])
    s = c.serialize()
    assert(len(s) == 3)
    cmd = Command.unserialize(s)
    logging.debug("unserisalized: %s" % type(cmd.answer))

    assert(cmd.success)
    assert(type(cmd.answer) == list)
    assert(cmd.answer == ['whatever','end'])
    assert(str(cmd).startswith("START"))


def test_commandStart():
    import Command_START
    c = Command_START.Command_START("START")
    assert(c)
    assert(c.name == "START")

    c.onInit()
    ret, answer = c.Execute()
    c.onAnswer(ret, answer)

if __name__ == '__main__':
    logging.config.fileConfig('../logging.conf')
    test_commandSerialize()
    test_commandStart()
    test_commandAnswer()
    test_commandAbstract()
