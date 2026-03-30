from rest_framework import viewsets, status
from rest_framework.decorators import action
from accounts.permissions import IsAuthenticated

from .models import Conversation, Message
from .serializers import ConversationListSerializer, MessageSerializer
from utils.api_response import success_response, error_response

class ConversationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # On récupère les conversations et on trie par la plus récente mise à jour
        return Conversation.objects.filter(participants=self.request.user).order_by('-updated_at')

    def get_serializer_class(self):
        if self.action == 'list':
            return ConversationListSerializer
        return MessageSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # CRUCIAL : On ajoute context={'request': request} pour le calcul des messages non lus
        serializer = ConversationListSerializer(queryset, many=True, context={'request': request})
        return success_response(
            message="Liste des conversations récupérée avec succès",
            body=serializer.data
        )

    def retrieve(self, request, *args, **kwargs):
        """
        GET /api/chat/conversations/{id}/
        Récupère l'historique d'UNE personne et marque comme LU.
        """
        try:
            instance = self.get_object()

            # LOGIQUE DE LECTURE : Marquer les messages reçus comme lus
            instance.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

            # Récupération de l'historique trié
            messages = instance.messages.all().order_by('created_at')
            serializer = MessageSerializer(messages, many=True, context={'request': request})

            return success_response(
                message="Historique récupéré et messages marqués comme lus",
                body=serializer.data
            )
        except Exception:
            return error_response("Discussion introuvable ou accès refusé", code=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], url_path='send-message')
    def send_message(self, request):
        product_id = request.data.get('product_id')
        receiver_id = request.data.get('receiver_id')
        content = request.data.get('content')

        if not all([product_id, receiver_id, content]):
            return error_response("Champs manquants : product_id, receiver_id et content sont requis")

        try:
            # Recherche d'une conversation existante entre ces deux personnes pour ce produit
            conversation = Conversation.objects.filter(
                product_id=product_id,
                participants=request.user
            ).filter(participants=receiver_id).first()

            # Création si premier contact
            if not conversation:
                conversation = Conversation.objects.create(product_id=product_id)
                conversation.participants.add(request.user, receiver_id)

            # Création du message
            message = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )

            serializer = MessageSerializer(message, context={'request': request})

            return success_response(
                message="Message envoyé avec succès",
                body=serializer.data,
                code=status.HTTP_201_CREATED
            )

        except Exception as e:
            return error_response(f"Erreur lors de l'envoi : {str(e)}")