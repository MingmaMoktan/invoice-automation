from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone

PLAN_UPLOAD_LIMITS = {
    'demo': 3,
    'starter': 200,
    'advanced': 1000,
    'professional': 3000,
    'enterprise': None,  # unlimited
}

def upload_limit_required(view_func):
    """
    Check if user has reached monthly upload limit for their plan.
    """
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            messages.error(request, "You must be logged in to upload invoices.")
            return redirect('login')

        profile = user.userprofile
        now = timezone.now()

        # Reset monthly uploads if month changed
        if profile.last_reset_date is None or profile.last_reset_date.month != now.month:
            profile.uploads_this_month = 0
            profile.last_reset_date = now
            profile.save()

        max_uploads = PLAN_UPLOAD_LIMITS.get(profile.plan)

        if max_uploads is not None and profile.uploads_this_month >= max_uploads:
            messages.warning(request, "You reached your upload limit. Please upgrade your plan.")
            return redirect('pricing')

        return view_func(request, *args, **kwargs)
    
    return _wrapped_view
