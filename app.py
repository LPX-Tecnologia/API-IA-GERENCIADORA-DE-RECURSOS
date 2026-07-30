from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import requests
from datetime import datetime
import re

app = Flask(__name__)
CORS(app)

DB_FILE = 'ia_memoria.json'
APIS_FILE = 'apis_registradas.json'

# ==========================================================
# BANCO DE CONHECIMENTO DA IA
# ==========================================================

CONHECIMENTO = {
    "apis_disponiveis": {
        "usuarios": {"url": "https://clipador-api-usuarios.onrender.com", "porta": 5000, "descricao": "Cadastro, login, perfis"},
        "vagas": {"url": "https://clipador-api-vagas.onrender.com", "porta": 5001, "descricao": "CRUD de obras e vagas"},
        "chat": {"url": "https://clipador-api-chat.onrender.com", "porta": 5002, "descricao": "Mensagens em tempo real"},
        "notificacoes": {"url": "https://clipador-api-notificacoes.onrender.com", "porta": 5003, "descricao": "Push notifications"},
        "videos": {"url": "https://clipador-api-videos.onrender.com", "porta": 5004, "descricao": "Upload de vídeos"},
        "legendas": {"url": "https://clipador-api-legendas.onrender.com", "porta": 5005, "descricao": "Legendas animadas"},
        "tiktok": {"url": "https://clipador-api-tiktok.onrender.com", "porta": 5006, "descricao": "Postar no TikTok"},
        "youtube": {"url": "https://clipador-api-youtube.onrender.com", "porta": 5007, "descricao": "Postar no YouTube"},
        "pagamentos": {"url": "https://clipador-api-pagamentos.onrender.com", "porta": 5008, "descricao": "PIX, cartão, boleto"},
        "ia": {"url": "https://clipador-api-ia.onrender.com", "porta": 5009, "descricao": "Chatbot, hashtags"},
        "youtube_dl": {"url": "https://clipador-api-youtube-download.onrender.com", "porta": 5010, "descricao": "Download de vídeos"},
        "localizacao": {"url": "https://clipador-api-localizacao.onrender.com", "porta": 5011, "descricao": "Geolocalização"},
        "email": {"url": "https://clipador-api-email.onrender.com", "porta": 5012, "descricao": "Disparo de emails"},
        "mensagens": {"url": "https://clipador-api-mensagens.onrender.com", "porta": 5013, "descricao": "WhatsApp, Telegram, SMS"},
        "edicao_video": {"url": "https://clipador-api-edicao-video.onrender.com", "porta": 5014, "descricao": "Edição de vídeo profissional"},
        "edicao_imagem": {"url": "https://clipador-api-edicao-imagem.onrender.com", "porta": 5015, "descricao": "Edição de imagens"},
        "edicao_audio": {"url": "https://clipador-api-edicao-audio.onrender.com", "porta": 5016, "descricao": "Edição de áudio"},
        "sorteios": {"url": "https://clipador-api-sorteios.onrender.com", "porta": 5017, "descricao": "Sorteios e torneios"},
        "rastreamento": {"url": "https://clipador-api-rastreamento.onrender.com", "porta": 5018, "descricao": "Localização de pessoas"}
    },
    
    "padroes_problemas": {
        "video": ["vídeo", "video", "filmagem", "gravação", "youtube", "tiktok", "reels", "shorts"],
        "imagem": ["imagem", "foto", "picture", "png", "jpg", "thumbnail", "selfie"],
        "audio": ["áudio", "audio", "música", "musica", "som", "mp3", "podcast", "voz"],
        "mensagem": ["mensagem", "whatsapp", "telegram", "sms", "email", "notificação"],
        "localizacao": ["localização", "mapa", "gps", "endereço", "rota", "perto", "próximo"],
        "sorteio": ["sorteio", "rifa", "prêmio", "torneio", "campeonato", "competição"],
        "pagamento": ["pagamento", "pix", "dinheiro", "cobrar", "valor", "preço"],
        "usuario": ["usuário", "login", "cadastro", "perfil", "conta", "senha"]
    },
    
    "solucoes_prontas": {
        "criar_app_completo": """
Para criar um app completo, use estas APIs:
1. usuarios - para login/cadastro
2. vagas - para publicar/conteúdo
3. chat - para mensagens
4. notificacoes - para push
5. localizacao - para mapa/GPS
Todas já estão prontas e documentadas!
""",
        "editar_video_para_rede_social": """
Para editar vídeo para rede social:
1. Use a API 'youtube_dl' para baixar o vídeo
2. Use a API 'edicao_video' para cortar, redimensionar e adicionar legendas
3. Use a API 'tiktok' ou 'youtube' para postar
""",
        "criar_sorteio": """
Para criar um sorteio completo:
1. Use a API 'sorteios' para criar rifa ou sorteio
2. Use a API 'email' para notificar ganhadores
3. Use a API 'mensagens' para enviar WhatsApp
4. Use a API 'notificacoes' para push
""",
        "sistema_rastreamento": """
Para sistema de rastreamento:
1. Use a API 'rastreamento' para localização em tempo real
2. Use a API 'notificacoes' para alertas
3. Use a API 'mensagens' para emergência
4. Use a API 'localizacao' para geolocalização
"""
    }
}

