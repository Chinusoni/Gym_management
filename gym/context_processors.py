from .models import GymSettings

def gym_settings(request):
    try:
        gym = GymSettings.objects.get(pk=1)
    except GymSettings.DoesNotExist:
        gym = GymSettings()
    return {'gym': gym}
