from django.urls import path
from . import views

urlpatterns = [
    path('sign-up/', views.sign_up, name='sign_up'),
    path('sign-in/', views.sign_in, name='sign_in'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('invite-member/', views.invite_member, name='invite_member'),
    path('delete-member/<int:org_id>/<int:user_id>/', views.delete_member, name='delete_member'),
    path('update-member-role/', views.update_member_role, name='update_member_role'),
    path('role-wise-user-count/', views.role_wise_user_count, name='role_wise_user_count'),
    path('organization-wise-member-count/', views.organization_wise_member_count, name='organization_wise_member_count'),
    path('organization-role-wise-user-count/', views.organization_role_wise_user_count, name='organization_role_wise_user_count'),
]
