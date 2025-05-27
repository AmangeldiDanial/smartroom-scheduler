from django.contrib.auth.models import User as AuthUser
from scheduler.models import User as CustomUser

auth_user = AuthUser.objects.create_user(
    username='jdoe',
    password='doepass456',
    email='jdoe@example.com'
)

custom_user = CustomUser.objects.get(user_id=2)
custom_user.auth_user = auth_user
custom_user.save()
