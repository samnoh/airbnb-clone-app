from django.contrib import admin
from django.utils.html import mark_safe
from . import models


class PhotoInline(admin.TabularInline):

    model = models.Photo


@admin.register(models.Room)
class RoomAdmin(admin.ModelAdmin):

    inlines = (PhotoInline,)

    list_display = (
        "name",
        "photo_number",
    )


@admin.register(models.Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ("__str__", "get_thumbnail")

    def get_thumbnail(self, obj):
        return mark_safe(f'<img width=50 src="{obj.file.url}" />')

    get_thumbnail.short_description = "Thumbnail"
