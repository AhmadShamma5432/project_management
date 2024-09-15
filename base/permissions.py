from rest_framework.permissions import BasePermission,IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import SAFE_METHODS
from .models import List,Card,Board,BoardMember

class IsBoardMember(BasePermission):
    def has_permission(self, request, view):
        if not hasattr(view, 'board_member') or view.board_member is None:
            raise PermissionDenied("The user is not a member of the board")
        return True

    def has_object_permission(self, request, view, obj):
        if not hasattr(view, 'board_member') or view.board_member is None:
            raise PermissionDenied("The user is not a member of the board")
        return True

class CustomBoardPermissionClass(BasePermission):
    def has_permission(self, request, view):
        is_authenticated = IsAuthenticated().has_permission(request, view)

        return is_authenticated 
    
    def has_object_permission(self, request, view, obj):
        
        if request.method in ['PATCH','PUT','DELETE']:
            return obj.board_owner == request.user
        return True

class CustomListPermissionClass(BasePermission):

    def has_permission(self, request, view):
        if not hasattr(view, 'board_member') or view.board_member is None:
            raise PermissionDenied("The user is not a member of the board")
        
        board_member_role = view.board_member.role
        if board_member_role == 'Member' and view.action == 'move':
            return False
        
        return True
    def has_object_permission(self, request, view, obj):
        # print(request.action)

        if not hasattr(view, 'board_member') or view.board_member is None:
            raise PermissionDenied("The user is not a member of the board")
        
        board_member = view.board_member

        if request.method in ['DELETE','PATCH','PUT']:
            if board_member.role != 'Member':
                return True
            else:
                return False
        return True
    
class CustomCardPermissionClass(BasePermission):

    def has_permission(self, request, view):
        # Check if the user is a board member and has board-level permissions
        is_board_member = IsBoardMember().has_permission(request, view)
        board_permissions = CustomBoardPermissionClass().has_permission(request, view)

        board_member = view.board_member
        if is_board_member and request.method == 'POST' and board_member.role == 'Member':
            return False
        
        return is_board_member and board_permissions

    def has_object_permission(self, request, view, obj):
        # Ensure the board_member is attached to the view, not the request
        if not hasattr(view, 'board_member') or view.board_member is None:
            raise PermissionDenied("The user is not a member of the board")
        
        board_member = view.board_member
        
        # Handle DELETE method: allow only if the user is not a 'Member'
        if request.method == 'DELETE':
            if board_member.role != 'Member':
                return True
            return False
        
        return True
    
class CustomBoardMemberPermissionClass(BasePermission):
    def has_permission(self, request, view):
        is_board_member = IsBoardMember().has_permission(request,view)
        return is_board_member
    def has_object_permission(self, request, view, obj):
        if not hasattr(view, 'board_member') or view.board_member is None:
            raise PermissionDenied("The user is not a member of the board")
        return True
    
class CustomCardMemberPermissionClass(BasePermission):
    def has_permission(self, request, view):
        is_board_member = IsBoardMember().has_permission(request,view)
        return is_board_member
    
    def has_object_permission(self, request, view, obj):

        if not hasattr(view, 'board_member') or view.board_member is None:
            raise PermissionDenied("The user is not a member of the board")
        
        board_member = view.board_member
        if request.method in ['DELETE'] and board_member.role == 'Member':
            return False
        return True
    

class CustomCardFilePermissionClass(BasePermission):
    def has_permission(self, request, view):
        if not hasattr(view, 'board_member') or view.board_member is None:
            raise PermissionDenied("The user is not a member of the board")
        
        board_member = view.board_member

        if board_member.role == 'Member' and request.method == 'POST':
            return False

        return IsAuthenticated().has_permission(request,view)
    
    def has_object_permission(self, request, view, obj):
        if not hasattr(view, 'board_member') or view.board_member is None:
            raise PermissionDenied("The user is not a member of the board")
        
        board_member = view.board_member

        if board_member.role == 'Member' and request.method in ['PUT','PATCH','DELETE']:
            return False

        return True   
    

class CustomCardCommentPermissionClass(BasePermission):
    def has_permission(self, request, view):
        return IsBoardMember().has_permission(request,view)
    
    def has_object_permission(self, request, view, obj):
        if not hasattr(view, 'board_member') or view.board_member is None:
            raise PermissionDenied("The user is not a member of the board")
        
        board_member = view.board_member    
    
        if request.method == 'DELETE':
            if obj.user == request.user or board_member.role != 'Member':
                return True
            return False
        elif request.method in ['PUT','PATCH']:
            return obj.user == request.user

        return True
            
