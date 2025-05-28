from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Usuario
from django.shortcuts import redirect, get_object_or_404
from hashlib import sha256
from django.contrib import messages
from plataforma.services import validate_email, enviar_email_verificacao
from django.urls import reverse

def login(request):
    status = request.GET.get('status')
    return render(request, 'login.html', {'status': status})

def cadastro(request):
    status = request.GET.get('status')
    return render(request, 'cadastro.html', {'status': status})

def valida_cadastro(request):
    nome = request.POST.get('nome')
    email = request.POST.get('email')
    senha = request.POST.get('senha')
    
    if len(nome.strip()) == 0 or len(email.strip()) == 0:
        return redirect('/auth/cadastro/?status=1')
    
    if len(senha) < 8:
        return redirect('/auth/cadastro/?status=2')

    # Verifica se o email já existe
    if Usuario.objects.filter(email=email).exists():
        return redirect('/auth/cadastro/?status=3')
    
    # Valida o email usando a API
    if not validate_email(email):
        messages.error(request, 'Email inválido ou temporário. Por favor, use um email válido.')
        return redirect('/auth/cadastro/?status=5')
    
    try:
        senha = sha256(senha.encode()).hexdigest()
        usuario = Usuario(nome=nome, senha=senha, email=email)
        usuario.save()
        
        # Gera e envia código de verificação
        codigo = usuario.gerar_codigo_verificacao()
        if enviar_email_verificacao(email, nome, codigo):
            request.session['email_verificacao'] = email
            messages.success(request, 'Cadastro realizado! Por favor, verifique seu email.')
            return redirect('usuarios:verificar_email')
        else:
            messages.error(request, 'Erro ao enviar email de verificação. Tente novamente.')
            usuario.delete()
            return redirect('/auth/cadastro/?status=4')
            
    except Exception as e:
        print(f"Erro no cadastro: {e}")
        return redirect('/auth/cadastro/?status=4')

def valida_login(request):
    email = request.POST.get('email')
    senha = request.POST.get('senha')
    senha = sha256(senha.encode()).hexdigest()

    usuario = Usuario.objects.filter(email=email).filter(senha=senha).first()

    if not usuario:
        return redirect('/auth/login/?status=1')
    
    if not usuario.email_verificado:
        messages.error(request, 'Por favor, verifique seu email antes de fazer login.')
        request.session['email_verificacao'] = email
        return redirect('usuarios:verificar_email')
    
    request.session['logado'] = True
    request.session['usuario_id'] = usuario.id
    return redirect('/plataforma/home')

def verificar_email(request):
    email = request.session.get('email_verificacao')
    if not email:
        return redirect('usuarios:login')
    return render(request, 'verificar_email.html', {'email': email})

def verificar_codigo(request):
    if request.method == 'POST':
        email = request.session.get('email_verificacao')
        if not email:
            return redirect('usuarios:login')
        
        codigo = request.POST.get('codigo')
        usuario = get_object_or_404(Usuario, email=email)
        
        if usuario.verificar_codigo(codigo):
            messages.success(request, 'Email verificado com sucesso! Você já pode fazer login.')
            del request.session['email_verificacao']
            return redirect('usuarios:login')
        else:
            messages.error(request, 'Código inválido ou expirado. Tente novamente.')
            return redirect('usuarios:verificar_email')
    return redirect('usuarios:verificar_email')

def reenviar_codigo(request):
    if request.method == 'POST':
        email = request.session.get('email_verificacao')
        if not email:
            return redirect('usuarios:login')
        
        usuario = get_object_or_404(Usuario, email=email)
        codigo = usuario.gerar_codigo_verificacao()
        
        if enviar_email_verificacao(email, usuario.nome, codigo):
            messages.success(request, 'Novo código enviado! Verifique seu email.')
        else:
            messages.error(request, 'Erro ao enviar código. Tente novamente.')
    
    return redirect('usuarios:verificar_email')

def sair(request):
    request.session.flush()
    return redirect('/auth/login/')

def perfil_usuario(request):
    if request.session.get('usuario_id'):
        usuario = Usuario.objects.get(id=request.session['usuario_id'])
        
        # Obtém informações do clima se a cidade estiver definida
        clima = None
        if usuario.cidade:
            from plataforma.services import get_weather
            clima = get_weather(usuario.cidade)
        
        # Calcula pontos e nível
        from plataforma.services import calculate_eco_points
        info_pontos = calculate_eco_points(usuario.atividades or {})
        usuario.pontos_eco = info_pontos['pontos']
        usuario.nivel = info_pontos['nivel']
        usuario.save()
        
        # Obtém notícias ambientais
        from plataforma.services import get_environmental_news
        noticias = get_environmental_news()
        
        context = {
            'usuario': usuario,
            'clima': clima,
            'info_pontos': info_pontos,
            'noticias': noticias[:3]  # Limita a 3 notícias
        }
        
        return render(request, 'usuario.html', context)
    return redirect('/auth/login/?status=2')

def atualizar_foto(request):
    if request.method == 'POST' and request.FILES.get('foto'):
        usuario = Usuario.objects.get(id=request.session['usuario_id'])
        usuario.foto = request.FILES['foto']
        usuario.save()
        messages.success(request, 'Foto de perfil atualizada com sucesso!')
    return redirect('usuarios:usuario')

def atualizar_perfil(request):
    if request.method == 'POST':
        usuario = Usuario.objects.get(id=request.session['usuario_id'])
        
        # Verifica se o email já existe para outro usuário
        email = request.POST['email']
        if Usuario.objects.filter(email=email).exclude(id=usuario.id).exists():
            messages.error(request, 'Este email já está em uso.')
            return redirect('usuarios:usuario')
        
        usuario.nome = request.POST['nome']
        usuario.email = email
        
        # Atualiza a senha se fornecida
        nova_senha = request.POST.get('nova_senha')
        if nova_senha:
            usuario.senha = sha256(nova_senha.encode()).hexdigest()
        
        usuario.save()
        messages.success(request, 'Perfil atualizado com sucesso!')
    return redirect('usuarios:usuario')

def excluir_conta(request):
    if request.method == 'POST':
        usuario = Usuario.objects.get(id=request.session['usuario_id'])
        usuario.delete()
        del request.session['usuario_id']
        messages.success(request, 'Sua conta foi excluída com sucesso.')
        return redirect('usuarios:login')
    return redirect('usuarios:usuario')

def atualizar_cidade(request):
    if request.method == 'POST':
        usuario = Usuario.objects.get(id=request.session['usuario_id'])
        usuario.cidade = request.POST.get('cidade')
        usuario.save()
        messages.success(request, 'Cidade atualizada com sucesso!')
    return redirect('usuarios:usuario')

def registrar_atividade(request):
    if request.method == 'POST':
        usuario = Usuario.objects.get(id=request.session['usuario_id'])
        tipo = request.POST.get('tipo')
        quantidade = int(request.POST.get('quantidade', 1))
        
        usuario.adicionar_atividade(tipo, quantidade)
        
        # Recalcula pontos e nível
        from plataforma.services import calculate_eco_points
        info_pontos = calculate_eco_points(usuario.atividades)
        usuario.pontos_eco = info_pontos['pontos']
        usuario.nivel = info_pontos['nivel']
        usuario.save()
        
        messages.success(request, f'Atividade registrada com sucesso! Você ganhou pontos!')
    return redirect('usuarios:usuario')