from django.db import transaction
from django.db.models import Q , Prefetch
from rest_framework import status
from rest_framework.exceptions import PermissionDenied,ValidationError
from rest_framework.permissions import IsAuthenticated,SAFE_METHODS
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet,ModelViewSet
from rest_framework.mixins import RetrieveModelMixin,UpdateModelMixin,ListModelMixin,DestroyModelMixin,CreateModelMixin
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import CustomBoardPermissionClass,CustomListPermissionClass,CustomCardPermissionClass,CustomCardMemberPermissionClass,CustomBoardMemberPermissionClass,CustomCardFilePermissionClass,CustomCardCommentPermissionClass
from .models import Board,List,Card,BoardMember,CardFile,CardMember,CardComment
from .serializers import CardCommentSerializer,ListUpdateSerializer,CardMemberSerializer,CardUpdateSerializer,UpdateBoardMemberSerializer,MoveListSerializer,MoveCardSerializer
from .serializers import BoardSerializer,ListSerializer,CardSerializer,BaseBoardMemberSerializer,CardFileSerializer,ListCreateSerializer,MoveCardSerializer
from .filters import CardCommentsFilter,BoardMemberFilter,CardFilter,BoardFilter,ListFilter
# Create your views here.


def get_board(board_id):
    try:
        board = Board.objects.get(pk=board_id)
    except:
        raise PermissionDenied("The board isn't exists")
    
    return board

def get_board_member(board_id,user):
    try:
        board_member = BoardMember.objects.get(board_id=board_id,user=user).role
    except:
        raise PermissionDenied("The BoardMember isn't exists")
    return board_member

def get_list(list_id):
    try:
        moving_list = List.objects.get(pk=list_id)
    except:
        raise PermissionDenied("the list isn't exist")

    return moving_list

def get_card(card_id):
    try:
        card = Card.objects.get(pk=card_id)
    except:
        raise ValidationError("The card isn't exist")
    return card

class BoardView(ModelViewSet):
    serializer_class = BoardSerializer
    permission_classes= [ CustomBoardPermissionClass ]
    filter_backends = [DjangoFilterBackend]
    filterset_class = BoardFilter


    def get_queryset(self):
        user_id = self.request.user.id
        boards_id = BoardMember.objects.select_related('user').filter(user_id=user_id).values('board_id')
        ordered_cards_prefetch = Prefetch(
            'cards',  # The related field on List
            queryset=Card.objects.order_by('position')  # Ordering cards by position
        )

        # Prefetch related lists and order by 'position', including cards
        ordered_lists_prefetch = Prefetch(
            'lists',  # The related field on Board
            queryset=List.objects.prefetch_related(ordered_cards_prefetch).order_by('position')  # Ordering lists and their cards by position
        )

        queryset = Board.objects.prefetch_related(
            'board_members__user',
            ordered_lists_prefetch,
            'lists__cards__card_files',
            'lists__cards__card_members__user',
            'lists__cards__card_comments__user',
        ).select_related('board_owner').filter(
            Q(board_owner=user_id) | Q(id__in=boards_id)
        )
        return queryset

    def get_serializer_context(self):
        return {"board_owner":self.request.user.id}
        

