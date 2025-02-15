import os
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from .models import Student, Book

# Xóa ảnh cũ khi cập nhật ảnh mới
@receiver(pre_save, sender=Student)
def delete_old_avatar_on_update(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_avatar = Student.objects.get(pk=instance.pk).avatar
        except Student.DoesNotExist:
            return
        new_avatar = instance.avatar
        if old_avatar and old_avatar != new_avatar and old_avatar.name != "students/avatars/default.png":
            if os.path.isfile(old_avatar.path):
                os.remove(old_avatar.path)

# Xóa ảnh khi xóa tài khoản
@receiver(post_delete, sender=Student)
def delete_avatar_on_delete(sender, instance, **kwargs):
    if instance.avatar and instance.avatar.name != "students/avatars/default.png":
        if os.path.isfile(instance.avatar.path):
            os.remove(instance.avatar.path)

# Xóa ảnh cũ khi cập nhật ảnh bìa sách
@receiver(pre_save, sender=Book)
def delete_old_cover_on_update(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_cover = Book.objects.get(pk=instance.pk).cover_image
        except Book.DoesNotExist:
            return
        new_cover = instance.cover_image
        if old_cover and old_cover != new_cover and old_cover.name != "books/covers/default.jpg":
            if os.path.isfile(old_cover.path):
                os.remove(old_cover.path)

# Xóa ảnh khi xóa sách
@receiver(post_delete, sender=Book)
def delete_cover_on_delete(sender, instance, **kwargs):
    if instance.cover_image and instance.cover_image.name != "books/covers/default.jpg":
        if os.path.isfile(instance.cover_image.path):
            os.remove(instance.cover_image.path)