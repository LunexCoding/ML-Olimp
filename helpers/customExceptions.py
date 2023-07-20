class TypeException(Exception):
    def __init__(self, variable, receivedType, expectedType):
        self._variable = variable
        self._receivedType = receivedType
        self._expectedType = expectedType

    def __str__(self):
        return f"Wrong variable type: variable <{self._variable}> with type <{self._receivedType}>, expected type <{self._expectedType}>"
