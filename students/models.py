from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.contrib.auth.hashers import make_password
from django.utils.timezone import now
from phonenumber_field.modelfields import PhoneNumberField


class Classes(models.Model):
    name = models.CharField(max_length=10, unique=True,verbose_name="Tên lớp")
    max_students = models.PositiveSmallIntegerField(
        verbose_name="Số lượng tối đa",
        validators=[MinValueValidator(50), MaxValueValidator(80)],
        help_text="Số lượng học sinh tối đa từ 50-80"
    )
    current_students = models.PositiveIntegerField(
        verbose_name="Số lượng hiện tại",
        default=0,
        #editable=False # không thể chỉnh sửa ở giao diện admin
    )

    class Meta:
        verbose_name = "Lớp học"
        verbose_name_plural = "Các lớp học"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.current_students}/{self.max_students})"


class Student(models.Model):
    GENDER_CHOICES = (
        ('M', 'Nam'),
        ('F', 'Nữ'),
        ('O', 'Khác')
    )

    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/',
        verbose_name="Ảnh đại diện",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        default="students/avatars/default.png"
    )
    full_name = models.CharField(max_length=150, verbose_name="Họ và tên", db_index=True)  # Đánh index cho tìm kiếm nhanh hơn
    date_of_birth = models.DateField(verbose_name="Ngày sinh", null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Giới tính")
    
    student_class = models.ForeignKey(
        'Classes',
        on_delete=models.PROTECT,
        related_name='students',
        verbose_name="Lớp học",
        null=True,
        blank=True
    )

    phone_number = PhoneNumberField(verbose_name="Số điện thoại", region='VN', unique=True)
    email = models.EmailField(verbose_name="Email", unique=True)
    address = models.CharField(max_length=255, verbose_name="Địa chỉ", blank=True)
    username = models.CharField(max_length=20, unique=True, verbose_name="Tên đăng nhập")
    password = models.CharField(max_length=128, verbose_name="Mật khẩu")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Học sinh"
        verbose_name_plural = "Danh sách học sinh"
        ordering = ['student_class', 'full_name']
        
        # Thêm index để tối ưu truy vấn
        indexes = [
            models.Index(fields=['student_class', 'full_name'], name='idx_student_class_fullname'),  # Multi-column index
            models.Index(fields=['phone_number', 'email'], name='idx_phone_email'),  # Multi-column index
            models.Index(fields=['created_at'], name='idx_created_at'),  # Dùng nếu có truy vấn ORDER BY created_at DESC
        ]

        constraints = [
            models.CheckConstraint(check=~models.Q(phone_number=""), name="phone_number_not_empty"),
            models.CheckConstraint(check=~models.Q(email=""), name="email_not_empty"),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.student_class.name if self.student_class else 'Chưa xếp lớp'})"

    def save(self, *args, **kwargs):
        """Mã hóa mật khẩu trước khi lưu (nếu mật khẩu chưa được mã hóa)."""
        if not self.password.startswith("pbkdf2_sha256$"):
            self.password = make_password(self.password)
        # Nếu có lớp học và là sinh viên mới, cập nhật số lượng học sinh trong lớp
        if self.student_class and self._state.adding:
            if self.student_class.current_students >= self.student_class.max_students:
                raise ValueError("Lớp học đã đủ số lượng học sinh.")
            self.student_class.current_students += 1
            self.student_class.save()
        super().save(*args, **kwargs)

    def clean(self):
        """Kiểm tra logic trước khi lưu"""
        if self.date_of_birth and self.date_of_birth > now().date():
            raise ValueError("Ngày sinh không thể ở tương lai.")

class Book(models.Model):
    COVER_TYPES = (
        ('H', 'Bìa cứng'),
        ('P', 'Bìa mềm')
    )

    cover_image = models.ImageField(
        upload_to='book/%Y/%m/',
        verbose_name="Bìa sách",
        blank=True,
        null=True,
    )
    title = models.CharField(max_length=255, verbose_name="Tên sách", db_index=True)
    author = models.CharField(max_length=255, verbose_name="Tác giả")
    isbn = models.CharField(max_length=13, verbose_name="ISBN", unique=True, blank=True, null=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Giá tiền",
        validators=[MinValueValidator(0)]
    )
    quantity = models.PositiveIntegerField(verbose_name="Số lượng tồn kho", default=0)
    cover_type = models.CharField(max_length=1, choices=COVER_TYPES, verbose_name="Loại bìa", default='P')
    publish_date = models.DateField(verbose_name="Ngày xuất bản", default=now)
    description = models.TextField(verbose_name="Mô tả", blank=True, default='Đang cập nhật')

    class Meta:
        verbose_name = "Sách"
        verbose_name_plural = "Danh mục sách"
        ordering = ['-publish_date', 'title']
        constraints = [
            models.CheckConstraint(check=models.Q(quantity__gte=0), name="quantity_non_negative")
        ]

    def __str__(self):
        return f"{self.title} - {self.author} ({self.price} VNĐ)"
