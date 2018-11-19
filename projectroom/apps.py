from django.apps import AppConfig


class DefaultPRConfig(AppConfig):
    name = 'projectroom'
    verbose_name = 'CKW Projectroom'

    def ready(self):
        super(DefaultPRConfig, self).ready()
        import signals
        signals.register_signals(config=self)

