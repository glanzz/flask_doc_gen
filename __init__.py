import warnings
from json import dumps, load
from typing import Any
from .constants import DEFAULT_GEN_FILE_NAME, OpenAPIContentTypes, OpenAPIDataTypes, ParameterType
from flask import current_app


class _FlaskDocGenState:
    def __init__(self, generator) -> None:
        self.generator = generator


class DocGen:
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def _is_valid_json_file_name(cls, file_name):
        valid_file_name = True
        if not type(file_name) == str:
            valid_file_name = False
        elif file_name.endswith(".json"):
            valid_file_name = False
        return valid_file_name

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
        if not app.config.get("FLASK_DOC_GEN_FILE"):
            warnings.warn(
                "FlaskDocGen: No custom file name given initialized to "
                "document.json in app root folder."
                "Set FLASK_DOC_GEN_FILE='path/to/file'"
            )
        else:
            json_file_name = app.config["FLASK_DOC_GEN_FILE"]
            if not self._is_valid_json_file_name(json_file_name):
                app.config["FLASK_DOC_GEN_FILE"] = DEFAULT_GEN_FILE_NAME
                warnings.warn(
                    "Invalid file name given, "
                    "defaulting to document.json"
                )

        app.config.setdefault("FLASK_DOC_GEN_ACTIVE", False)
        app.config.setdefault("FLASK_DOC_GEN_FILE", DEFAULT_GEN_FILE_NAME)
        app.config.setdefault(
            "FLASK_DOC_GEN_BLACKLISTED_HEADERS", []
        )  # Not used currently
        app.config.setdefault(
            "FLASK_DOC_GEN_ENDPOINT_DESCRIPTIONS", []
        )  # Not used currently

        app.extensions["flask_doc_gen"] = _FlaskDocGenState(self)

    def generate(self, request, response):
        if not current_app.config.get("FLASK_DOC_GEN_ACTIVE"):
            return
        document_json = {}
        file_name = current_app.config["FLASK_DOC_GEN_FILE"]

        try:
            json_file = open(file_name, "r")
            document_json = load(json_file)
            json_file.close()
        except Exception as e:
            warnings.warn(f"Failed to read data {str(e)}")

        path_schema = document_json.get(request.path, {})
        path_schema = self.get_path_schema(
            request=request, response=response, current_schema=path_schema
        )
        document_json[request.path] = path_schema

        with open(file_name, "w") as json_file:
            json_file.writelines(dumps(document_json))

    def get_path_schema(self, request, response, current_schema={}):
        path_schema = current_schema if current_schema else {}
        request_method = request.method.lower()
        path_schema[request_method] = self.get_request_method_schema(
            current_schema=path_schema.get(request_method, {}),
            response=response,
            request=request,
        )

        return path_schema

    def get_request_method_schema(self, request, response, current_schema={}):
        SUCCESS_RESPONSE = response.status_code == 200
        parameters_schema = []
        request_body_schema = {}
        if SUCCESS_RESPONSE:
            parameters_schema = self.get_parameters(
                query_params=request.args,
                headers=request.headers,
                path_params=request.view_args,
                current_schema=current_schema.get("parameters", []),
            )
            request_body_schema = self.get_request_schema(
                request, current_schema=current_schema.get("requestBody", {})
            )

        request_method_schema = current_schema if current_schema else {}
        if parameters_schema:
            request_method_schema["parameters"] = parameters_schema
        if request_body_schema:
            request_method_schema["requestBody"] = request_body_schema

        request_method_schema["responses"] = self.get_response_schema(
            response, current_schema=current_schema.get("responses", {})
        )

        return request_method_schema

    def get_response_schema(self, response, current_schema={}):
        response_schema = current_schema if current_schema else {}
        content_type = response.content_type
        if content_type == OpenAPIContentTypes.JSON.value:
            response_data = response.json
        if content_type == OpenAPIContentTypes.FORM.value:
            response_data = response.form

        response_code = str(response.status_code)
        if response_code not in response_schema:
            response_schema[response_code] = {
                "description": "TBA",  # use from config when possible
                "content": {
                    (content_type): self.get_response_content(response_data)
                },
            }
        else:
            response_schema[response_code] = self._get_content_schema(
                content_type=content_type,
                data=response_data,
                current_schema=response_schema[response_code],
            )

        return response_schema

    def get_response_content(self, response_data) -> object:
        return {
            "description": "TBA",
            "schema": self._get_data_schema(response_data)
        }

    def get_request_schema(self, request, current_schema={}):
        request_schema = (
            current_schema
            if current_schema
            else {"description": "TBA", "required": True, "content": {}}
        )

        content_type = request.content_type
        if content_type == OpenAPIContentTypes.JSON.value:
            request_data = request.json
        if content_type == OpenAPIContentTypes.FORM.value:
            request_data = request.form

        request_schema = self._get_content_schema(
            current_schema=request_schema,
            content_type=content_type,
            data=request_data,
        )

        return request_schema

    def _get_content_schema(self, content_type, data, current_schema):
        schema = current_schema
        if content_type not in current_schema["content"].keys():
            schema["content"][content_type] = {
                "schema": self._get_data_schema(data)
            }
        else:
            content_type_schema = current_schema["content"][content_type]
            schema["content"][content_type] = {
                "schema": self._get_data_schema(
                    data, current_schema=content_type_schema["schema"]
                )
            }

        return schema

    def get_parameters(
        self,
        query_params={},
        headers={},
        path_params={},
        existing_params=[],
        current_schema=[],
    ):
        parameters = current_schema if current_schema else []
        existing_params = (
            [param_schema["name"] for param_schema in current_schema]
            if current_schema
            else []
        )
        for query_param in query_params:
            if query_param not in existing_params:
                parameters.append(
                    self._get_parameter_object(
                        required=(True if current_schema else False),
                        param_type=ParameterType.QUERY.value,
                        value=query_params[query_param],
                        name=query_param,
                    )
                )
        for header in headers:
            if header[0] not in existing_params:
                parameters.append(
                    self._get_parameter_object(
                        header[0], header[1], ParameterType.HEADERS.value
                    )
                )
        for path_param in path_params:
            if path_param not in existing_params:
                parameters.append(
                    self._get_parameter_object(
                        param_type=ParameterType.PATH.value,
                        value=path_params[path_param],
                        name=path_param,
                    )
                )
        return parameters

    def _get_parameter_object(self, name, value, param_type, required=None):
        param_object = {
            "name": name,
            "schema": self._get_data_schema(value),
            "in": param_type,
        }
        """if required is not None:
            param_object["required"] = required"""
        return param_object

    def _get_data_schema(self, value, current_schema=None):
        value_type = self._get_type(value)
        schema = {
            "type": value_type
        }  # "required": True if current_schema else False
        type_match = current_schema and current_schema["type"] == value_type

        if value_type == OpenAPIDataTypes.object.name:
            schema["properties"] = (
                current_schema["properties"] if type_match else {}
            )
            for object_key in value:
                schema["properties"][object_key] = self._get_data_schema(
                    value[object_key],
                    current_schema=schema["properties"].get(object_key),
                )
            return schema
        elif value_type == OpenAPIDataTypes.array.name:
            if len(value):
                schema["items"] = current_schema["items"] if type_match else {}
                schema["items"] = self._get_data_schema(
                    value[0], current_schema=current_schema.get("items")
                )

        return schema

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
