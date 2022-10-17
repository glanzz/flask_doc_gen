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


DEFAULT_GEN_FILE_NAME = "document.json"


class SCHEMA_KEYWORDS(Enum):
    PARAMETERS = "parameters"
    REQUEST_BODY = "requestBody"
    RESPONSES = "responses"


class CONFIG_KEYS(Enum):
    ACTIVE = "FLASK_DOC_GEN_ACTIVE"
    FILE = "FLASK_DOC_GEN_FILE"
    BLACKLISTED_HEADERS = "FLASK_DOC_GEN_BLACKLISTED_HEADERS"
    DESCRIPTIONS = "FLASK_DOC_GEN_ENDPOINT_DESCRIPTIONS"

CONTENT_TYPE_HEADER_NAME = "Content-Type"
REQUEST_BODY_UNALLOWED_METHODS = ["GET", "DELETE"]
