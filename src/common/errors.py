class DatabaseError(Exception):
    pass

class InsertError(DatabaseError):
    pass

class InsertInDataBaseError(InsertError):
    pass

class TableError(DatabaseError):
    pass

class TableCreationError(TableError):
    pass

class SearchError(DatabaseError):
    pass

class AccountError(DatabaseError):
    pass

class StorageInputError(Exception):
    pass

class WrongDataTypeDict(StorageInputError):
    """
    This Error means that the given type is not a dictionary.
    The type needs to be changed to make it Work.
    """
    pass

class WrongDataTypeList(StorageInputError):
    """
    This Error means that the given tpye is not a List.
    The type needs to be changed to make it Work.
    """
    pass

class WrongDataTypeTuple(StorageInputError):
    pass


class DataLengthError(StorageInputError):
    """
    This Error means that the length isn't the same as the other one given.
    The list need to have the same length for this to work.     
    """

class InputValidationError(Exception):
    pass

class EmailMismatchError(InputValidationError):
    pass

class PasswordMismatchError(InputValidationError):
    pass

class InvalidPasswordError(InputValidationError):
    pass

class DuplicationError(Exception):
    pass

class WrongSQLStatement(Exception):
    pass

class UnexpectedError(Exception):
    pass

class DecryptionError(Exception):
    pass
