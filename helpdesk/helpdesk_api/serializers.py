from rest_framework.serializers import ModelSerializer

from .models import User, Issues, Conversations

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'role', 'department', 'floor', 'created_at']

class IssuesSerializer(ModelSerializer):
    class Meta:
        model = Issues
        fields = ['id', 'title', 'description', 'status', 'created_at', 'reported_by']

class ConversationsSerializer(ModelSerializer):
    class Meta:
        model = Conversations
        fields = ['id', 'issue', 'message', 'sender', 'timestamp']

