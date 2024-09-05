from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, RegisterSerializer, OrganizationSerializer, MemberSerializer, RoleSerializer
from .models import Organization, Member, Role
from django.db.models import Count


User = get_user_model()

def generate_invite_link(user_id, org_id):
    return f"http://example.com/invite/{user_id}/{org_id}"

def send_invite_email(email, invite_link):
    subject = "You're Invited!"
    message = f"Click the following link to join the organization: {invite_link}"
    send_mail(subject, message, 'noreply@example.com', [email])

def send_password_update_alert(email):
    subject = "Password Updated Successfully"
    message = "Your password has been updated successfully."
    send_mail(subject, message, 'noreply@example.com', [email])

def send_login_alert_event(email):
    subject = "New Login Alert"
    message = "A new login to your account was detected."
    send_mail(subject, message, 'noreply@example.com', [email])

@api_view(['POST'])
def sign_up(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # Return serialized user data on successful registration
        user_data = UserSerializer(user).data
        
        organization_data = request.data.get('organization')
        if organization_data:
            org_serializer = OrganizationSerializer(data=organization_data)
            if org_serializer.is_valid():
                organization = org_serializer.save()
                role, created = Role.objects.get_or_create(name='Owner', org=organization)
                Member.objects.create(org=organization, user=user, role=role, status=0)
                
                # Generate and send invite link
                invite_link = generate_invite_link(user.id, organization.id)
                send_invite_email(user.email, invite_link)
                
                return Response({
                    "message": "User and organization registered successfully",
                    "user": user_data
                }, status=201)
            return Response(org_serializer.errors, status=400)
        
        return Response({
            "message": "User registered successfully",
            "user": user_data
        }, status=201)
    return Response(serializer.errors, status=400)

@api_view(['POST'])
def sign_in(request):
    email = request.data.get('email')
    password = request.data.get('password')
    print(password)
    print(email)
    user = get_object_or_404(User, email=email)

    print(user)
    print(password)
    print(email)
    print(user.password)
    
    if check_password(password, user.password):
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Send login alert event
        send_login_alert_event(user.email)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data  # Include user data in response
        }, status=200)
    
    return Response({"detail": "Invalid credentials"}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reset_password(request):
    email = request.data.get('email')
    new_password = request.data.get('new_password')
    user = get_object_or_404(User, email=email)
    
    # Update password and notify user
    user.password = make_password(new_password)
    user.save()
    send_password_update_alert(email)
    
    return Response({"message": "Password updated successfully"}, status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def invite_member(request):
    org_id = request.data.get('org_id')
    user_email = request.data.get('user_email')
    role_id = request.data.get('role_id')
    
    organization = get_object_or_404(Organization, id=org_id)
    user = get_object_or_404(User, email=user_email)
    role = get_object_or_404(Role, id=role_id)
    
    # Check if a member with the same role and organization already exists
    if Member.objects.filter(org=organization, user=user, role=role).exists():
        return Response({"message": "A member with the same role and organization already exists."}, status=400)
    
    # Add the user to the organization
    Member.objects.create(org=organization, user=user, role=role, status=0)
    
    # Generate and send invite link
    invite_link = generate_invite_link(user.id, org_id)
    send_invite_email(user_email, invite_link)
    
    return Response({"message": "Member invited successfully"}, status=200)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_member(request, org_id, user_id):
    organization = get_object_or_404(Organization, id=org_id)
    user = get_object_or_404(User, id=user_id)
    
    # Get all member instances for this user and organization
    members = Member.objects.filter(org=organization, user=user)
    
    if members.exists():
        # Delete all matching member records
        members.delete()
        return Response({"message": "Member(s) deleted successfully"}, status=200)
    
    return Response({"message": "No member found for the given organization and user"}, status=404)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_member_role(request):
    org_id = request.data.get('org_id')
    user_id = request.data.get('user_id')
    role_id = request.data.get('role_id')
    
    organization = get_object_or_404(Organization, id=org_id)
    user = get_object_or_404(User, id=user_id)
    role = get_object_or_404(Role, id=role_id)
    
    # Get all member records for the organization and user
    members = Member.objects.filter(org=organization, user=user)
    
    if members.exists():
        # Update the role for each matching member
        members.update(role=role)
        return Response({"message": "Member roles updated successfully"}, status=200)
    
    return Response({"message": "No member found for the given organization and user"}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def role_wise_user_count(request):
    from_date = request.query_params.get('from_date')
    to_date = request.query_params.get('to_date')
    status = request.query_params.get('status')

    query = Member.objects.select_related('role').values('role__name').annotate(count=Count('user'))

    if from_date:
        query = query.filter(created_at__gte=from_date)
    if to_date:
        query = query.filter(created_at__lte=to_date)
    if status:
        query = query.filter(status=status)

    return Response(list(query), status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def organization_wise_member_count(request):
    from_date = request.query_params.get('from_date')
    to_date = request.query_params.get('to_date')
    status = request.query_params.get('status')

    query = Member.objects.select_related('org').values('org__name').annotate(count=Count('user'))

    if from_date:
        query = query.filter(created_at__gte=from_date)
    if to_date:
        query = query.filter(created_at__lte=to_date)
    if status:
        query = query.filter(status=status)

    return Response(list(query), status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def organization_role_wise_user_count(request):
    from_date = request.query_params.get('from_date')
    to_date = request.query_params.get('to_date')
    status = request.query_params.get('status')

    query = Member.objects.select_related('org', 'role').values('org__name', 'role__name').annotate(count=Count('user'))

    if from_date:
        query = query.filter(created_at__gte=from_date)
    if to_date:
        query = query.filter(created_at__lte=to_date)
    if status:
        query = query.filter(status=status)

    return Response(list(query), status=200)
