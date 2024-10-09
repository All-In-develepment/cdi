from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Count, Sum

from transacoes.models import Transacao
from .models import Mercado
from django import forms


# Create your views here.

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redireciona para a página inicial após o login
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
    return render(request, 'contas/login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']
        if password == password_confirm:
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            return redirect('home')  # Redireciona para a página inicial após o registro
        else:
            messages.error(request, 'As senhas não coincidem.')
    return render(request, 'contas/register.html')

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('login')

@login_required
def home_view(request):
    # Retorna apenas as transações do usuário autenticado
    
    # lista todas as tranções do tipo aposta e soma os valores do campo retorno e e valor
    total_por_mercado = Transacao.objects.filter(usuario=request.user, tipo='Aposta').values('id','mercado__nome','resultado').annotate(total_valor=Sum('valor'), total_retorno=Sum('retorno'))
    listagem = Transacao.objects.filter(usuario=request.user, tipo='Aposta').values('mercado__nome', 'mercado__color').annotate(total=Count('id'))
    
    # Calcular o total geral de apostas
    total_apostas = len(total_por_mercado)
    
    # Dicionário para armazenar os resultados finais por mercado
    resultados_por_mercado = {}

    # Processar os dados para fazer a subtração de 'Red' de 'Green'
    for dado in total_por_mercado:
        mercado_nome = dado['mercado__nome']
        resultado = dado['resultado'].strip().lower()
        
        if mercado_nome not in resultados_por_mercado:
            resultados_por_mercado[mercado_nome] = {'contage_green': 0, 'contagen_red': 0, 'green_retorno': 0, 'red_valor': 0, 'percentual': 0}

        if resultado == 'green':
            resultados_por_mercado[mercado_nome]['green_retorno'] += dado['total_retorno']
            resultados_por_mercado[mercado_nome]['contage_green'] += 1
        
        elif resultado == 'red':
            resultados_por_mercado[mercado_nome]['red_valor'] += dado['total_valor']
            resultados_por_mercado[mercado_nome]['contagen_red'] += 1

        # Calcular a porcentagem de participação do mercado no volume total de apostas
        resultados_por_mercado[mercado_nome]['percentual'] = (
            sum([
                resultados_por_mercado[mercado_nome]['contage_green'], 
                resultados_por_mercado[mercado_nome]['contagen_red']
            ]) / total_apostas
        ) * 100
            
    # Agora calcule a subtração (green_retorno - red_valor) para cada mercado
    for mercado, valores in resultados_por_mercado.items():
        resultado_final = valores['green_retorno'] - valores['red_valor']
        print(f"Mercado: {mercado}, Quantidade green: {valores['contage_green']}, Qunatidade red: {valores['contagen_red']}")

    return render(request, 'contas/home.html', {'listagem': listagem, 'resultados_por_mercado': resultados_por_mercado.items()})

class MercadoListView(LoginRequiredMixin, ListView):
    model = Mercado
    template_name = 'mercados/mercado_list.html'
    def get_queryset(self):
        return Mercado.objects.filter(usuario=self.request.user)

class MercadoForm(forms.ModelForm):
    class Meta:
        model = Mercado
        fields = ['nome', 'color']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
        }

class MercadoCreateView(LoginRequiredMixin, CreateView, forms.ModelForm):
    model = Mercado
    form_class = MercadoForm
    template_name = 'mercados/mercado_form.html'
    success_url = reverse_lazy('mercado-list')
    
    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)

class MercadoUpdateView(LoginRequiredMixin, UpdateView):
    model = Mercado
    template_name = 'mercados/mercado_form.html'
    form_class = MercadoForm
    success_url = reverse_lazy('mercado-list')

    def get_queryset(self):
        # Garantir que o usuário só possa editar seus próprios mercados
        return Mercado.objects.filter(usuario=self.request.user)

class MercadoDeleteView(LoginRequiredMixin, DeleteView):
    model = Mercado
    template_name = 'mercados/mercado_confirm_delete.html'
    success_url = reverse_lazy('mercado-list')

    def get_queryset(self):
        # Garantir que o usuário só possa deletar seus próprios mercados
        return Mercado.objects.filter(usuario=self.request.user)

