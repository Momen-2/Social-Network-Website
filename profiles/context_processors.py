from .models import Profile, Relationship

def profile_picture(request):
    if request.user.is_authenticated:
        profile_obj = Profile.objects.get(user=request.user)
        avatar = profile_obj.avatar
        return {'avatar':avatar}
    return {}

def invatations_received_number(request):
    if request.user.is_authenticated:
        profile_obj = Profile.objects.get(user=request.user)
        queryset_count = Relationship.objects.invitations_receive(profile_obj).count()
        return {'invites_number':queryset_count}
    return {}