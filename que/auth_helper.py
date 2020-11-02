import os
from datetime import datetime

from django.conf import settings
from django.urls import reverse
from requests_oauthlib import OAuth2Session

from .models import AuthorizedTeamsUser

# This is necessary for testing with non-HTTPS localhost
# Remove this if deploying to production
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# This is necessary because Azure does not guarantee
# to return scopes in the same case and order as requested
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"
os.environ["OAUTHLIB_IGNORE_SCOPE_CHANGE"] = "1"

authorize_url = "https://login.microsoftonline.com/{}/oauth2/v2.0/authorize".format(
    settings.MS_TEAMS_TENANT_ID
)
token_url = "https://login.microsoftonline.com/{}/oauth2/v2.0/token".format(
    settings.MS_TEAMS_TENANT_ID
)


def get_callback_url(request):
    if request.get_host().startswith("localhost"):
        return "http://" + request.get_host() + reverse("callback")

    return "https://" + request.get_host() + reverse("callback")


def get_sign_in_url(request):
    aad_auth = OAuth2Session(
        settings.MS_TEAMS_APP_ID,
        scope=settings.MS_TEAMS_SCOPES,
        redirect_uri=get_callback_url(request),
    )

    sign_in_url, state = aad_auth.authorization_url(authorize_url, prompt="login")
    return sign_in_url, state


def get_token_from_code(request, expected_state):
    aad_auth = OAuth2Session(
        settings.MS_TEAMS_APP_ID,
        state=expected_state,
        scope=settings.MS_TEAMS_SCOPES,
        redirect_uri=get_callback_url(request),
    )
    token = aad_auth.fetch_token(
        token_url,
        client_secret=settings.MS_TEAMS_APP_SECRET,
        authorization_response=request.get_full_path(),
    )

    return token


def get_user(token):
    graph_client = OAuth2Session(token=token)
    user = graph_client.get("https://graph.microsoft.com/v1.0/me")
    return user.json()


def get_token(request, token):
    if token != None:
        now = datetime.now()
        # Subtract 5 minutes from expiration to account for clock skew
        expire_time = token["expires_at"] - 300
        if now >= expire_time:
            aad_auth = OAuth2Session(
                settings.MS_TEAMS_APP_ID,
                token=token,
                scope=settings.MS_TEAMS_SCOPES,
                redirect_uri=get_callback_url(request),
            )

            refresh_params = {
                "client_id": settings.MS_TEAMS_APP_ID,
                "client_secret": settings.MS_TEAMS_APP_SECRET,
            }
            new_token = aad_auth.refresh_token(token_url, **refresh_params)

            AuthorizedTeamsUser.objects.get(token=token).update(token=new_token)
            return new_token

        else:
            return token
