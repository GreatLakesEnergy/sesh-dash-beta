# user permissions

# Guardian
from guardian.core import ObjectPermissionChecker
from guardian.shortcuts import get_objects_for_user
from guardian.shortcuts import get_perms

#models
from seshdash.models import Sesh_Site

def get_permissions(user):
    permission =  user.has_perm('view_Sesh_Site')
    return permission

