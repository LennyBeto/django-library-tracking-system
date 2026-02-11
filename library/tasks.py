from celery import shared_task
from .models import Loan
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Loan


@shared_task
def send_loan_notification(loan_id):
    try:
        loan = Loan.objects.get(id=loan_id)
        member_email = loan.member.user.email
        book_title = loan.book.title
        send_mail(
            subject='Book Loaned Successfully',
            message=f'Hello {loan.member.user.username},\n\nYou have successfully loaned "{book_title}".\nPlease return it by the due date.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[member_email],
            fail_silently=False,
        )
    except Loan.DoesNotExist:
        pass

@shared_task
def check_overdue_loans():
    """
    Celery task that runs daily to check for overdue book loans
    and sends email notifications to members.
    """
    # Query all loans that are overdue
    overdue_loans = Loan.objects.filter(
        is_returned=False,
        due_date__lt=timezone.now().date()
    ).select_related('book', 'member')

    notifications_sent = 0
    
    for loan in overdue_loans:
        days_overdue = loan.days_overdue()
        
        # Prepare email content
        subject = f'Overdue Book Reminder: {loan.book.title}'
        message = f"""
Dear {loan.member.first_name} {loan.member.last_name},

This is a friendly reminder that the following book is overdue:

Book Title: {loan.book.title}
Loan Date: {loan.loan_date}
Due Date: {loan.due_date}
Days Overdue: {days_overdue}

Please return the book as soon as possible to avoid any late fees.

If you need to extend your loan period, please use our loan extension feature before the due date.

Thank you for your cooperation.

Best regards,
Library Management System
"""
        
        try:
            # Send email notification
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[loan.member.email],
                fail_silently=False,
            )
            notifications_sent += 1
        except Exception as e:
            # Log the error (in production, use proper logging)
            print(f"Failed to send email to {loan.member.email}: {str(e)}")
    
    return f"Checked {overdue_loans.count()} overdue loans. Sent {notifications_sent} notifications."


@shared_task
def send_loan_reminder(loan_id):
    """
    Send a reminder email for a specific loan.
    This can be used for individual notifications.
    """
    try:
        loan = Loan.objects.select_related('book', 'member').get(id=loan_id)
        
        if loan.is_returned:
            return "Loan already returned"
        
        subject = f'Loan Reminder: {loan.book.title}'
        message = f"""
Dear {loan.member.first_name} {loan.member.last_name},

This is a reminder about your current book loan:

Book Title: {loan.book.title}
Loan Date: {loan.loan_date}
Due Date: {loan.due_date}

Please return the book by the due date or extend your loan period if needed.

Thank you,
Library Management System
"""
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[loan.member.email],
            fail_silently=False,
        )
        
        return f"Reminder sent to {loan.member.email}"
    
    except Loan.DoesNotExist:
        return f"Loan with ID {loan_id} not found"
    except Exception as e:
        return f"Error sending reminder: {str(e)}"
