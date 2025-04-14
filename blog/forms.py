from django import forms
from .models import Blog, Tag
from ckeditor.widgets import CKEditorWidget

class BlogPostForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())
    class Meta:
        model = Blog
        fields = ['title', 'content', 'image', 'tags']
        widgets = {
            'tags': forms.SelectMultiple(attrs={'id': 'id_tags'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tags'].queryset = Tag.objects.all()
        if self.instance:
            self.fields['tags'].queryset = Tag.objects.filter(blog=self.instance)

        
