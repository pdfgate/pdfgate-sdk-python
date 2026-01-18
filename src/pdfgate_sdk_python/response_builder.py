from typing import Optional, Union, cast

import httpx

from pdfgate_sdk_python.dict_keys_converter import convert_camel_keys_to_snake
from pdfgate_sdk_python.responses import PDFGateDocument


class ResponseBuilder:

    @staticmethod
    def build_response(response: httpx.Response, json: Optional[bool] = False) -> Union[bytes, PDFGateDocument]:
        if json:
            json_response = response.json()
            return cast(PDFGateDocument, convert_camel_keys_to_snake(json_response))

        return response.content