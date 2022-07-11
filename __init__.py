from typing import Any
from .constants import OpenAPIContentTypes, OpenAPIDataTypes


class DocGen:
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
                "content": {
                    (content_type): self.get_response_content(response_data)
                },
            }
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
