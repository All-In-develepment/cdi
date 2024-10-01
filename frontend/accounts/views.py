from django.shortcuts import get_object_or_404, render
import requests
from django.shortcuts import render, redirect
from django.contrib import messages

from django.http import JsonResponse






from .models import Mercado, Usuario
from django.contrib.auth.decorators import login_required  # Verifica se o usuário está autenticado
import json
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from django.contrib.auth.views import LoginView



# Definindo o decorator token_required
def token_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        token = request.session.get('token')
        # print(token)
        if not token:
            return redirect('login')  # Redireciona para a página de login se não houver token

        # Aqui você pode validar o token com a API Flask, se necessário
        response = requests.get('http://api:5000/protected', headers = {'Authorization': f'Bearer {token}'})
        # print(response.json)
        if response.status_code != 200:
            return redirect('login')  # Redireciona para a página de login se o token for inválido

        return view_func(request, *args, **kwargs)
    return _wrapped_view





class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = 'signup.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('login')



def custom_login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        # Faz a requisição para a API Flask de autenticação
        try:
            response = requests.post('http://api:5000/login', json={
                'email': email,
                'senha': senha
            })

            if response.status_code == 200:
                # Recebe o token e o usuario_id da API
                data = response.json()
                token = data['token']
                usuario_id = data['usuario_id']

                # Armazena o token e o usuario_id na sessão
                request.session['token'] = token
                request.session['usuario_id'] = usuario_id

                # Redireciona para a página de criação de mercado
                return redirect(reverse_lazy('listar_mercados'))
            else:
                # Em caso de falha na autenticação, exibe mensagem de erro
                messages.error(request, response.json().get('error', 'Erro ao fazer login.'))
        
        except requests.exceptions.RequestException as e:
            # Lida com erros de conexão ou outros problemas com a requisição
            messages.error(request, f"Erro ao conectar com o servidor: {str(e)}")

    return render(request, 'registration/loginpage.html')


# view para lidar com o login.

# def login_view(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         senha = request.POST.get('senha')

#         # Fazer a requisição para a API
#         response = requests.post('http://api:5000/login', json={
#             'email': email,
#             'senha': senha
#         })

#         if response.status_code == 200:
#             # Se a autenticação for bem-sucedida, armazenar o token na sessão
#             data = response.json()
#             token = data.get('token')
#             usuario_id = data.get('usuario')

#             # Armazenar o token e o usuario_id na sessão
#             request.session['token'] = token
#             request.session['usuario_id'] = usuario_id
#             print(Usuario)
#             # Redirecionar para a página inicial
#             return redirect('home')  # Altere para o nome da sua view inicial
#         else:
#             messages.error(request, response.json().get('error', 'Erro ao fazer login.'))

#     return render(request, 'login.html')

def authenticate_user(email, senha):
    # Fazer a requisição para a API de autenticação
    response = requests.post('http://api:5000/login', json={
        'email': email,
        'senha': senha
    })
   
    if response.status_code == 200:
    
        # Se a autenticação for bem-sucedida, retorna o token
        return True, response.json().get('token')
    else:
        # Caso contrário, retorna False e a mensagem de erro
        return False, response.json().get('error', 'Erro ao fazer login.')


# view para lidar com criação de mercados .
# @login_required

@token_required
def criar_mercado(request):
    token = request.session.get('token')

    if not token:
        messages.error(request, "Autenticação necessária. Faça login para continuar.")
        return redirect('custom_login_view')

    headers = {
        'Authorization': f'Bearer {token}'
    }

    if request.method == 'POST':
        nome = request.POST.get('nome')
        usuario_id = request.session.get('usuario_id')

        if not nome or not usuario_id:
            return JsonResponse({"error": "O campo nome é obrigatório."}, status=400)

        # Interagir com a API Flask
        url = 'http://api:5000/mercados'
        data = {
            'nome': nome,
            'usuario_id': usuario_id
        }

        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 201:
            return redirect('listar_mercados')
        else:
            return JsonResponse(response.json(), status=response.status_code)

    return render(request, 'mercado_form.html')







def custom_logout_view(request):
    # Remove o token da sessão
    if 'token' in request.session:
        del request.session['token']
        messages.success(request, "Logout realizado com sucesso.")
    else:
        messages.warning(request, "Você não estava logado.")

    # Redireciona para a página de login ou para outra página
    return redirect('login')



