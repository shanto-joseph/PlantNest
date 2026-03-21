from django import forms
from .models import Comment, BlogPost, VideoPost

class VideoPostForm(forms.ModelForm):
    class Meta:
        model = VideoPost
        fields = ['title', 'description', 'video_url', 'thumbnail']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter an engaging title for your video'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Describe what viewers will learn from your video'
            }),
            'video_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://youtube.com/watch?v=... or https://vimeo.com/...'
            }),
            'thumbnail': forms.FileInput(attrs={
                'class': 'form-control-file',
                'accept': 'image/*'
            }),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your comment here...'})
        }

class CustomerBlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'category', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter an engaging title for your blog post'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 12,
                'placeholder': 'Share your gardening story, tips, or experiences...'
            }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter categories for customer submissions
        self.fields['category'].choices = [
            ('tips', 'Gardening Tips'),
            ('diy', 'DIY Projects'),
            ('sustainability', 'Sustainability'),
            ('plant_care', 'Plant Care'),
            ('community', 'Community Stories'),
            ('experience', 'My Experience'),
        ]
        
        # Add help text
        self.fields['content'].help_text = "Share your gardening knowledge, experiences, or tips. Use clear headings and detailed explanations."