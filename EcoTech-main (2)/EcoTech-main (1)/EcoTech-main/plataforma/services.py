import requests
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from django.conf import settings
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

def get_weather(city):
    """
    Obtém informações do clima para uma cidade usando a API OpenWeatherMap
    """
    api_key = os.getenv('OPENWEATHER_API_KEY', '')
    if not api_key:
        return None
    
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric',
        'lang': 'pt_br'
    }
    
    try:
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            weather_info = {
                'temperatura': round(data['main']['temp']),
                'descricao': data['weather'][0]['description'].capitalize(),
                'umidade': data['main']['humidity'],
                'icone': f"http://openweathermap.org/img/w/{data['weather'][0]['icon']}.png"
            }
            return weather_info
    except Exception as e:
        print(f"Erro ao obter dados do clima: {e}")
    return None

def find_nearby_collection_points(latitude, longitude, max_distance=10):
    """
    Encontra pontos de coleta próximos usando geolocalização
    """
    # Exemplo de pontos de coleta (em produção, isso viria do banco de dados)
    collection_points = [
        {
            'name': 'EcoPonto Central',
            'latitude': -23.550520,
            'longitude': -46.633308,
            'tipos': ['Eletrônicos', 'Pilhas', 'Baterias']
        },
        {
            'name': 'Recicla Mais',
            'latitude': -23.557820,
            'longitude': -46.639408,
            'tipos': ['Papel', 'Plástico', 'Metal']
        },
        # Adicione mais pontos conforme necessário
    ]
    
    user_location = (latitude, longitude)
    nearby_points = []
    
    for point in collection_points:
        point_location = (point['latitude'], point['longitude'])
        distance = geodesic(user_location, point_location).kilometers
        
        if distance <= max_distance:
            point['distance'] = round(distance, 2)
            nearby_points.append(point)
    
    return sorted(nearby_points, key=lambda x: x['distance'])

def get_environmental_news():
    """
    Obtém notícias sobre meio ambiente e sustentabilidade
    """
    # Em produção, você usaria uma API de notícias real
    return [
        {
            'titulo': 'Nova tecnologia de reciclagem revoluciona tratamento de plástico',
            'descricao': 'Cientistas desenvolvem método inovador que permite reciclar plástico infinitamente.',
            'data': '2025-05-28',
            'fonte': 'EcoNews'
        },
        {
            'titulo': 'Brasil aumenta índice de reciclagem em 15%',
            'descricao': 'País atinge marca histórica na reciclagem de resíduos sólidos.',
            'data': '2025-05-27',
            'fonte': 'Sustentabilidade Hoje'
        },
        {
            'titulo': 'Startup cria programa de recompensas para reciclagem',
            'descricao': 'Empresa inova ao oferecer benefícios para quem recicla corretamente.',
            'data': '2025-05-26',
            'fonte': 'Tech & Ambiente'
        }
    ]

def calculate_eco_points(user_activities):
    """
    Calcula pontos de sustentabilidade baseado nas atividades do usuário
    """
    points_table = {
        'reciclagem_papel': 5,
        'reciclagem_plastico': 5,
        'reciclagem_vidro': 8,
        'reciclagem_metal': 10,
        'reciclagem_eletronico': 15,
        'compostagem': 20,
        'economia_agua': 25,
        'energia_renovavel': 30
    }
    
    total_points = 0
    for activity, quantity in user_activities.items():
        if activity in points_table:
            total_points += points_table[activity] * quantity
    
    # Calcula nível baseado nos pontos
    levels = {
        0: 'Iniciante',
        100: 'Bronze',
        500: 'Prata',
        1000: 'Ouro',
        2000: 'Platina',
        5000: 'Diamante'
    }
    
    current_level = 'Iniciante'
    for points, level in sorted(levels.items()):
        if total_points >= points:
            current_level = level
        else:
            break
    
    return {
        'pontos': total_points,
        'nivel': current_level,
        'proximo_nivel': next((level for points, level in sorted(levels.items()) 
                             if points > total_points), 'Máximo'),
        'pontos_proximo_nivel': next((points for points in sorted(levels.keys()) 
                                    if points > total_points), total_points) - total_points
    }

def validate_email(email):
    """
    Valida um email usando a API do Abstract
    Documentação: https://www.abstractapi.com/email-verification-validation-api
    """
    api_key = os.getenv('ABSTRACT_API_KEY', '')
    if not api_key:
        return True  # Retorna True se não tiver API key configurada
    
    url = f"https://emailvalidation.abstractapi.com/v1/?api_key={api_key}&email={email}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            
            # Verifica vários aspectos do email
            is_valid_format = data.get('is_valid_format', {}).get('value', True)
            is_disposable = data.get('is_disposable', False)
            is_webmail = data.get('is_webmail', True)
            is_deliverable = data.get('is_smtp_valid', {}).get('value', True)
            
            # Retorna True apenas se o email passar em todas as verificações
            return (is_valid_format and 
                   not is_disposable and 
                   (is_webmail or is_deliverable))
            
    except Exception as e:
        print(f"Erro ao validar email: {e}")
        return True  # Em caso de erro, permite o cadastro
    
    return True 

def enviar_email_verificacao(email, nome, codigo):
    """
    Envia email de verificação usando SMTP do Gmail
    """
    # Configurações do email
    remetente = os.getenv('EMAIL_USER', '').strip()
    senha = os.getenv('EMAIL_PASSWORD', '').strip()
    
    if not remetente or not senha:
        print("Credenciais de email não configuradas")
        return False
    
    print(f"Tentando enviar email para {email} usando {remetente}")
    
    # Cria a mensagem
    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = email
    msg['Subject'] = 'Verificação de Email - EcoTech'
    
    # Corpo do email em HTML
    corpo_email = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #2b7a3d;">Olá {nome}!</h2>
            <p>Bem-vindo(a) ao EcoTech! Para completar seu cadastro, por favor confirme seu email.</p>
            <p>Seu código de verificação é:</p>
            <div style="background-color: #f5f5f5; padding: 15px; text-align: center; margin: 20px 0;">
                <h1 style="color: #2b7a3d; font-size: 32px; letter-spacing: 5px;">{codigo}</h1>
            </div>
            <p>Este código expira em 30 minutos.</p>
            <p style="color: #666; font-size: 14px;">Se você não se cadastrou no EcoTech, por favor ignore este email.</p>
        </div>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(corpo_email, 'html'))
    
    try:
        # Conecta ao servidor SMTP do Gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        print("Conectado ao servidor SMTP")
        
        # Remove espaços da senha
        senha = ''.join(senha.split())
        server.login(remetente, senha)
        print("Login realizado com sucesso")
        
        # Envia o email
        server.send_message(msg)
        print("Email enviado com sucesso")
        server.quit()
        return True
    except Exception as e:
        print(f"Erro detalhado ao enviar email: {str(e)}")
        return False 