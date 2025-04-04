from core.loading import get_model
from core.validators import URLDoesNotExistValidator
from django import forms

FlatPage = get_model("flatpages", "FlatPage")


class PageSearchForm(forms.Form):
    """
    Search form to filter pages by *title.
    """

    title = forms.CharField(required=False, label="Заголовок страницы")


class PageUpdateForm(forms.ModelForm):
    """
    Update form to create/update flatpages. It provides a *title*, *url*,
    and *content* field. The specified URL will be validated and check if
    the same URL already exists in the system.
    """

    url = forms.RegexField(
        label="URL",
        max_length=100,
        regex=r"^[-\w/\.~]+$",
        required=False,
        help_text="Пример: '/about/contact/'.",
        error_messages={
            "invalid": (
                "Это значение должно содержать только буквы, цифры и точки,"
                "подчеркивание, тире, косая черта или тильда."
            ),
        },
    )

    def clean_url(self):
        """
        Validate the input for field *url* checking if the specified
        URL already exists. If it is an actual update and the URL has
        not been changed, validation will be skipped.

        Returns cleaned URL or raises an exception.
        """
        url = self.cleaned_data["url"]
        if "url" in self.changed_data:
            if not url.endswith("/"):
                url += "/"
            URLDoesNotExistValidator()(url)
        return url

    class Meta:
        model = FlatPage
        fields = ("title", "url", "content")
