from rest_framework.renderers import BaseRenderer


class XLSRenderer(BaseRenderer):
    media_type = "application/xls"
    format = "xls"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


class ODSRenderer(BaseRenderer):
    media_type = "application/vnd.oasis.opendocument.spreadsheet .ods"
    format = "ods"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data
