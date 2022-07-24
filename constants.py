from enum import Enum


class OpenAPIDataTypes(Enum):
    number = 1
    string = 2
    object = 3
    array = 4
    boolean = 5


class OpenAPIContentTypes(Enum):
    JSON = "application/json"
    FORM = "multipart/form-data"


class ParameterType(Enum):
    HEADERS = "header"
    QUERY = "query"
    PATH = "path"