def carregar(arquivo):
    if os.path.exists(arquivo):
        with open(arquivo, 'r') as f:
            return json.load(f)
    return []

def salvar(arquivo, dados):
    with open(arquivo, 'w') as f:
        json.dump(dados, f, indent=2)

def identificar_problema(texto):
    """Identifica qual API resolve o problema"""
    texto = texto.lower()
    matches = {}
    
    for categoria, palavras in CONHECIMENTO['padroes_problemas'].items():
        pontos = sum(1 for p in palavras if p in texto)
        if pontos > 0:
            matches[categoria] = pontos
    
    return sorted(matches.items(), key=lambda x: x[1], reverse=True)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "api": "Clipador - IA Gerenciadora",
        "versao": "3.0.0",
        "descricao": "IA que gerencia todas as APIs e encontra soluções",
        "capacidades": [
            "entender_problemas", "sugerir_solucoes",
            "combinar_apis", "criar_novos_recursos",
            "aprender_padroes", "otimizar_processos"
        ]
    })

@app.route('/api/ia/gerenciadora/pensar', methods=['POST'])
def pensar():
    """IA analisa o problema e sugere solução"""
    data = request.json
    problema = data.get('problema', '')
    contexto = data.get('contexto', {})
    
    if not problema:
        return jsonify({"erro": "Descreva o problema"}), 400
    
    # 1. Identifica padrões
    categorias = identificar_problema(problema)
    
    # 2. Busca APIs relevantes
    apis_sugeridas = []
    for cat, score in categorias[:3]:
        for nome, info in CONHECIMENTO['apis_disponiveis'].items():
            if cat in nome.lower() or cat in info['descricao'].lower():
                apis_sugeridas.append({
                    "api": nome,
                    "url": info['url'],
                    "descricao": info['descricao'],
                    "relevancia": score
                })
    
    # 3. Busca soluções prontas
    solucoes_encontradas = []
    for chave, solucao in CONHECIMENTO['solucoes_prontas'].items():
        if any(p in problema.lower() for p in chave.split('_')):
            solucoes_encontradas.append({"tipo": chave, "solucao": solucao.strip()})
    
    # 4. Gera plano de ação
    plano = gerar_plano_acao(problema, apis_sugeridas, contexto)
    
    # 5. Aprende com a interação
    memoria = carregar(DB_FILE)
    memoria.append({
        "problema": problema,
        "categorias": [c[0] for c in categorias],
        "apis_sugeridas": [a['api'] for a in apis_sugeridas],
        "timestamp": str(datetime.now())
    })
    salvar(DB_FILE, memoria)
    
    return jsonify({
        "analise": {
            "problema": problema,
            "categorias_detectadas": [{"categoria": c[0], "confianca": c[1]} for c in categorias]
        },
        "apis_recomendadas": apis_sugeridas[:5],
        "solucoes_prontas": solucoes_encontradas,
        "plano_acao": plano,
        "proximo_passo": plano[0] if plano else "Descreva mais detalhes do problema"
    })

@app.route('/api/ia/gerenciadora/executar', methods=['POST'])
def executar():
    """IA executa uma ação usando as APIs"""
    data = request.json
    api_nome = data.get('api')
    acao = data.get('acao')
    parametros = data.get('parametros', {})
    
    api_info = CONHECIMENTO['apis_disponiveis'].get(api_nome)
    if not api_info:
        return jsonify({"erro": f"API '{api_nome}' não encontrada"}), 404
    
    try:
        url = f"{api_info['url']}/api/{api_nome}/{acao}"
        response = requests.post(url, json=parametros, timeout=30)
        return jsonify({
            "api": api_nome,
            "acao": acao,
            "resultado": response.json()
        })
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/api/ia/gerenciadora/combinar', methods=['POST'])
def combinar_apis():
    """IA combina múltiplas APIs para resolver problema complexo"""
    data = request.json
    objetivo = data.get('objetivo', '')
    apis_necessarias = data.get('apis', [])
    
    fluxo = {
        "objetivo": objetivo,
        "passos": []
    }
    
    passo = 1
    for api_nome in apis_necessarias:
        api_info = CONHECIMENTO['apis_disponiveis'].get(api_nome)
        if api_info:
            fluxo['passos'].append({
                "passo": passo,
                "api": api_nome,
                "url": api_info['url'],
                "descricao": api_info['descricao'],
                "acao": f"Usar {api_nome} para processar"
            })
            passo += 1
    
    fluxo['total_passos'] = passo - 1
    fluxo['estimativa_tempo'] = f"{passo * 2} segundos"
    
    return jsonify(fluxo)

