from django.db.models import Q
from django.views.generic import View
from django.http import Http404
from django.shortcuts import render, redirect, reverse
from users import models as user_models
from . import models, forms

# Create your views here.


def go_conversations(request, host_pk, guest_pk):
    try:
        user_one = user_models.User.objects.get(pk=host_pk)
        user_two = user_models.User.objects.get(pk=guest_pk)
    except user_models.User.DoesNotExist:
        return redirect(reverse("core:home"))

    if user_one is not None and user_two is not None:
        try:
            a = models.Conversation.objects.get(Q(participants=user_one))
            print(a)
            conversation = models.Conversation.objects.get(
                Q(participants=user_one), Q(participants=user_two)
            )
        except models.Conversation.DoesNotExist:
            conversation = models.Conversation.objects.create()
            conversation.participants.add(user_one, user_two)
        return redirect(reverse("conversations:detail", kwargs={"pk": conversation.pk}))


class ConversationDetailView(View):
    def get(self, *args, **kwargs):
        pk = kwargs.get("pk")
        converstaion = models.Conversation.objects.get_or_none(pk=pk)
        if not converstaion:
            raise Http404()
        return render(
            self.request,
            "conversations/conversation_detail.html",
            {"conversation": converstaion},
        )

    def post(self, *args, **kwargs):
        pk = kwargs.get("pk")
        message = self.request.POST.get("message", None)
        converstaion = models.Conversation.objects.get_or_none(pk=pk)
        if not converstaion:
            raise Http404()
        if message is not None:
            models.Message.objects.create(
                message=message, user=self.request.user, conversation=converstaion
            )
        return redirect(reverse("conversations:detail", kwargs={"pk": pk}))
