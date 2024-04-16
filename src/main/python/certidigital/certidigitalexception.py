""" Module that manages the possible business rules exceptions... """


class CertiDigitalException(Exception):
    """ Manages the possible business rules exceptions... """

    def __init__(self, message):
        self.__message = message
        super().__init__(self.message)

    @property
    def message(self):
        """ Returns the message associated with the exception occurred... """
        return self.__message

    @message.setter
    def message(self, value):
        self.__message = value
