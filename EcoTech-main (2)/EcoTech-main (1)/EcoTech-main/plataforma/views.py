from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import logout
from .models import Doacao, Coleta

def home(request):
    if request.session.get('logado'):
        return render(request, 'home.html')
    else:
        return redirect('/auth/login/?status=2')

def sobre_view(request):
    return render(request, 'sobre.html')

def servicos_view(request):
    return render(request, 'servicos.html')

def cadastro_view(request):
    return render(request, 'cadastro.html')

def doar_view(request):
    # Redireciona para a página de doação
    return redirect('doacao')

def doacao_view(request):
    if request.method == "POST":
        try:
            doacao = Doacao(
                descricao=request.POST.get('descricao'),
                categoria=request.POST.get('categoria'),
                local=request.POST.get('local')
            )
            
            if 'foto' in request.FILES:
                doacao.foto = request.FILES['foto']
            
            doacao.save()
            return redirect('home')  # Redireciona para a página inicial após salvar
        except Exception as e:
            print(f"Erro ao salvar doação: {e}")
            return render(request, 'doacao.html', {'error': 'Erro ao salvar os dados.'})

    return render(request, 'doacao.html')

def coleta_view(request):
    if request.method == "POST":
        try:
            coleta = Coleta(
                quantidade=request.POST.get('quantidade'),
                tipo_material=request.POST.get('tipo_material'),
                endereco=request.POST.get('endereco'),
                data_preferencial=request.POST.get('data_preferencial'),
                observacoes=request.POST.get('observacoes', '')
            )
            
            coleta.save()
            return redirect('home')  # Redireciona para a página inicial após salvar
        except Exception as e:
            print(f"Erro ao salvar coleta: {e}")
            return render(request, 'coleta.html', {'error': 'Erro ao salvar os dados.'})

    return render(request, 'coleta.html')

def contato_view(request):
    return render(request, 'contato.html')

def logout_view(request):
    logout(request)
    return redirect('login')