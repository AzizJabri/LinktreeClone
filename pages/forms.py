from django import forms
from .models import Page, Link, PageDecorator, LinkDecorator


class PageForm(forms.ModelForm):
    title = forms.CharField(max_length=255, min_length=4, required=True, widget=forms.TextInput(attrs={'placeholder': 'Title',
                                                                                                       'class': 'form-control',
                                                                                                       }))
    slug = forms.CharField(max_length=255, min_length=3, required=True, widget=forms.TextInput(attrs={'placeholder': 'Slug',
                                                                                                      'class': 'form-control',
                                                                                                      }))

    def clean(self):
        unwanted_names = ['create', 'update', 'delete', 'detail', 'index', 'page', 'page_detail', 'page_create',
                          'page_update', 'page_delete', 'link', 'link_create', 'link_update', 'link_delete', 'dashboard', "dashbord"]
        cleaned_data = super().clean()
        slug = cleaned_data.get('slug')
        if slug in unwanted_names:
            self.add_error('slug', 'This slug is not allowed')
            raise forms.ValidationError('This slug is not allowed')

        return cleaned_data

    class Meta:
        model = Page
        fields = ['title', 'slug']


class LinkForm(forms.ModelForm):
    name = forms.CharField(max_length=255, min_length=4, required=True, widget=forms.TextInput(attrs={'placeholder': 'Name',
                                                                                                      'class': 'form-control',
                                                                                                      }))
    url = forms.URLField(max_length=255, min_length=3, required=True, widget=forms.URLInput(attrs={'placeholder': 'URL',
                                                                                                   'class': 'form-control',
                                                                                                   }))

    class Meta:
        model = Link
        fields = ['name', 'url']
        widgets = {
            'page': forms.HiddenInput(),
        }
