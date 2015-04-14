import re
import lampstand.reactions.base
import logging


def __init__():
    pass


class Reaction(lampstand.reactions.base.Reaction):
    __name = 'Nickserv'

    def __init__(self, connection):
        self.logger = logging.getLogger(self.__name)
        self.privateMatch = (
            re.compile(
                '^Please identify via', re.IGNORECASE), re.compile(
                '^Lampstand has been ghosted', re.IGNORECASE), re.compile(
                'Reidentify', re.IGNORECASE))

    def privateAction(self, connection, user, channel, message, matchindex=0):
        if matchindex == 0 or matchindex == 2:

            if user == 'NickServ' or user == "Aquarion":
                if connection.chanserv_password:
                    self.logger.info('[IDENTIFY] Identifying myself to %s ' % user)
                    response = "Identify %s" % connection.chanserv_password.encode(
                        'ascii')
                    connection.message('NickServ', response)
                    self.logger.info(response)
                else:
                    self.logger.info('[IDENTIFY] Couldn\'t Identify myself to %s, no password ' % user)
            else:
                self.logger.info('[IDENTIFY] I think %s is trying to scam my password' % user)
        elif matchindex == 1:
            connection.register(connection.original_nickname)
