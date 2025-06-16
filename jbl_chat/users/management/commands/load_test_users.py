from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile


class Command(BaseCommand):
    help = "Create test users with proper passwords and profiles"

    def handle(self, *args, **kwargs):
        # Create test users
        test_users = [
            {
                "username": "test",
                "email": "john@example.com",
                "password": "test123",
                "first_name": "John",
                "last_name": "Doe",
            },
            {
                "username": "john",
                "email": "john@test.com",
                "password": "john123",
                "first_name": "John",
                "last_name": "Doe",
            },
            {
                "username": "mark",
                "email": "mark@test.com",
                "password": "mark123",
                "first_name": "Mark",
                "last_name": "Gold",
            },
            {
                "username": "juha",
                "email": "juha@test.com",
                "password": "juha123",
                "first_name": "Juha",
                "last_name": "Mattila",
            },
            {
                "username": "maria",
                "email": "maria@test.com",
                "password": "maria124",
                "first_name": "Maria",
                "last_name": "Fuentes",
            },
        ]

        for user_data in test_users:
            # Create or update user
            user, created = User.objects.get_or_create(
                username=user_data["username"],
                defaults={
                    "email": user_data["email"],
                    "first_name": user_data["first_name"],
                    "last_name": user_data["last_name"],
                },
            )

            # Set password
            user.set_password(user_data["password"])
            user.save()

            # Create or update profile
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    "image_url": f"https://api.dicebear.com/9.x/avataaars-neutral/svg?seed={user_data['username']}"  # noqa: E261 E501
                },
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully created user "{user_data["username"]}"'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'User "{user_data["username"]}" already exists')
                )
