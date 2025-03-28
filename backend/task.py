
from workers import celery
from models import *
from celery.schedules import crontab
from mailer import send_email
from flask import render_template 
from datetime import datetime, timedelta

@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    # sender.add_periodic_task(crontab(minute=0, hour=10), send_daily_reminders.s(), name='send_daily_reminders at 10:00')
    sender.add_periodic_task(crontab(minute='*/1'), send_daily_reminders.s(), name='send_daily_reminders every 60 seconds')


@celery.task()
def send_daily_reminders():
    """ Send daily reminders to user for attempting new quizzes """
    # Get all non-admin users
    users = User.query.filter_by(role='user').all()
    results = []
    for user in users:
        now = datetime.utcnow()
        last_day = now - timedelta(days=1)
        # Get user's quiz attempts in the last 24 hours
        recent_scores = Score.query.filter_by(user_id=user.id).filter(
            Score.time_stamp_of_attempt.between(last_day, now)
        ).all()
        score_count = len(recent_scores)
        
        # Calculate average score
        average_score = 0
        if score_count > 0:
            total_percentage = sum((score.total_scored / score.total_questions) * 100 for score in recent_scores)
            average_score = round(total_percentage / score_count, 2)
        
        # Determine performance level and color
        performance_level, performance_color = get_performance_metrics(average_score)
        
        # Get available quizzes that the user hasn't attempted
        attempted_quiz_ids = [score.quiz_id for score in Score.query.filter_by(user_id=user.id).all()]
        available_quizzes = Quiz.query.filter(
            Quiz.id.notin_(attempted_quiz_ids),
            Quiz.status == 'active',
            Quiz.start_date <= now,
            Quiz.end_date >= now
        ).count()
        
        html_content = render_template(
            'daily_reminder.html',
            user=user,
            recent_scores=score_count,
            average_score=average_score,
            performance_level=performance_level,
            performance_color=performance_color,
            available_quizzes=available_quizzes
        )
        send_email(to=user.username, subject='Daily Quiz Reminder', body=html_content)
        results.append(f"Mail sent to {user.full_name} - Recent scores: {score_count}, Performance: {average_score}% ({performance_level})")
    
    return "\n".join(results)


@celery.task()
def send_monthly_activity_report():
    # Get all non-admin users
    users = User.query.filter_by(role='user').all()
    results = []
    for user in users:
        now = datetime.utcnow()
        last_month = now - timedelta(days=30)
        # Get user's scores from last month
        monthly_scores = Score.query.filter_by(user_id=user.id).filter(
            Score.time_stamp_of_attempt.between(last_month, now)
        ).all()
        score_count = len(monthly_scores)
        
        # Calculate average score and other metrics
        average_score = 0
        best_score = 0
        if score_count > 0:
            total_percentage = sum((score.total_scored / score.total_questions) * 100 for score in monthly_scores)
            average_score = round(total_percentage / score_count, 2)
            best_score = max((score.total_scored / score.total_questions) * 100 for score in monthly_scores)
        
        # Determine performance level and color
        performance_level, performance_color = get_performance_metrics(average_score)
        
        html_content = render_template(
            'monthly_activity_report.html',
            user=user,
            score_count=score_count,
            average_score=average_score,
            best_score=round(best_score, 2),
            performance_level=performance_level,
            performance_color=performance_color
        )
        send_email(to=user.username, subject='Monthly Activity Report', body=html_content)
        results.append(f"Monthly report sent to {user.full_name} - Total scores: {score_count}, Avg: {average_score}%, Best: {round(best_score, 2)}%")
    
    return "\n".join(results)

def get_performance_metrics(percentage):
    """Helper function to determine performance level and color"""
    if percentage >= 90:
        return "Excellent", "#198754"  # success
    elif percentage >= 75:
        return "Good", "#0dcaf0"  # info
    elif percentage >= 60:
        return "Fair", "#ffc107"  # warning
    else:
        return "Needs Improvement", "#dc3545"  # danger
       
