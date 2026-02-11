from rest_framework import serializers
from .models import Author, Book, Member, Loan
from django.contrib.auth.models import User


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(), source='author', write_only=True
    )

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'author_id', 'isbn', 'genre', 'available_copies']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class MemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )

    class Meta:
        model = Member
        fields = ['id', 'user', 'user_id', 'membership_date']


class LoanSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(), source='book', write_only=True
    )
    member = MemberSerializer(read_only=True)
    member_id = serializers.PrimaryKeyRelatedField(
        queryset=Member.objects.all(), source='member', write_only=True
    )
    is_overdue = serializers.SerializerMethodField()
    days_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = [
            'id', 'book', 'book_id', 'member', 'member_id',
            'loan_date', 'due_date', 'return_date', 'is_returned',
            'is_overdue', 'days_overdue'
        ]
        read_only_fields = ['loan_date', 'due_date']

    def get_is_overdue(self, obj):
        """Check if the loan is overdue."""
        return obj.is_overdue()

    def get_days_overdue(self, obj):
        """Get the number of days overdue."""
        return obj.days_overdue()


class ExtendDueDateSerializer(serializers.Serializer):
    """Serializer for extending loan due dates."""
    additional_days = serializers.IntegerField(min_value=1, max_value=30)

    def validate_additional_days(self, value):
        """Validate that additional_days is a positive integer."""
        if value <= 0:
            raise serializers.ValidationError("Additional days must be a positive integer.")
        return value