class ListView(ModelViewSet):
    permission_classes = [CustomListPermissionClass]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ListFilter

    def initial(self, request, *args, **kwargs):
        
        try:
            board_id = self.kwargs['board_pk']
            self.board_member =  BoardMember.objects.get(board_id=board_id, user=self.request.user)
        except BoardMember.DoesNotExist:
            self.board_member = None

        return super().initial(request, *args, **kwargs)

    def get_queryset(self):
        
        ordered_cards_prefetch = Prefetch(
            'cards',  # The related field on List
            queryset=Card.objects.order_by('position')  # Ordering cards by position
        )

        queryset = List.objects.select_related('board')\
        .prefetch_related(
            ordered_cards_prefetch,
            'cards__card_files',
            'cards__card_members__user',
            'cards__card_comments__user',
            'board__board_members__user',
        ).order_by('position').filter(board_id=self.kwargs['board_pk'])

        return queryset
    
    def get_serializer_class(self):
        if self.action == 'move':
            return MoveListSerializer
        if self.request.method == 'POST':
            return ListCreateSerializer
        elif self.request.method in ['PATCH','PUT']:
            return ListUpdateSerializer
        return ListSerializer

    def get_serializer_context(self):
        return {"board_id":self.kwargs['board_pk'],"user":self.request.user,
                "board_member":self.board_member
               }
    
    
    @action(detail=True,methods=['POST'])
    def move(self, request, pk=None, board_pk=None):
        serializer = MoveListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        goal_board_pk = serializer.data['goal_board_pk']
        goal_position = serializer.data['position']

        goal_board = get_board(goal_board_pk)
        goal_board_member_role = get_board_member(goal_board_pk,request.user)
        moving_list = get_list(pk)
        
        if goal_board_member_role == 'Member':
            raise PermissionDenied("You can't move the list because the role in the goal board is member")


        board_goal_lists = List.objects.filter(board_id=goal_board_pk)
        board_goal_lists_positions = board_goal_lists.filter(position__gte=goal_position)

        if board_goal_lists.filter(name=moving_list.name).exists():
            raise ValidationError("A list with the same name already exists on the goal board.")

        if goal_position > board_goal_lists.count() + 1:
            raise ValidationError("Invalid goal position.")

        with transaction.atomic():
            for value in board_goal_lists_positions:
                if value.position >= goal_position:
                    value.position += 1 
            moving_list.board = goal_board
            moving_list.position = goal_position
            moving_list.save()

            List.objects.bulk_update(board_goal_lists_positions, ['position'])
        return Response({"detail": "List moved successfully."}, status=status.HTTP_200_OK)

        
