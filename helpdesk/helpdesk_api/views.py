import os
from django.shortcuts import render
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.views import TokenObtainPairView

from django.template.loader import render_to_string

# SMTP
import smtplib, ssl
from email.message import EmailMessage

from dotenv import load_dotenv
load_dotenv()

from .models import User, Issues, Conversations
from .serializers import MyTokenObtainPairSerializer, UserSerializer, IssuesSerializer, ConversationsSerializer

def send_mail(subject, to_email, context, type):
        port = 587
        smtp_server =os.getenv('SMTP_SERVER')
        username=os.getenv('EMAIL_USER')
        password =os.getenv('EMAIL_PASSWORD')
        
        if type == "issue_reported":
            html_content = render_to_string('issue_reported.html', context)
        elif type == "issue_resolved":
            html_content = render_to_string('issue_resolved.html', context)
        
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = "technology@crccreditbureau.com"
        msg['To'] = [to_email]
        msg.set_content(html_content, subtype='html')
        
        try:
            if port == 465:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                    server.login(username, password)
                    server.send_message(msg)
            elif port == 587:
                with smtplib.SMTP(smtp_server, port) as server:
                    server.starttls()
                    server.login(username, password)
                    server.send_message(msg)
            else:
                print ("use 465 / 587 as port value")
                exit()
            return True
        except Exception as e:
            print (e)
            return False

class MyTokenObtainPairView(TokenObtainPairView):
    """
    Custom TokenObtainPairView using MyTokenObtainPairSerializer.
    """
    serializer_class = MyTokenObtainPairSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class IssuesViewSet(viewsets.ModelViewSet):
    queryset = Issues.objects.all()
    serializer_class = IssuesSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'reported_by']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        response = super().create(request, *args, **kwargs)
        # issue = Issues.objects.get(id=response.data['id'])
        
        # context = {
        #     'issue_title': issue.title,
        #     'issue_description': issue.description,
        #     'reported_by': issue.reported_by.first_name + ' ' + issue.reported_by.last_name,
        #     'created_at': issue.created_at,
        # }

        # # To Admin
        # send_mail(
        #     subject="New Issue Reported",
        #     to_email="technology@crccreditbureau.com",
        #     context=context,
        #     type="issue_reported"
        # )

        # # To User
        # send_mail(
        #     subject="Issue Reported Successfully",
        #     to_email=issue.reported_by.email,
        #     context=context,
        #     type="issue_reported"
        # )

        return response

class ConversationsViewSet(viewsets.ModelViewSet):
    queryset = Conversations.objects.all()
    serializer_class = ConversationsSerializer