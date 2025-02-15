from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.core.validators import validate_email
from phonenumber_field.validators import validate_international_phonenumber
from django.core.exceptions import ValidationError
from .models import Student
from datetime import date
from django.utils.timezone import now


class StudentSerializer(serializers.ModelSerializer):
    # Hiển thị URL ảnh đại diện đầy đủ
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Student
        fields = [
            'id', 'avatar', 'full_name', 'date_of_birth', 'gender', 'student_class',
            'phone_number', 'email', 'address', 'username', 'password', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'password': {'write_only': True},  # Không trả mật khẩu trong response
            'created_at': {'read_only': True},  # Không cho sửa thời gian tạo
            'updated_at': {'read_only': True},  # Không cho sửa thời gian cập nhật
        }

    def validate_full_name(self, value):
        """Kiểm tra tên hợp lệ."""
        if not value.strip():
            raise serializers.ValidationError("Tên không được để trống.")
        if len(value) > 150:
            raise serializers.ValidationError("Tên không được vượt quá 150 ký tự.")
        return value

    def validate_date_of_birth(self, value):
        """Kiểm tra ngày sinh hợp lệ."""
        if value and value > date.today():
            raise serializers.ValidationError("Ngày sinh không thể ở tương lai.")
        return value

    def validate_phone_number(self, value):
        """Kiểm tra số điện thoại hợp lệ."""
        try:
            validate_international_phonenumber(value)
        except ValidationError:
            raise serializers.ValidationError("Số điện thoại không hợp lệ.")
        
        # Kiểm tra trùng lặp số điện thoại
        if Student.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Số điện thoại đã được sử dụng.")
        
        return value

    def validate_email(self, value):
        """Kiểm tra email hợp lệ và không trùng lặp."""
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Email không hợp lệ.")
        
        if Student.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email đã được sử dụng.")
        
        return value

    def validate_username(self, value):
        """Kiểm tra username hợp lệ."""
        if len(value) < 5:
            raise serializers.ValidationError("Tên đăng nhập phải có ít nhất 5 ký tự.")
        if Student.objects.filter(username=value).exists():
            raise serializers.ValidationError("Tên đăng nhập đã tồn tại.")
        return value

    def validate_password(self, value):
        """Kiểm tra độ mạnh của mật khẩu."""
        if len(value) < 8:
            raise serializers.ValidationError("Mật khẩu phải có ít nhất 8 ký tự.")
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Mật khẩu phải chứa ít nhất một số.")
        if not any(char.isalpha() for char in value):
            raise serializers.ValidationError("Mật khẩu phải chứa ít nhất một chữ cái.")
        if not any(char in "!@#$%^&*()" for char in value):
            raise serializers.ValidationError("Mật khẩu phải chứa ít nhất một ký tự đặc biệt (!@#$%^&*()).")
        return value

    def validate(self, data):
        """Kiểm tra logic tổng hợp trước khi lưu."""
        if data.get('student_class'):
            student_class = data.get('student_class')
            if student_class.current_students >= student_class.max_students:
                raise serializers.ValidationError("Lớp học đã đủ số lượng học sinh.")
        return data

    def create(self, validated_data):
        """Mã hóa mật khẩu trước khi tạo mới."""
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Xử lý cập nhật thông tin học sinh, bao gồm mật khẩu nếu có."""
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        
        return super().update(instance, validated_data)