class CardView(ModelViewSet):
    permission_classes = [CustomCardPermissionClass]
    filterset_class = CardFilter
    filter_backends = [DjangoFilterBackend]

    def initial(self, request, *args, **kwargs):
        
        try:
            board_id = self.kwargs['board_pk']
            self.board_member =  BoardMember.objects.get(board_id=board_id, user=self.request.user)
        except BoardMember.DoesNotExist:
            self.board_member = None

        return super().initial(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Card.objects.select_related('list__board__board_owner',)\
               .prefetch_related(
                   'card_files',
                   'card_members__user',
                   'card_comments__user',
                   'list__board__board_members__user',
                ).order_by('position').filter(list_id=self.kwargs['list_pk'])

        return queryset
    
    
    def get_serializer_class(self):
        if self.action == 'move':
            return MoveCardSerializer
        if self.request.method in ['PATCH','PUT']:
            return CardUpdateSerializer
        else:
            return CardSerializer

    def get_serializer_context(self):
        list_id = self.kwargs['list_pk']
        return {"list_id":list_id,"board_id":self.kwargs['board_pk'],"user":self.request.user,
                "board_member":self.board_member
               }

    @action(detail=True, methods=['POST'])
    def move(self, request, pk=None, board_pk=None, list_pk=None):
        serializer = MoveCardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        goal_board_pk = serializer.validated_data['goal_board_pk']
        goal_list_pk = serializer.validated_data['goal_list_pk']
        goal_position = serializer.validated_data['position']

        goal_board_member_role = get_board_member(goal_board_pk, request.user)
        goal_list = get_list(goal_list_pk)
        moving_card = get_card(pk)

        moving_card_list_id = moving_card.list_id

        if moving_card_list_id != int(list_pk):
            raise ValidationError("The card does not belong to the provided list.")

        if moving_card.list.board_id != int(board_pk):
            raise ValidationError("The card does not belong to the provided board.")

        if goal_board_member_role == 'Member':
            raise PermissionDenied("You don't have permission to move the card as a member on the goal board.")

        if goal_list.board_id != goal_board_pk:
            raise ValidationError("The specified list does not belong to the provided board.")

        goal_list_cards = Card.objects.filter(list_id=goal_list_pk).order_by('position')
        goal_list_cards_positions = goal_list_cards.filter(position__gte=goal_position)

        if goal_position > goal_list_cards.count() + 1:
            raise ValidationError("Invalid goal position.")

        with transaction.atomic():
            for card in goal_list_cards_positions:
                card.position += 1

            moving_card.list = goal_list
            moving_card.position = goal_position
            moving_card.save()

            Card.objects.bulk_update(goal_list_cards_positions, ['position'])

        return Response({"detail": "Card moved successfully."}, status=status.HTTP_200_OK)

class BoardMemberView(ModelViewSet):
    permission_classes = [CustomBoardMemberPermissionClass]
    filter_backends = [DjangoFilterBackend]
    filterset_class = BoardMemberFilter
    
    def initial(self, request, *args, **kwargs):
        
        try:
            board_id = self.kwargs['board_pk']
            self.board_member =  BoardMember.objects.get(board_id=board_id, user=self.request.user)
        except BoardMember.DoesNotExist:
            self.board_member = None

        return super().initial(request, *args, **kwargs)

    def get_queryset(self):
        queryset = BoardMember.objects.select_related('board','user').filter(board_id=self.kwargs['board_pk'])

        return queryset
    
    def get_serializer_class(self):
        if self.request.method in ['PATCH','PUT']:
            return UpdateBoardMemberSerializer
        else:
            return BaseBoardMemberSerializer
        
    def get_serializer_context(self):
        return {"creator_id":self.request.user.id,"board_id":self.kwargs['board_pk']}
    
    def destroy(self, request, *args, **kwargs):
        member_to_delete = self.get_object()  
        
        board_member_requesting = self.board_member
        
        if board_member_requesting.role == 'BoardOwner':
            if member_to_delete.role == 'BoardOwner':
                raise PermissionDenied("A BoardOwner cannot delete themselves.")
        
        elif board_member_requesting.role == 'Admin':
            if member_to_delete.role in ['Admin', 'BoardOwner']:
                raise PermissionDenied("Admin cannot delete another Admin or the BoardOwner.")
        
        elif board_member_requesting.role == 'Manager':
            if member_to_delete.role != 'Member':
                raise PermissionDenied("Managers can only delete Members.")
        
        else:
            raise PermissionDenied("You don't have permission to delete members.")
        
        return super().destroy(request, *args, **kwargs)

class CardMemberView(CreateModelMixin,DestroyModelMixin,ListModelMixin,RetrieveModelMixin,GenericViewSet):
    serializer_class = CardMemberSerializer
    permission_classes = [CustomCardMemberPermissionClass]
    
    def initial(self, request, *args, **kwargs):
        
        try:
            board_id = self.kwargs['board_pk']
            self.board_member =  BoardMember.objects.get(board_id=board_id, user=self.request.user)
        except BoardMember.DoesNotExist:
            self.board_member = None

        return super().initial(request, *args, **kwargs)

    def get_queryset(self):
        queryset = CardMember.objects.select_related('user','card__list__board')\
        .prefetch_related('card__list__board__board_members__user').filter(card_id=self.kwargs['card_pk'])
        
        return queryset

    def get_serializer_context(self):
        return {"user_id":self.request.user.id,"card_id":self.kwargs['card_pk'],
                "board_id":self.kwargs['board_pk'],"board_member":self.board_member}

    def destroy(self, request, *args, **kwargs):
        
        board_member_requested = self.board_member

        if board_member_requested.role == 'Member':
            raise PermissionDenied("Members can't delete members from card")
        return super().destroy(request, *args, **kwargs)
    
class CardFileView(ModelViewSet):
    permission_classes = [CustomCardFilePermissionClass]

    def initial(self, request, *args, **kwargs):
        
        try:
            board_id = self.kwargs['board_pk']
            self.board_member =  BoardMember.objects.get(board_id=board_id, user=self.request.user)
        except BoardMember.DoesNotExist:
            self.board_member = None

        return super().initial(request, *args, **kwargs)

    def get_queryset(self):
        queryset = CardFile.objects.select_related('card').filter(card_id=self.kwargs['card_pk']).all()
        return queryset
    serializer_class = CardFileSerializer

    def get_serializer_context(self):
        return {"card_id":self.kwargs['card_pk']}
    
class CardCommentView(ModelViewSet):
    serializer_class = CardCommentSerializer
    permission_classes = [CustomCardCommentPermissionClass]
    filterset_class = CardCommentsFilter
    filter_backends = [DjangoFilterBackend]
    
    def initial(self, request, *args, **kwargs):
        
        try:
            board_id = self.kwargs['board_pk']
            self.board_member =  BoardMember.objects.get(board_id=board_id, user=self.request.user)
        except BoardMember.DoesNotExist:
            self.board_member = None

        return super().initial(request, *args, **kwargs)

    def get_queryset(self):
        queryset = CardComment.objects.select_related('user','card').filter(card_id=self.kwargs['card_pk'])
        return queryset

    def get_serializer_context(self):
        return {"card_id":self.kwargs['card_pk'],"user_id":self.request.user.id}
    
