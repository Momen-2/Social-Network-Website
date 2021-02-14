from django.urls import path
from .views import (
    profile, 
    invite_receive, 
    profiles_list,
    send_invitation, 
    invite_profiles_list,
    remove_from_friends,
    accept_invitation,
    reject_invitation,
    ProfilesList,
    ProfilesDetail
    )

app_name = "profiles"
urlpatterns = [
    path("", ProfilesList.as_view(), name="all-profiles"),
    path("my-profile/", profile, name="my-profile"),
    path("invites/", invite_receive, name="invites"),
    path("invites-list/", invite_profiles_list, name="invite-list"),
    path("send-invitation/", send_invitation, name="send-invite"),
    path("remove-friend/", remove_from_friends, name="remove-friend"),
    path("<slug>/", ProfilesDetail.as_view(), name="profiles-detail"),
    path("invites/accept/", accept_invitation, name="accept-invite"),
    path("invites/reject/", reject_invitation, name="reject-invite"),
]