@token_required  
def listar_mercados(request):
        # Verifica se o token está armazenado na sessão
        token = request.session.get('token')
        
        if not token:
            # Se o token não estiver presente, redireciona para a página de login
            messages.error(request, "Autenticação necessária. Faça login para continuar.")
            return redirect('custom_login_view')

        # Cabeçalhos com o token de autenticação
        headers = {
            'Authorization': f'Bearer {token}'
        }
        
        usuario_id = request.session.get('usuario_id')
        # if not usuario_id:
        #     messages.error(request, "id não foi na sessão boy.")
        #     return redirect('criar_mercado')

        # Faz a requisição GET para o backend Flask
        try:
            response = requests.get(f'http://api:5000/mercado/usuario/{usuario_id}', headers=headers)

            if response.status_code == 200:
                data = response.json()
                if 'message' in data:
                    # Se não houver mercados cadastrados
                    return render(request, 'listar_mercados.html', {'message': data['message']})
                else:
                    # Se houver mercados, exibe a lista
                    return render(request, 'listar_mercados.html', {'mercados': data})

            # Tratar caso haja erro na requisição
            return JsonResponse({"error": "Erro ao buscar os mercados"}, status=response.status_code)

        except requests.exceptions.RequestException as e:
            # Lidar com erro de conexão ou outros problemas na requisição
            return JsonResponse({"error": f"Erro ao conectar com o backend: {str(e)}"}, status=500)









@token_required 
def criar_transacao(request):
    token = request.session.get('token')
    
    if not token:
        messages.error(request, "Autenticação necessária. Faça login para continuar.")
        return redirect('custom_login_view')

    headers = {
        'Authorization': f'Bearer {token}'
    }

    if request.method == 'POST':
        valor = request.POST.get('valor')
        tipo = request.POST.get('tipo')
        odd = request.POST.get('odd', None)  # Campo opcional para odds
        # total = request.POST.get('total', None)  # Campo opcional para total ganho/perda

        usuario_id = request.session.get('usuario_id')

        if not valor or not tipo or not usuario_id:
            return JsonResponse({"error": "Todos os campos (valor, tipo) são obrigatórios."}, status=400)

        # Ajuste os dados conforme o tipo de transação
        if tipo == 'green' and not odd:
            return JsonResponse({"error": "Campo 'odd' é obrigatório para transações do tipo green."}, status=400)
        
        # Interagir com a API Flask
        url = 'http://api:5000/transacoes'
        data = {
            'valor': valor,
            'tipo': tipo,
            'odd': odd,
            'usuario_id': usuario_id
        }
        
        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 201:
            return redirect('listar_transacoes')
        else:
            return JsonResponse(response.json(), status=response.status_code)

    return render(request, 'criar_transacao.html')





# view para lidar com as transações

@token_required  
def listar_transacoes(request):
    token = request.session.get('token')
    if not token:
        messages.error(request, "Autenticação necessária. Faça login para continuar.")
        return redirect('custom_login_view')

    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    usuario_id = request.session.get('usuario_id')
    try:
        response = requests.get(f'http://api:5000/transacao/usuario/{usuario_id}', headers=headers)

        if response.status_code == 200:
            data = response.json()

            if 'message' in data:
                return render(request, 'listar_transacoes.html', {'message': data['message']})

            # Calcular a soma total
            soma_total = 0
            for transacao in data['transacoes']:
                tipo = transacao.get('tipo')
                valor = float(transacao.get('valor', 0))

                if tipo == 'green' and transacao.get('total') not in [None, '']:
                    # Green: somar o valor total (valor * odd)
                    soma_total += float(transacao['total'])
                elif tipo == 'red':
                    # Red: subtrair o valor da transação
                    soma_total -= valor
                elif tipo == 'aporte':
                    # Aporte: somar o valor da transação
                    soma_total += valor
                elif tipo == 'retirada':
                    # Retirada: subtrair o valor da transação
                    soma_total -= valor

            # Passar a lista de transações corretamente
            return render(request, 'listar_transacoes.html', {'transacoes': data['transacoes'], 'soma_total': soma_total})

        return JsonResponse({"error": "Erro ao buscar as transações"}, status=response.status_code)

    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": f"Erro ao conectar com o backend: {str(e)}"}, status=500)






# views para editar mercado 


@token_required  
def editar_mercado(request, id):
    token = request.session.get('token')
    
    if not token:
        messages.error(request, "Autenticação necessária. Faça login para continuar.")
        return redirect('custom_login_view')

    headers = {
        'Authorization': f'Bearer {token}'
    }

    # Buscar os dados do mercado atual para exibição no formulário
    url_get = f'http://api:5000/mercado/{id}'  # URL para buscar mercado pelo ID
    response_get = requests.get(url_get, headers=headers)
    
    if response_get.status_code != 200:
        messages.error(request, "Erro ao buscar informações do mercado.")
        return redirect('listar_mercados')

    mercado = response_get.json().get('mercado')

    if request.method == 'POST':
        nome = request.POST.get('nome')

        # Preparar os dados para enviar para a API Flask
        data = {'nome': nome}

        # Atualizar o mercado via API Flask
        url = f'http://api:5000/mercado/{id}'  # Atualizando o mercado pelo ID
        response = requests.put(url, json=data, headers=headers)

        if response.status_code == 200:
            messages.success(request, "Mercado atualizado com sucesso.")
            return redirect('listar_mercados')
        else:
            messages.error(request, "Erro ao atualizar o mercado.")
            return redirect('editar_mercado', id=id)

    return render(request, 'editar_mercado.html', {'mercado': mercado})







