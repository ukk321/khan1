from rest_framework import serializers
from blog.models import Blog,Tag,NewsletterSubscriber

class BlogPostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    tags = serializers.SlugRelatedField(
        queryset=Tag.objects.all(),
        slug_field='name',
        many=True
    )
    
    class Meta:
        model = Blog
        fields = ['id','author','title','content','tags','image','date_posted']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class NewsLetterSerializer(serializers.ModelSerializer):
    class Meta:
        model=NewsletterSubscriber
        fields = '__all__'