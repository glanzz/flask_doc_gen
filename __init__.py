import warnings
from json import dumps, load
from typing import Any
from .constants import OpenAPIContentTypes, OpenAPIDataTypes, ParameterType
from flask import current_app


class _FlaskDocGenState:
    def __init__(self, generator) -> None:
        self.generator = generator


class DocGen:
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        if (
            "FLASK_DOC_GEN_ACTIVE" not in app.config
            or not app.config["FLASK_DOC_GEN_ACTIVE"]
        ):
            warnings.warn(
                "FlaskDocGen is initialized but it is not active,"
                "defaulting to false"
                "Set FLASK_DOC_GEN_ACTIVE=True to activate"
            )

        app.config.setdefault("FLASK_DOC_GEN_ACTIVE", False)
        app.config.setdefault(
            "FLASK_DOC_GEN_BLACKLISTED_HEADERS", []
        )  # Not used currently
        app.config.setdefault(
            "FLASK_DOC_GEN_ENDPOINT_DESCRIPTIONS", []
        )  # Not used currently

        app.extensions["flask_doc_gen"] = _FlaskDocGenState(self)

    def get_response_schema(self, response):
        response_data = {}
        content_type = response.content_type
        if content_type == OpenAPIContentTypes.JSON.value:
            response_data = response.json
        if content_type == OpenAPIContentTypes.FORM.value:
            response_data = response.form
        return {
            (response.status_code): {
                "description": "TBA",  # use from config when possible
                "content": {(content_type): self.get_response_content(response_data)},
            }
        }

    def get_request_schema(self, request):
        request_data = {}
        content_type = request.content_type
        if content_type == OpenAPIContentTypes.JSON.value:
            request_data = request.json
        if content_type == OpenAPIContentTypes.FORM.value:
            request_data = request.form
        return {
            "description": "TBA",
            "required": True,
            "content": {
                (content_type): {"schema": self._get_data_schema(request_data)}
            },
        }

    def get_response_content(self, response_data) -> object:
        return {
            "description": "TBA",
            "schema": self._get_data_schema(response_data)
        }

    def _get_data_schema(self, value):
        value_type = self._get_type(value)
        schema = {"type": value_type}
        if value_type == OpenAPIDataTypes.object.name:
            schema["properties"] = {}
            for object_key in value:
                schema["properties"][object_key] = self._get_data_schema(
                    value[object_key]
                )
            return schema
        elif value_type == "array":
            if value:  # Add items only if not an empty array
                schema["items"] = self._get_data_schema(value[0])

        return schema

    def _get_parameter_object(self, name, value, param_type):
        return {
            "schema": self._get_data_schema(value),
            "in": param_type,
            "name": name
        }

    def get_parameters(self, query_params={}, headers={}, path_params={}):
        parameters = []
        for query_param in query_params:
            parameters.append(
                self._get_parameter_object(
                    query_param,
                    query_params[query_param],
                    ParameterType.QUERY.value
                )
            )
        for header in headers:
            parameters.append(
                self._get_parameter_object(
                    header[0],
                    header[1],
                    ParameterType.HEADERS.value
                )
            )
        for path_param in path_params:
            parameters.append(
                self._get_parameter_object(
                    path_param,
                    path_params[path_param],
                    ParameterType.PATH.value
                )
            )
        return parameters

    def _get_type(self, data: Any) -> str:
        data_type = type(data)
        if data_type == int or data_type == float:
            return OpenAPIDataTypes.number.name
        if data_type == str:
            return OpenAPIDataTypes.string.name
        if data_type == dict:
            return OpenAPIDataTypes.object.name
        if data_type == list:
            return OpenAPIDataTypes.array.name
        if data_type == bool:
            return OpenAPIDataTypes.boolean.name
        return ""

    def generate(self, request, response):
        if not current_app.config.get("FLASK_DOC_GEN_ACTIVE"):
            return
        document_json = {}

        try:
            json_file = open("document.json", "r")
            document_json = load(json_file)
            json_file.close()
        except Exception as e:
            warnings.warn(f"Failed to read data {str(e)}")

        path_schema = document_json.get(request.path)
        if path_schema:
            warnings.warn(f"Path schema found for {request.path}")
            request_method = request.method.lower()
            if path_schema.get(request_method):
                # Handle intelli param and response type manipulation
                warnings.warn(f"Request method found for {request_method}")
                warnings.warn("Nothing to update")
            else:
                warnings.warn(f"generating new request data for {request_method}")
                path_schema[request_method] = self.get_request_method_schema(
                    request, response
                )
        else:
            warnings.warn(f"Generating new path data for {request.path}")
            path_schema = self.get_path_schema(request, response)

        # Redefine path schema
        document_json[request.path] = path_schema

        with open("document.json", "w") as json_file:
            json_file.writelines(dumps(document_json))

    def get_path_schema(self, request, response):
        path_schema = {}
        request_method = request.method.lower()
        path_schema[request_method] = self.get_request_method_schema(
            request, response
        )
        return path_schema

    def get_request_method_schema(self, request, response):
        return {
            "parameters": self.get_parameters(
                query_params=request.args,
                headers=request.headers,
                path_params=request.view_args,
            ),  # add params optionally if it is there, also try sending the resposne code so that we can determine if the params should be added to doc
            "requestBody": self.get_request_schema(request),
            "responses": self.get_response_schema(response),
        }
