from django.contrib import admin
from .models import *
from django.utils.html import mark_safe

# Register your models here.

class ClassesAdmin(admin.ModelAdmin):
    list_display = ['id','name','current_students','max_students']
    list_per_page = 10
    search_fields = ['id','name']

class StudentAdmin(admin.ModelAdmin):
    readonly_fields = ["image_static"]
    list_display = ['id','full_name','username','student_class','email','phone_number']
    search_fields = ['id','full_name','username','email','phone_number','gender']
    list_per_page = 5
    list_filter = ['student_class__name']

    def image_static(self, avatar):
        if avatar.avatar:
            return mark_safe(f"<img src='{avatar.avatar.url}' width='120px' style='border-radius: 5px;' />")
        return "No Image"
    

class BookAdmin(admin.ModelAdmin):
    list_display = ['id','title','author','quantity','cover_type','price','image']
    search_fields = ['title','author','cover_type','price']
    readonly_fields = ["image_static"]
    list_per_page = 5

    def image_static(self, obj):
        if obj.cover_image:
            return mark_safe(f"<img src='{obj.cover_image.url}' width='360px' style='border-radius: 5px;' />")
        return "No Image"
    
    def image(self, obj):
        if obj.cover_image:
            return mark_safe(f"<img src='{obj.cover_image.url}' width='180px' style='border-radius: 5px;' />")
        return "No Image"


admin.site.register(Student, StudentAdmin)
admin.site.register(Classes, ClassesAdmin)
admin.site.register(Book, BookAdmin)