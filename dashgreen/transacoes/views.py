from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from contas.models import Mercado
from .models import Transacao
from django import forms

# Create your views here.
class TransacaoListView(LoginRequiredMixin, ListView):
    model = Transacao
    template_name = 'transacoes/transacao_list.html'

    def get_queryset(self):
        # Retorna apenas as transações do usuário autenticado
        return Transacao.objects.filter(usuario=self.request.user)

class TransacaoCreateView(LoginRequiredMixin, CreateView):
    model = Transacao
    template_name = 'transacoes/transacao_form.html'
    fields = ['valor', 'tipo', 'mercado', 'resultado', 'odd']
    widgets = {
        'valor': forms.NumberInput(attrs={'class': 'form-control input-group input-group-lg'}),
        'mercado': forms.Select(attrs={'class': 'form-control input-group input-group-lg'}),
        'tipo': forms.Select(attrs={'class': 'form-control input-group input-group-lg'}),
        'resultado': forms.Select(attrs={'class': 'form-control input-group input-group-lg'}),
        'odd': forms.NumberInput(attrs={'class': 'form-control input-group input-group-lg'}),
    }
    success_url = reverse_lazy('transacao-list')
    
    def get_form(self, *args, **kwargs):
        form = super(TransacaoCreateView, self).get_form(*args, **kwargs)
        # Filtra os mercados pelo usuário autenticado
        form.fields['mercado'].queryset = Mercado.objects.filter(usuario=self.request.user)
        return form

    def form_valid(self, form):
        # Define o usuário como o criador da transação
        form.instance.usuario = self.request.user
        return super().form_valid(form)

class TransacaoUpdateView(LoginRequiredMixin, UpdateView):
    model = Transacao
    template_name = 'transacoes/transacao_form.html'
    fields = ['valor', 'tipo', 'mercado', 'resultado', 'odd']
    widgets = {
        'valor': forms.NumberInput(attrs={'class': 'form-control input-group input-group-lg'}),
        'mercado': forms.Select(attrs={'class': 'form-control input-group input-group-lg'}),
        'tipo': forms.Select(attrs={'class': 'form-control input-group input-group-lg'}),
        'resultado': forms.Select(attrs={'class': 'form-control input-group input-group-lg'}),
        'odd': forms.NumberInput(attrs={'class': 'form-control input-group input-group-lg'}),
    }
    success_url = reverse_lazy('transacao-list')
    
    def get_form(self, *args, **kwargs):
        form = super(TransacaoUpdateView, self).get_form(*args, **kwargs)
        # Filtra os mercados pelo usuário autenticado
        form.fields['mercado'].queryset = Mercado.objects.filter(usuario=self.request.user)
        return form

    def get_queryset(self):
        # Garantir que o usuário só possa editar suas próprias transações
        return Transacao.objects.filter(usuario=self.request.user)


class TransacaoDeleteView(LoginRequiredMixin, DeleteView):
    model = Transacao
    template_name = 'transacoes/transacao_confirm_delete.html'
    success_url = reverse_lazy('transacao-list')

    def get_queryset(self):
        # Garantir que o usuário só possa deletar suas próprias transações
        return Transacao.objects.filter(usuario=self.request.user)

