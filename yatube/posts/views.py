from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User

NUMBER_POSTS: int = 10


def paginator_func(posts, request):
    paginator = Paginator(posts, NUMBER_POSTS)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def index(request):
    posts = Post.objects.all()
    page_obj = paginator_func(posts, request)
    context = {
        "page_obj": page_obj,
    }

    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = paginator_func(posts, request)
    context = {
        "group": group,
        "page_obj": page_obj,
    }

    return render(request, "posts/group_list.html", context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_obj = paginator_func(posts, request)
    context = {
        "author": author,
        "page_obj": page_obj,
        "posts_count": author.posts.count(),
    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    context = {
        "post": post,
        "author": post.author,
        "posts_count": post.author.posts.count(),
    }
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if not form.is_valid():
        return render(
            request,
            "posts/create_post.html",
            {"form": form},
        )
    new_post = form.save(commit=False)
    new_post.author = request.user
    new_post.save()
    return redirect("posts:profile", request.user)


@login_required
def post_edit(request, post_id, template="posts/create_post.html"):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST, instance=post)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("posts:post_detail", post_id=post_id)
    form = PostForm(instance=post)
    return render(request, template, {"post": post, "form": form, "is_edit": True})
