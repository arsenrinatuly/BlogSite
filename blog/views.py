from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Comment, Like, Tag
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator


# Create your views here.
def post_search(request):
    query = request.GET.get("q")
    posts = Post.objects.all()
    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(tags__name__icontains=query) 
        ).distinct()
    return render(request, "blog/post_list.html", {"posts" : posts, "query" : query})




def post_by_tag(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)
    posts = tag.posts.all()
    return render(request, "blog/post_list.html", {"posts" : posts, "tag" : tag})

def post_list(request):
    posts = Post.objects.all().order_by("-created_at")
    paginator = Paginator(posts, 6) 
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "blog/post_list.html",
        {
            "posts": page_obj.object_list,  
            "page_obj": page_obj,          
            "is_paginated": page_obj.has_other_pages(),  
        },
    )


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all().order_by("-created_at")
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Нужно войти чтобы комментировать")
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            messages.success(request, "💬 Комментарий добавлен!")
            return redirect("post_detail", pk=pk)
    else:
        form = CommentForm()
    return render(request, 'blog/post_detail.html', {
        'post': post,
        "comments": comments,
        "form" : form,
        "liked" : post.likes.filter(user=request.user).exists() if request.user.is_authenticated else False 
        })

@login_required
def toggle_like(request,pk):
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({"liked": liked, "total_likes" : post.total_likes})

@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            messages.success(request, "✅ Пост успешно создан!")
            return redirect('post_list')
        else:
            return render(request, 'blog/post_form.html', {'form': form})
    else:
        form = PostForm()
        return render(request, 'blog/post_form.html', {'form' : form})
    
@login_required
def post_update(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return HttpResponseForbidden("⛔ У вас нет прав редактировать этот пост.")
    
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "✏️ Пост успешно обновлён!")
            return redirect("post_list")
    else:
        form = PostForm(instance=post)
    return render(request, "blog/post_form.html", {"form": form})



def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return HttpResponseForbidden("⛔ У вас нет прав удалять этот пост.")
    post.delete()
    messages.success(request, "🗑️ Пост успешно удалён!")
    return redirect("post_list")

@login_required
def feed(request):
    following_users = request.user.following.values_list("following", flat=True)
    posts= Post.objects.filter(author__in=following_users).order_by("-created_at")
    return render(request, "blog/feed.html", {"posts": posts})