@app.route('/api/ia/gerenciadora/aprender', methods=['POST'])
def aprender():
    """IA aprende novo padrão ou solução"""
    data = request.json
    tipo = data.get('tipo', 'padrao')
    
    if tipo == 'api':
        # Registra nova API
        apis = carregar(APIS_FILE)
        apis.append({
            "nome": data.get('nome'),
            "url": data.get('url'),
            "descricao": data.get('descricao'),
            "registrada_em": str(datetime.now())
        })
        salvar(APIS_FILE, apis)
        
        # Adiciona ao conhecimento
        CONHECIMENTO['apis_disponiveis'][data['nome']] = {
            "url": data['url'],
            "porta": data.get('porta', 0),
            "descricao": data['descricao']
        }
    
    elif tipo == 'solucao':
        CONHECIMENTO['solucoes_prontas'][data.get('chave')] = data.get('solucao')
    
    elif tipo == 'padrao':
        CONHECIMENTO['padroes_problemas'][data.get('categoria')] = data.get('palavras', [])
    
    return jsonify({"status": "Aprendizado registrado!", "tipo": tipo})

@app.route('/api/ia/gerenciadora/sugerir-nova-api', methods=['POST'])
def sugerir_nova_api():
    """IA sugere criação de nova API baseada em necessidade"""
    data = request.json
    necessidade = data.get('necessidade', '')
    
    # Analisa necessidade e sugere nova API
    sugestao = {
        "nome": necessidade.lower().replace(' ', '_')[:30],
        "descricao": f"API para {necessidade}",
        "recursos_sugeridos": [
            f"CRUD de {necessidade}",
            f"Busca de {necessidade}",
            f"Relatório de {necessidade}"
        ],
        "estrutura": {
            "app.py": "Flask com rotas REST",
            "requirements.txt": "flask, flask-cors, gunicorn",
            "Procfile": "web: gunicorn app:app"
        },
        "codigo_base": f"""
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/{necessidade.lower().replace(" ", "_")}', methods=['GET'])
def listar():
    return jsonify({{"status": "API de {necessidade} funcionando!"}})

if __name__ == '__main__':
    app.run(port=int(os.environ.get('PORT', 5019)))
"""
    }
    
    return jsonify(sugestao)

@app.route('/api/ia/gerenciadora/memoria', methods=['GET'])
def memoria():
    """Histórico de aprendizados da IA"""
    return jsonify({
        "interacoes": carregar(DB_FILE)[-50:],
        "apis_registradas": carregar(APIS_FILE),
        "total_apis": len(CONHECIMENTO['apis_disponiveis']),
        "total_padroes": len(CONHECIMENTO['padroes_problemas']),
        "total_solucoes": len(CONHECIMENTO['solucoes_prontas'])
    })

@app.route('/api/ia/gerenciadora/status', methods=['GET'])
def status():
    """Status de todas as APIs gerenciadas"""
    status_apis = {}
    
    for nome, info in CONHECIMENTO['apis_disponiveis'].items():
        try:
            response = requests.get(f"{info['url']}/", timeout=5)
            status_apis[nome] = {
                "online": response.status_code == 200,
                "status_code": response.status_code,
                "url": info['url']
            }
        except:
            status_apis[nome] = {
                "online": False,
                "status_code": 0,
                "url": info['url']
            }
    
    online = sum(1 for s in status_apis.values() if s['online'])
    
    return jsonify({
        "total_apis": len(status_apis),
        "online": online,
        "offline": len(status_apis) - online,
        "apis": status_apis
    })

def gerar_plano_acao(problema, apis, contexto):
    """Gera plano de ação passo a passo"""
    plano = []
    
    if not apis:
        return ["🤔 Não identifiquei APIs específicas. Me dê mais detalhes do problema."]
    
    plano.append(f"📋 Plano para resolver: '{problema}'")
    
    for i, api in enumerate(apis[:3], 1):
        plano.append(f"{i}. Usar API '{api['api']}' ({api['descricao']})")
    
    if len(apis) > 1:
        plano.append(f"💡 Dica: Combine estas APIs em sequência para melhor resultado!")
    
    plano.append("⚡ Pronto para executar? Use o endpoint /executar com a API desejada.")
    
    return plano

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5019))
    app.run(host='0.0.0.0', port=port, debug=False)