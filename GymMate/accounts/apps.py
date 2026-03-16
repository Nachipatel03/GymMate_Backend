from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        import os
        # Ensure the scheduler only runs in the main process, not for the auto-reloader
        if os.environ.get('RUN_MAIN') == 'true':
            from . import scheduler
            scheduler.start()
        import accounts.signals