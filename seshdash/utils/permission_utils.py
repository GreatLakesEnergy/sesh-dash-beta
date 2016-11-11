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

def get_org_edit_permissions(user):
    """
    Permissions for editing the sesh organisation
    """
    return user.is_org_admin
