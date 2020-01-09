from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Post
from .forms import PostForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import json

# Create your views here.


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date').reverse()
    return render(request, 'blog/post_list.html', {'posts': posts})
    
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            # post.published_date = timezone.now()      This is for saving drafts
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form':form})
    
@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            # post.published_date = timezone.now()      This is for saving drafts
            post.save()
            return redirect('post_detail', pk=post.pk)
    elif(request.user == post.author):
        form = PostForm(instance=post)
        return render(request, 'blog/post_edit.html', {'form': form})
    return redirect('post_detail', pk=post.pk)

@login_required
def post_draft_list(request):
    posts = Post.objects.filter(published_date__isnull=True).order_by('created_date')
    return render(request, 'blog/post_draft_list.html', {'posts': posts})

@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if (request.user == post.author):
        post.publish()
    return redirect('post_detail', pk=pk)

@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if (request.user == post.author):
        post.delete()
        return redirect('post_list')
    return redirect('post_detail', pk=pk)

@csrf_exempt
def new_user(request):
    if request.method == 'POST':
        # create new user, redirect to post_list page
        credentialsJSON = request.body.decode('utf-8')
        if(credentialsJSON != ''):
            credentialsObj = json.loads(credentialsJSON)
            #print('New User: ' + credentialsObj['username'])
            #print('New Pass: ' + credentialsObj['password'])
            newUser = User.objects.create_user(credentialsObj['username'], None, credentialsObj['password'])
            newUser.save()
        return redirect('post_list')
    else:
        return render(request, 'blog/new_user.html')