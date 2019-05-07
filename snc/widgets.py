from django import forms
from django.forms.utils import flatatt
from django.utils.safestring import mark_safe


class FileUploadWidget(forms.FileInput):
    def render(self, name, value, attrs=None):
        super().render(name, value, attrs)
        footer_class = ''

        if value is None or not value.name:
            footer_class = 'd-none'
            html = '''
            <div class="card card-input-file">
                <div class="card-header card-header-warning card-header-icon">
                    <div id="drag-space-%(name)s"
                         data-target="%(id)s"
                         class="upload-icon"
                         data-toggle="tooltip"
                         data-placement="top" title=""
                         rel="tooltip"
                         data-original-title="Clique ou Arraste">
                        <i class="material-icons" data-target="%(id)s">cloud_upload</i>
                    </div>
                    <p class="file-label-name" id="label-%(name)s">%(label)s</p>
                    <h6 class="file-name" id="file-name-%(name)s">
                        Clique ou arraste para upload.
                    </h6>
                </div>
                <div id="footer-%(name)s" class="%(footer_class)s card-footer">
                </div>
                <input type="%(input_type)s" id="%(id)s" name="%(name)s" />
            </div>
            ''' % {
                'label': self.attrs.get('label'),
                'id': attrs['id'],
                'name': name,
                'input_type': self.input_type,
                'footer_class': footer_class
            }
            return mark_safe(html)

        if hasattr(value, 'url'):
            file_url = value.url
            file_name = value.name
        else:
            footer_class = 'd-none'
            file_url = '#'
            file_name = value.name

        html = '''
            <div class="card card-input-file">
                <div class="card-header card-header-warning card-header-icon">
                    <div id="drag-space-%(name)s"
                         data-target="%(id)s"
                         class="upload-icon"
                         data-toggle="tooltip"
                         data-placement="top" title=""
                         rel="tooltip"
                         data-original-title="Clique ou Arraste">
                        <i class="material-icons" data-target="%(id)s">cloud_upload</i>
                    </div>
                    <p class="file-label-name" id="label-%(name)s">%(label)s</p>
                    <h6 class="file-name" id="file-name-%(name)s">
                        %(file_name)s
                    </h6>
                </div>
                <div id="footer-%(name)s" class="%(footer_class)s card-footer">
                    <div class="stats">
                    <i class="material-icons">save_alt</i>
                    <a id="url-%(name)s" href="%(file_url)s" >Download</a>
                    </div>
                </div>
                <input type="%(input_type)s" id="%(id)s" name="%(name)s" />
            </div>
        ''' % {
            'label': self.attrs.get('label'),
            'id': attrs['id'],
            'name': name,
            'file_name': file_name,
            'file_url': file_url,
            'input_type': self.input_type,
            'footer_class': footer_class
        }
        return mark_safe(html)
