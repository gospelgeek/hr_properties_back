from django.contrib.auth.models import AbstractUser
from django.db import models

class Role(models.Model):
    ADMIN = 'admin'
    CLIENTE = 'cliente'
    SOPORTE = 'soporte'
    INVITADO = 'invitado'
    
    ROLE_CHOICES = [
        (ADMIN, 'Administrator'),
        (CLIENTE, 'Client'),
        (SOPORTE, 'Support'),
        (INVITADO, 'Guest'),
    ]
    
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    
    class Meta:
        db_table = 'role'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
    
    def __str__(self):
        return self.get_name_display()

class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Email')
    name = models.CharField(max_length=255, blank=True, verbose_name='Full Name')
    google_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    profile_picture = models.URLField(blank=True, null=True, verbose_name='Profile Picture')
    
    # Sobrescribir los campos para evitar conflictos de reverse accessors
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.email
    
    def get_roles(self):
        return [ur.role.name for ur in self.userrole_set.all()]
    
    def has_role(self, role_name):
        return self.userrole_set.filter(role__name=role_name).exists()
    
    def is_admin_user(self):
        return self.has_role(Role.ADMIN)

class UserRole(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='id_user')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, db_column='id_role')
    
    class Meta:
        db_table = 'user_role'
        unique_together = ('user', 'role')
        verbose_name = 'User Role'
        verbose_name_plural = 'User Roles'
    
    def __str__(self):
        return f"{self.user.email} - {self.role.name}"