from apps.webshop.user.utils import normalise_email
from core.loading import get_model
from django import forms
from django.template import Template, TemplateSyntaxError

Order = get_model("order", "Order")
CommunicationEventType = get_model("communication", "CommunicationEventType")


class CommunicationEventTypeForm(forms.ModelForm):
    email_subject_template = forms.CharField(label="Шаблон темы письма")
    email_body_template = forms.CharField(
        label="Шаблон основного текста электронного письма",
        required=True,
        widget=forms.widgets.Textarea(attrs={"class": "plain"}),
    )
    email_body_html_template = forms.CharField(
        label="HTML-шаблон тела письма", required=True, widget=forms.Textarea
    )

    preview_order_number = forms.CharField(label="Номер заказа", required=False)
    preview_email = forms.EmailField(
        label="Предварительный просмотр письма", required=False
    )

    # pylint: disable=attribute-defined-outside-init
    def __init__(self, *args, data=None, **kwargs):
        self.show_preview = False
        self.send_preview = False
        if data:
            self.show_preview = "show_preview" in data
            self.send_preview = "send_preview" in data
        super().__init__(data, *args, **kwargs)

    def validate_template(self, value):
        try:
            Template(value)
        except TemplateSyntaxError as e:
            raise forms.ValidationError(str(e))

    def clean_email_subject_template(self):
        subject = self.cleaned_data["email_subject_template"]
        self.validate_template(subject)
        return subject

    def clean_email_body_template(self):
        body = self.cleaned_data["email_body_template"]
        self.validate_template(body)
        return body

    def clean_email_body_html_template(self):
        body = self.cleaned_data["email_body_html_template"]
        self.validate_template(body)
        return body

    def clean_preview_order_number(self):
        number = self.cleaned_data["preview_order_number"].strip()
        if not self.instance.is_order_related():
            return number
        if not self.show_preview and not self.send_preview:
            return number
        try:
            self.preview_order = Order.objects.get(number=number)
        except Order.DoesNotExist:
            raise forms.ValidationError("Заказ с этим номером не найден")
        return number

    def clean_preview_email(self):
        email = normalise_email(self.cleaned_data["preview_email"])
        if not self.send_preview:
            return email
        if not email:
            raise forms.ValidationError("Пожалуйста введите адрес электронной почты")
        return email

    def get_preview_context(self):
        ctx = {}
        if hasattr(self, "preview_order"):
            ctx["order"] = self.preview_order
        return ctx

    class Meta:
        model = CommunicationEventType
        fields = (
            "name",
            "email_subject_template",
            "email_body_template",
            "email_body_html_template",
            "preview_order_number",
            "preview_email",
        )
