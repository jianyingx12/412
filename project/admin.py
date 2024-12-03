from django.contrib import admin
from .models import Medicine, UserProfile, Schedule, Interaction

# Register your models here.

admin.site.register(Medicine)
admin.site.register(UserProfile)
admin.site.register(Schedule)
admin.site.register(Interaction)
