from django.db.models import Q
from django.db import transaction
from django.core.exceptions import ValidationError
from rest_framework.exceptions import PermissionDenied
from rest_framework import serializers
from core.models import User
from core.serializers import SimpleUserSerializer
from .models import Board , List , Card , BoardMember , CardMember , CardFile ,CardComment

def validate_if_list_name_exists(board_id,list_name):
    if List.objects.select_related('board').filter(board=board_id,name=list_name):
        raise ValidationError(f"The list name {list_name} is already exists")

    
class BoardMemberSerializer(serializers.ModelSerializer):
    users = serializers.SerializerMethodField()
    class Meta:
        model = BoardMember
        fields = ['users']
    
    def get_users(self, obj):
        return obj.user.username

class SimpleCardSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = Card
        fields = ['id']

class CardCommentSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)
    card = SimpleCardSerializer(read_only=True)
    class Meta:
        model = CardComment
        fields = ['id','text','card','user','date','time']

    def create(self, validated_data):
        card_id = self.context['card_id']
        user_id = self.context['user_id']
        return CardComment.objects.create(card_id=card_id,user_id=user_id,**validated_data)

class CardMemberSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer()
    card = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = CardMember
        fields = ['id','user','card']

    def get_card(self,obj):
        return obj.card.id
   
    def create(self, validated_data):
        ans = None
        user_id = validated_data['user']['id']
        card_id = self.context['card_id']

        ans = self.context['board_member'].role
        

        if ans == 'Member' or ans == None:
            raise PermissionDenied("Members can't add members to card")

        card_member_test = CardMember.objects.filter(card_id=card_id,user_id=user_id)
        # print(card_member_test[0].card.id,card_member_test[0].user.id)
        if len(card_member_test):
            raise Exception("the user is already member in the card")

        try:
            card_instance = Card.objects.get(id=card_id)
        except Card.DoesNotExist:
            raise Exception("The CARD is not exists")
        
        try:
            user_instance = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise Exception("The USER is not exists")
         
        return CardMember.objects.create(card=card_instance,user=user_instance)
    
class CardFileSerializer(serializers.ModelSerializer):
    # file = serializers.FileField()
    class Meta:
        model = CardFile
        fields = ['id','file']

    def validate_file(self, value):
        if value is None:
            raise serializers.ValidationError("No file was provided.")
        return value

    def create(self, validated_data):
        card_id = self.context['card_id']
        card = CardFile.objects.create(card_id=card_id,**validated_data)
        return card

class CardSerializer(serializers.ModelSerializer):
    position = serializers.IntegerField(read_only=True)
    card_members = serializers.SerializerMethodField(read_only=True)
    card_files = CardFileSerializer(many=True,read_only=True)
    card_comments = CardCommentSerializer(many=True,read_only=True)
    class Meta:
        model = Card
        fields = ['id','name','description','position','starts_Date','finish_Date','card_members','card_files','card_comments']

    def get_card_members(self,obj):
        return [ value.user.username for value in obj.card_members.all()]
    
    def create(self, validated_data):
        ans=self.context['board_member']
        
        if ans.role in ['Member',None]:
            raise PermissionDenied("Members can't add cards")
        
        list_id = self.context['list_id']
        position = validated_data.pop('position',None)
        position = len(Card.objects.filter(list_id=list_id)) + 1
        return Card.objects.create(list_id=list_id,position=position,**validated_data)
        
class CardUpdateSerializer(serializers.ModelSerializer):
    card_members = serializers.SerializerMethodField(read_only=True)
    card_files = CardFileSerializer(many=True,read_only=True)
    card_comments = CardCommentSerializer(many=True,read_only=True)
    class Meta:
        model = Card
        fields = ['id','name','description','position','starts_Date','finish_Date','card_members','card_files','card_comments']

    def get_card_members(self,obj):
        return [ value.user.username for value in obj.card_members.all()]
    
    def update(self, instance, validated_data):
        with transaction.atomic():
            list_id = self.context['list_id']
            swapped_instance = Card.objects.get(
                Q(position=validated_data['position'])& Q(list_id=list_id)
            )
            swapped_instance.position = instance.position
            swapped_instance.save()
            return super().update(instance,validated_data)

class ListSerializer(serializers.ModelSerializer):
    cards = CardSerializer(many=True,read_only=True)
    class Meta:
        model = List
        fields = ['id','name','position','created_at','cards']

class ListCreateSerializer(serializers.ModelSerializer):
    cards = CardSerializer(many=True,read_only=True)
    position = serializers.IntegerField(read_only=True)
    class Meta:
        model = List
        fields = ['id','name','position','created_at','cards']
   
    def create(self, validated_data):
        board_id = self.context['board_id']
        user = self.context['user']
        user_role = self.context['board_member'].role
        
        if user_role == 'Member' or user_role == None:
            raise Exception("Members can't add lists just managers and above")
        position = validated_data.pop('position',None)
        position = len(List.objects.select_related('board').filter(board_id=board_id)) + 1
        return List.objects.create(board_id=board_id,position=position,**validated_data)

    def validate(self, data):
        board_id = self.context['board_id']
        validate_if_list_name_exists(board_id, data['name'])
        return data

class ListUpdateSerializer(serializers.ModelSerializer):
    cards = CardSerializer(many=True,read_only=True)
    class Meta:
        model = List
        fields = ['id','name','position','created_at','cards']
    
    # def validate(self, data):
    #     board_id = self.context['board_id']
    #     validate_if_list_name_exists(board_id, data['name'])
    #     return data

    def update(self, instance, validated_data):
        with transaction.atomic():
            board_id = self.context['board_id']
            swapped_instance = List.objects.get(
                Q(position=validated_data['position']) & Q(board_id=board_id)
            )
            swapped_instance.position = instance.position
            swapped_instance.save()
            return super().update(instance, validated_data)

class SimpleBoardMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardMember
        fields = ['user','role']

class BoardSerializer(serializers.ModelSerializer):
    lists = ListSerializer(many=True,read_only=True)
    board_owner = serializers.SerializerMethodField()
    board_members = serializers.SerializerMethodField(read_only=True,source='board_members')
    class Meta:
        model = Board
        fields = ['id','name','description','board_owner','created_at','board_members','lists']
    
    def get_board_owner(self,obj):
        return obj.board_owner.username
    
    def get_board_members(self,obj):
        return [{"username":value.user.username,"user_role":value.role} for value in obj.board_members.all()]
    
    def create(self, validated_data):
        board_owner = User.objects.get(id=self.context['board_owner'])
        return Board.objects.create(board_owner=board_owner,**validated_data)

class SimpleBoardSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = Board
        fields = ['id']

class UpdateBoardMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardMember
        fields = ['role']

    def to_representation(self, instance):
        returned_instance = super().to_representation(instance)
        returned_instance['id'] = instance.id
        returned_instance['board_id'] = instance.board_id
        returned_instance['user_id'] = instance.user_id
        
        return returned_instance

    def update(self, instance, validated_data):
        board_id = instance.board.id
        post_role = validated_data['role']
        editor_id = self.context['creator_id']

        editor_role = BoardMember.objects.get(board_id=board_id,user_id=editor_id).role
        current_role = instance.role

        roles = ['Member','Manager','Admin','BoardOwner']
        
        def is_role_higher_or_equal(role_one,role_two):
            return roles.index(role_one) >= roles.index(role_two)
        
        if editor_role == 'BoardOwner':
            if current_role == 'BoardOwner' or post_role == 'BoardOwner' or post_role == 'Admin' or current_role == 'Admin':
                raise PermissionDenied("you can't edit or add another BoardOwner or Admin")

        elif editor_role == 'Admin':
            if is_role_higher_or_equal(current_role, 'Admin'):
                raise PermissionDenied("You cannot modify another Admin or BoardOwner.")
            if post_role == 'BoardOwner' or post_role == 'Admin':
                raise PermissionDenied("You can't make users admins or board_owners")

        
        elif editor_role == 'Manager':
            if is_role_higher_or_equal(current_role, 'Manager'):
                raise PermissionDenied("You cannot modify BoardOwner, Admin, or other Managers.")
            if post_role != 'Manager':
                raise PermissionDenied("You can only promote users to Manager")
        
        
        elif editor_role == 'Member':
            raise PermissionDenied("Members cannot promote or modify roles.")
        
        if instance.user.role in ['Admin']:
            validated_data['role'] = 'Admin'
            
        return super().update(instance, validated_data)
    
class BaseBoardMemberSerializer(serializers.ModelSerializer):
    user= SimpleUserSerializer()
    class Meta:
        model = BoardMember
        fields = ['id','user','role']


    def create(self, validated_data):
        board_id = self.context['board_id']
        user_id = validated_data['user']['id']
        role = validated_data['role']
        creator_id = self.context['creator_id']

        board_member_test = BoardMember.objects.filter(board_id=board_id,user_id=user_id)
        if len(board_member_test):
            raise Exception("the user is already member in the board")

        try:
            board_instance = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            raise Exception("The BOARD is not exists")
        
        try:
            user_instance = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise Exception("The USER is not exists")
        
        creator = BoardMember.objects.get(board_id=board_id,user=creator_id)
        added_user = User.objects.get(id=user_id)

        if creator.role == 'Manager' and role in ['Admin','BoardOwner'] :
            raise PermissionDenied("The manager can't add a member as admin or above")
        if creator.role == 'Manager' and added_user.role in ['Admin','Staff'] :
            raise PermissionDenied("the user is an admin in the app so you can't add him because you can't add admins or above")
        if creator.role == 'Admin' and (role == 'BoardOwner' or role == 'Admin'):
            raise PermissionDenied("The Admin only can add member as Managers or lower")
        if creator.role in ['Admin','BoardOwner'] and role == 'Admin' and user_instance.role not in ['Admin','Staff']:
            raise PermissionDenied("to add an admin as a user he should be an admin in the app first")
        if creator.role == 'BoardOwner' and role == 'BoardOwner':
            raise PermissionDenied("You can add just members As Managers or lower")
        if creator.role == 'Member':
            raise PermissionDenied("you don't have permission to add members")

        if user_instance.role in ['Admin','Staff']:
            return BoardMember.objects.create(user=added_user,board=board_instance,role='Admin')
        else:
            return BoardMember.objects.create(user=added_user,board=board_instance,role=role)


class MoveListSerializer(serializers.ModelSerializer):
    goal_board_pk = serializers.IntegerField()
    position = serializers.IntegerField()

    class Meta:
        model = List
        fields = ['goal_board_pk','position']

    def validate_goal_board_pk(self,value):
        if not Board.objects.filter(pk=value).exists():
            raise serializers.ValidationError("The goal board does not exist.")
        return value
    
    def validate_position(self,value):
        if value <= 0 :
            raise serializers.ValidationError("Position should be bigger than zero")
        return value
    

class MoveCardSerializer(serializers.Serializer):
    goal_board_pk = serializers.IntegerField()
    goal_list_pk = serializers.IntegerField()
    position = serializers.IntegerField()

    class Meta:
        model = Card
        fields = ['goal_board_pk','goal_list_pk','position']

        def validate_position(self,value):
            if value <= 0 :
                raise serializers.ValidationError("Position should be bigger than zero")
            return value