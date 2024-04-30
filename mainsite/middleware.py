from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from .models import UserActivity
from login.models import CustomUser

class UserActivityMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            user_obj = CustomUser.objects.get(id=request.user.id)
            if int(user_obj.daily_activity_goal > 0):
                now = timezone.now()
                session_key = 'last_activity'
                last_activity_time = request.session.get(session_key)

                if last_activity_time is not None:
                    last_activity_time = timezone.datetime.fromisoformat(last_activity_time)
                    duration = now - last_activity_time

                    # Check if duration since last recorded activity is 5 or more minutes
                    if duration.total_seconds() / 60 >= user_obj.daily_activity_goal:
                        # Check if an activity record exists for today
                        today_start = timezone.datetime.combine(now.date(), timezone.datetime.min.time()).replace(tzinfo=timezone.utc)
                        today_end = timezone.datetime.combine(now.date(), timezone.datetime.max.time()).replace(tzinfo=timezone.utc)
                        
                        activity_today = UserActivity.objects.filter(user=request.user, date__range=(today_start, today_end))
                        
                        if not activity_today.exists():
                            # Create a new activity record if one doesn't exist for today
                            UserActivity.objects.create(user=request.user, date=now)

                # Update the last activity time
                request.session[session_key] = now.isoformat()