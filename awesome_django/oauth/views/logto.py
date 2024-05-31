import json

from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.core.cache import cache
from django.http.response import HttpResponse
from django.shortcuts import redirect
from logto import LogtoClient
from logto import LogtoConfig
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet

User = get_user_model()

client = LogtoClient(
    LogtoConfig(
        endpoint="http://localhost:3001",
        appId="388wkuv2qgzfcw6jfk9pg",
        appSecret="lVpx5eHDXtgiAMzpnEhyPsP6oDR8IBAI",
    ),
    storage=cache,
)


class LogtoView(ViewSet):
    permission_classes = ()

    @action(detail=False, url_path="sign-in")
    def sign_in(self, request, *args, **kwargs):
        sync_func = async_to_sync(client.signIn)
        sign_in_url = sync_func(
            redirectUri="http://127.0.0.1:8000/oauth/logto/callback/",
            interactionMode="signIn",  # Show the sign-up page on the first screen
        )
        return redirect(sign_in_url)

    @action(detail=False)
    def callback(self, request, *args, **kwargs):
        sync_func = async_to_sync(client.handleSignInCallback)
        try:
            sync_func(request.build_absolute_uri())  # Handle a lot of stuff
        except Exception as e:  # noqa
            # Change this to your error handling logic
            return HttpResponse("Error: " + str(e))

        get_user_info = async_to_sync(client.fetchUserInfo)
        # result = {
        #     "client": json.loads(client.getIdTokenClaims().model_dump_json(exclude_unset=True)),
        #     "user": json.loads((get_user_info()).model_dump_json(exclude_unset=True))
        # }
        user_info = json.loads((get_user_info()).model_dump_json(exclude_unset=True))
        user, _ = User.objects.get_or_create(username=user_info["username"])
        if user.name != user_info["name"]:
            user.name = user_info["name"]
            user.save()

        login(request, user)

        return redirect(
            "/",
        )  # Redirect the user to the home page after a successful sign-in

    @action(detail=False)
    def home(self, request, *args, **kwargs):
        if client.isAuthenticated() is False:
            return "Not authenticated <a href='/sign-in'>Sign in</a>"

        get_user_info = async_to_sync(client.fetchUserInfo)
        return HttpResponse(
            # Get local ID token claims
            client.getIdTokenClaims().model_dump_json(exclude_unset=True)
            + "<br>"
            # Fetch user info from Logto userinfo endpoint
            + get_user_info().model_dump_json(exclude_unset=True)
            + "<br><a href='/sign-out'>Sign out</a>",
        )
