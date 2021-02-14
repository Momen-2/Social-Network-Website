from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile, Relationship
from .forms import ProfileForm
from django.views.generic import ListView, DetailView
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

@login_required
def profile(request):
    profile = Profile.objects.get(user=request.user)
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)
    confirm = False

    if request.method == "POST":
        form.save()
        confirm = True

    context = {
        "profile":profile, 
        "form":form,
        "confirm":confirm,
    }
    
    return render(request, "profiles/profile.html", context)

@login_required
def invite_receive(request):
    profile = Profile.objects.get(user=request.user)
    queryset = Relationship.objects.invitations_receive(profile)
    results = list(map(lambda x: x.sender, queryset))
    is_empty = False

    if len(results) == 0:
        is_empty = True

    context = {
                "queryset":results, 
                "is_empty":is_empty
              }
    
    return render(request, "profiles/invites.html", context)

@login_required
def invite_profiles_list(request):
    user = request.user    
    queryset = Profile.objects.get_all_profiles(user)

    context = {"queryset":queryset}

    return render(request, "profiles/invite-list.html", context)

@login_required
def profiles_list(request):
    user = request.user    
    queryset = Profile.objects.get_all_profiles(user)

    context = {"queryset":queryset}

    return render(request, "profiles/profiles-list.html", context)

@login_required
def send_invitation(request):
    if request.method == "POST":
        pk = request.POST.get("profile_pk")
        user = request.user
        sender = Profile.objects.get(user=user)
        receiver = Profile.objects.get(pk=pk)
        relation = Relationship.objects.create(sender=sender, receiver=receiver, status="send")

        return redirect(request.META.get("HTTP_REFERER"))

    return redirect("profiles:my-profile")

@login_required
def remove_from_friends(request):
    if request.method == "POST":
        pk = request.POST.get("profile_pk")
        user = request.user
        sender = Profile.objects.get(user=user)
        receiver = Profile.objects.get(pk=pk)
        relation = Relationship.objects.get(
            (Q(sender=sender) & Q(receiver=receiver)) | (Q(sender=receiver) & Q(receiver=sender))
        )

        relation.delete()

        return redirect(request.META.get("HTTP_REFERER"))

    return redirect("profiles:my-profile")

@login_required
def accept_invitation(request):
    if request.method == "POST":
        pk = request.POST.get("profile_pk")
        sender = Profile.objects.get(pk=pk)
        receiver = Profile.objects.get(user=request.user)
        relationship = get_object_or_404(Relationship, sender=sender, receiver=receiver)

        if relationship.status == "send":
            relationship.status = "accepted"
            relationship.save()

    return redirect("profiles:invites")

@login_required
def reject_invitation(request):
    if request.method == "POST":
        pk = request.POST.get("profile_pk")
        sender = Profile.objects.get(pk=pk)
        receiver = Profile.objects.get(user=request.user)
        relationship = get_object_or_404(Relationship, sender=sender, receiver=receiver)
        relationship.delete()
    return redirect("profiles:invites")

class ProfilesDetail(LoginRequiredMixin, DetailView):
    model = profile
    template_name = "profiles/profiles-detail.html"

    def get_object(self, slug=None):
        slug = self.kwargs.get("slug")
        profile = Profile.objects.get(slug=slug)

        return profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(username__iexact=self.request.user)
        profile = Profile.objects.get(user=user)
        relationship_reciever = Relationship.objects.filter(sender=profile)
        relationship_sender = Relationship.objects.filter(receiver=profile)
        receivers = []
        senders = []

        for item in relationship_reciever:
            receivers.append(item.receiver.user)
            
        for item in relationship_sender:
            senders.append(item.sender.user)

        context["receivers"] = receivers
        context["senders"] = senders
        context['posts'] = self.get_object().get_all_authors_posts()
        # contxt['len_posts'] = True if len(self.get_object().get_all_authors_posts()) > 0 else False

        return context

class ProfilesList(LoginRequiredMixin, ListView):
    model = Profile
    template_name = "profiles/profiles-list.html"

    def get_queryset(self):
        queryset = Profile.objects.get_all_profiles(self.request.user)        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(username__iexact=self.request.user)
        profile = Profile.objects.get(user=user)
        relationship_reciever = Relationship.objects.filter(sender=profile)
        relationship_sender = Relationship.objects.filter(receiver=profile)
        receivers = []
        senders = []

        for item in relationship_reciever:
            receivers.append(item.receiver.user)
            
        for item in relationship_sender:
            senders.append(item.sender.user)

        context["receivers"] = receivers
        context["senders"] = senders
        context["is_empty"] = False

        if len(self.get_queryset()) == 0:
            context["is_empty"] = True

        return context