from django.apps import AppConfig

class ChatConfig(AppConfig):
    name = 'chat'
class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat' # Assure-toi que c'est le bon nom

    def ready(self):
        # On importe les signaux au moment où l'application est prête
        import chat.signal