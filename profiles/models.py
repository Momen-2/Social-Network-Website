from django.db import models
from django.contrib.auth.models import User
from .utils import get_random_code
from django.template.defaultfilters import slugify
from django.db.models import Q
from django.shortcuts import reverse

class ProfileManager(models.Manager):
    def get_all_profiles_to_invite(self, sender):
        profiles = Profile.objects.all().exclude(user=sender)
        profile = Profile.objects.get(user=sender)
        queryset = Relationship.objects.filter(Q(sender=profile) | Q(receiver=profile))
        print(queryset)

        accepted = []
        for relation in queryset:
            if relation.status == "accepted":
                accepted.append(relation.receiver)
                accepted.append(relation.sender)
        print(accepted)
        available = [profile for profile in profiles if profile not in accepted]
        print(available)
        return available

    def get_all_profiles(self, me):
        profiles = Profile.objects.all().exclude(user=me)
        return profiles

class Profile(models.Model):
    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(default="no bio..", max_length=300)
    email = models.EmailField(max_length=200, blank=True)
    country = models.CharField(max_length=200, blank=True)
    avatar = models.ImageField(default="avatar.png", upload_to="avatars/")
    friends = models.ManyToManyField(User, blank=True, related_name="frinends")
    slug = models.SlugField(unique=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    objects = ProfileManager()

    def __str__(self):
        return f"{self.user.username}-{self.created.strftime('%d-%m-%Y')}"

    def get_absolute_url(self):
        return reverse("profiles:profiles-detail", kwargs={"slug": self.slug})
        
    def get_friends(self):
        return self.friends.all()
    
    def get_friends_number(self):
        return self.friends.all().count()
    
    def get_posts_number(self):
        return self.posts.all().count()
    
    def get_all_authors_posts(self):
        return self.posts.all
    
    def get_likes(self):
        likes = self.like_set.all()
        total_likes = 0

        for like in likes:
            if like.value=="Like":
                total_likes += 1
        return total_likes
    
    def get_likes_recieved_number(self):
        posts = self.posts.all()
        total_liked = 0
        for item in posts:
            total_liked += item.likes.all().count()
        return total_liked

    __initial_first_name = None
    __initial_last_name = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__initial_first_name = self.first_name
        self.__initial_last_name = self.last_name

    def save(self, *args, **kwargs):
        ex = False
        to_slug = self.slug
        if self.first_name != self.__initial_first_name or self.last_name != self.__initial_last_name or self.slug=="":
            if self.first_name and self.last_name:
                to_slug = slugify(str(self.first_name) + " " + str(self.last_name))
                ex = Profile.objects.filter(slug=to_slug).exists()
                while ex:
                    to_slug = slugify(to_slug + " " + str(get_random_code()))
                    ex = Profile.objects.filter(slug=to_slug).exists()
            else:
                to_slug = str(self.user)
        self.slug = to_slug
        super().save(*args, **kwargs)

STATUS_CHOICES = (
    ("send", "send"),
    ("accepted", "accepted")
)

class RelationshipManager(models.Manager):
    def invitations_receive(self, receiver):
        queryset = Relationship.objects.filter(receiver=receiver, status="send")
        return queryset

class Relationship(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="sender")   
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="receiver")   
    status = models.CharField(max_length=8, choices=STATUS_CHOICES)
    updated = models.DateTimeField(auto_now_add=True)
    created = models.DateTimeField(auto_now_add=True)
    objects = RelationshipManager()

    def __str__(self):
        return f"{self.sender}-{self.receiver}-{self.status}"
