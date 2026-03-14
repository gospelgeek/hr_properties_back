import os
import posixpath
import re

from django.conf import settings
from django.http import FileResponse, Http404
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

PUBLIC_PROPERTY_FOLDERS = {"images", "media", "ensers"}
PROPERTY_FOLDER_PATTERN = re.compile(r"^property_\d+$")


def _is_admin_user(user) -> bool:
    if not user or not user.is_authenticated:
        return False

    # Allow Django superusers and users with app role "admin".
    if getattr(user, "is_superuser", False):
        return True

    user_roles = user.userrole_set.values_list("role__name", flat=True)
    return "admin" in user_roles


def _normalize_media_path(path: str) -> str:
    """Normalize and validate media path to avoid traversal attacks."""
    normalized = posixpath.normpath(path).lstrip("/")

    # Block traversal patterns like ../x or absolute-style paths.
    if normalized == ".." or normalized.startswith("../"):
        raise Http404("Invalid media path")

    return normalized


def _is_public_media_path(media_path: str) -> bool:
    """Public files are only under property_X/images|media|ensers."""
    parts = media_path.split("/")
    if len(parts) < 2:
        return False

    property_folder, category = parts[0], parts[1]
    return bool(PROPERTY_FOLDER_PATTERN.match(property_folder)) and category in PUBLIC_PROPERTY_FOLDERS


def _build_safe_file_path(media_path: str) -> str:
    media_root = os.path.abspath(settings.MEDIA_ROOT)
    full_path = os.path.abspath(os.path.join(media_root, media_path))

    # Ensure the final path remains inside MEDIA_ROOT.
    if full_path != media_root and not full_path.startswith(media_root + os.sep):
        raise Http404("Invalid media path")

    return full_path


@api_view(["GET"])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([AllowAny])
def protected_media(request, path: str):
    normalized_path = _normalize_media_path(path)

    if not _is_public_media_path(normalized_path):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided for this media file."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not _is_admin_user(request.user):
            return Response(
                {"detail": "You do not have permission to access this private media file."},
                status=status.HTTP_403_FORBIDDEN,
            )

    file_path = _build_safe_file_path(normalized_path)

    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise Http404("Media file not found")

    return FileResponse(open(file_path, "rb"))
