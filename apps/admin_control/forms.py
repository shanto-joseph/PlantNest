from django import forms
from apps.product_management.models import Product, Category
from apps.customer_interaction.models import BlogPost
from apps.order_payment.models import Order

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'category', 'price',
            'stock_quantity', 'image', 'is_eco_friendly', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter product name',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Enter product description',
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Enter price'
            }),
            'stock_quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Enter stock quantity'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control-file',
                'accept': 'image/*'
            }),
            'is_eco_friendly': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default values
        self.fields['is_active'].initial = True
        # Remove blank option from category dropdown
        self.fields['category'].empty_label = None
        # Exclude 'Other' category
        self.fields['category'].queryset = Category.objects.exclude(name__iexact='Other')
        # Add help text
        self.fields['name'].help_text = "Enter a clear, descriptive product name"
        self.fields['description'].help_text = "Provide detailed product information and benefits"
        self.fields['price'].help_text = "Enter the product price"
        self.fields['stock_quantity'].help_text = "Current available inventory count"
        self.fields['image'].help_text = "Upload high-quality images (PNG, JPG up to 5MB)"

    @property
    def category_images(self):
        return {cat.pk: cat.image.url if cat.image else '' for cat in Category.objects.exclude(name__iexact='Other')}

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter category description'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control-file',
                'accept': 'image/*'
            }),
        }

class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'slug', 'category', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter blog post title'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL slug (auto-generated from title)'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 12,
                'placeholder': 'Write your blog post content here...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = None
        
        # Add help text
        self.fields['title'].help_text = "Enter a compelling title for your blog post"
        self.fields['slug'].help_text = "URL-friendly version of the title (auto-generated)"
        self.fields['content'].help_text = "Write your blog post content using markdown or HTML"

class OrderStatusUpdateForm(forms.Form):
    status = forms.ChoiceField(choices=Order.ORDER_STATUS)