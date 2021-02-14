from django.shortcuts import render, redirect
from .models import Post, Like
from django.urls import reverse_lazy
from .forms import PostForm, CommentForm
from profiles.models import Profile
from django.views.generic import UpdateView, DeleteView
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

@login_required
def posts_comment_and_list_view(request):
    queryset = Post.objects.all()
    profile = Profile.objects.get(user=request.user)

    # intials
    post_form = PostForm()
    comment_form = CommentForm()
    post_add = False

    profile = Profile.objects.get(user=request.user)

    if "submit_post_form" in request.POST:
        post_form = PostForm(request.POST, request.FILES)
        if post_form.is_valid():
            instance = post_form.save(commit=False)
            instance.author = profile
            instance.save()
            profile_form = PostForm()
            post_add = True

    if "submit_comment_form" in request.POST:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            instance = comment_form.save(commit=False)
            instance.user = profile
            instance.post = Post.objects.get(id=request.POST.get("post_id"))
            instance.save()
            comment_form = CommentForm()

    context = {
        "queryset":queryset,
        "profile":profile,
        "post_form":post_form,
        "comment_form":comment_form,
        "post_add":post_add
    }

    return render(request, "posts/posts.html", context)

@login_required
def like_dislike_post(request):
    user = request.user
    if request.method == "POST":
        post_id = request.POST.get("post_id")
        post_obj = Post.objects.get(id=post_id)
        profile = Profile.objects.get(user=user)

        if profile in post_obj.likes.all():
            post_obj.likes.remove(profile)
        else:
            post_obj.likes.add(profile)
        
        like, created = Like.objects.get_or_create(user=profile, post_id=post_id)

        if not created:
            if like.value == "Like":
                like.value = "Dislike"
            else:
                like.value = "Like"
        else:
            like.value

            post_obj.save()
            like.save()
        
    data = {
        "value": like.value,
        "counter": post_obj.likes.all().count()
    }
    
    return JsonResponse(data, safe=False)

    return redirect("posts:post")

class PostDelete(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = "posts/post-delete.html"
    success_url = reverse_lazy("posts:post")

    def get_object(self, *args, **kwargs):
        pk = self.kwargs.get("pk")
        obj = Post.objects.get(pk=pk)
        if not obj.author.user == self.request.user:
            messages.warning(self.request, "You need to be the author to delete this post")
        return obj

class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "posts/post-update.html"
    success_url = reverse_lazy("posts:post")

    def form_valid(self, form):
        profile = Profile.objects.get(user=self.request.user)
        if form.instance.author == profile:
            return super().form_valid(form)
        else:
            form.add_error(None, "You need to be the author to update this post")
            return super().form_invalid(form)