from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm
from django.contrib.auth import login
from django.contrib.auth.models import User
from .models import Follow
from django.contrib.auth.decorators import login_required
from django.contrib import messages



def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # сохраняем аватар и био
            user.profile.avatar = form.cleaned_data.get("avatar")
            user.profile.bio = form.cleaned_data.get("bio")
            user.profile.save()
            return redirect("login")
    else:
        form = CustomUserCreationForm()
    return render(request, "users/register.html", {"form": form})


@login_required
def profile(request, username=None):
    if username:
        user_obj = get_object_or_404(User, username=username)
    else:
        user_obj = request.user

    posts = user_obj.posts.all()

    is_following = False
    if request.user.is_authenticated and request.user != user_obj:
        is_following = request.user.following.filter(following=user_obj).exists()

    return render(request, "users/profile.html", {
        "profile_user": user_obj,
        "posts": posts,
        "is_following": is_following
    })



@login_required
def follow_user(request,username):
    user_to_follow = get_object_or_404(User, username=username)
    if user_to_follow == request.user:
        messages.error(request, "❌ Нельзя подписаться на самого себя.")
    else:
        Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
        messages.success(request, f"✅ Вы подписались на {user_to_follow.username}!")
    return redirect('user_profile', username=username)

@login_required
def unfollow_user(request, username):
    user_to_unfollow = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(follower=request.user, following=user_to_unfollow)
    if follow.exists():
        follow.delete()
        messages.success(request, f"❌ Вы отписались от {user_to_unfollow.username}.")
    return redirect("user_profile", username=username)
