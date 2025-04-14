from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Blog,NewsletterSubscriber
from .serializers import BlogPostSerializer
from rest_framework.decorators import api_view, permission_classes

@api_view(['GET'])
def blog_list(request):
    queryset = Blog.objects.filter(isApproved=True)
    serializer = BlogPostSerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def blog_detail(request, pk):
    try:
        blog = Blog.objects.get(pk=pk,isApproved=True)
        serializer = BlogPostSerializer(blog)
        return Response(serializer.data)
    except Blog.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_blog(request):
    serializer = BlogPostSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_blog(request, pk):
    try:
        blog = Blog.objects.get(pk=pk)
        if blog.author != request.user:
            return Response({"error": "You are not allowed to edit this blog!"}, status=status.HTTP_403_FORBIDDEN)
        serializer = BlogPostSerializer(blog, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Blog.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_blog(request, pk):
    try:
        blog = Blog.objects.get(pk=pk)
        if blog.author != request.user:
            return Response({"error": "You are not allowed to delete this blog!"}, status=status.HTTP_403_FORBIDDEN)
        blog.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Blog.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def subscribe_newsletter(request):
    email=request.data.get('email')
    if not email:
        return Response({'success':False,'message':'Email is required','data':None},status=status.HTTP_400_BAD_REQUEST)
    else:
        try:
            NewsletterSubscriber.objects.get(email=email)
            return Response({'success':False,'message':'Email already subscribed','data':None},status=status.HTTP_400_BAD_REQUEST)
        except NewsletterSubscriber.DoesNotExist:
            NewsletterSubscriber.objects.create(email=email)
            return Response({'success':True,'message':'Subscribed successfully','data':email},status=status.HTTP_200_OK)