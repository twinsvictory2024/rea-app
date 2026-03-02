from rest_framework.permissions import IsAuthenticated
from rea_common.views import BaseModelViewSet
from .serializers.contact import ContactSerializer
from .permissions import IsContactOwner
from .models import Contact


class ContactViewSet(BaseModelViewSet):
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated, IsContactOwner]

    def get_queryset(self):
        user = self.request.user
        return Contact.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)