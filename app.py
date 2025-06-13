import os
import re
import csv
import io
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
import pdfplumber
import requests
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Configurações
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
MARITACA_API_KEY = os.environ.get('MARITACA_API_KEY')

# Cria pasta de uploads se não existir
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Verifica se o arquivo tem extensão permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_path):
    """
    Extrai texto do PDF preservando formatação
    
    Args:
        pdf_path (str): Caminho para o arquivo PDF
        
    Returns:
        tuple: (texto_extraido, sucesso)
    """
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
        
        if not text.strip():
            return None, False
            
        return text, True
        
    except Exception as e:
        print(f"Erro ao extrair texto do PDF: {e}")
        return None, False

def search_tributos_in_text(text, tributos):
    """
    Busca menções aos tributos no texto usando regex com word boundaries
    
    Args:
        text (str): Texto do PDF
        tributos (list): Lista de tributos para buscar
        
    Returns:
        list: Lista de dicionários com trechos encontrados
    """
    results = []
    lines = text.split('\n')
    
    for tributo in tributos:
        # Regex com word boundaries para evitar falsos positivos
        pattern = r'\b' + re.escape(tributo.strip()) + r'\b'
        
        for i, line in enumerate(lines):
            if re.search(pattern, line, re.IGNORECASE):
                # Captura contexto: 7 linhas antes e depois
                start_idx = max(0, i - 7)
                end_idx = min(len(lines), i + 8)
                
                context_lines = lines[start_idx:end_idx]
                context = '\n'.join(context_lines)
                
                results.append({
                    'tributo': tributo.strip(),
                    'linha_encontrada': line.strip(),
                    'contexto': context,
                    'linha_numero': i + 1
                })
    
    return results

def extract_entities_with_regex(text):
    """
    Extrai nomes de empresas usando regex simples
    
    Args:
        text (str): Texto para análise
        
    Returns:
        list: Lista de possíveis nomes de empresas
    """
    entities = set()
    
    # Padrões para identificar empresas
    patterns = [
        # CNPJ
        r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}',
        # Palavras em maiúsculas seguidas de LTDA, S/A, etc.
        r'[A-ZÁÊÇÕ\s]{3,}(?:\s(?:LTDA|S/A|S\.A\.|EIRELI|EPP|ME)\.?)',
        # Sequências de palavras em maiúsculas (possíveis razões sociais)
        r'(?:[A-ZÁÊÇÕ]{2,}\s){2,}[A-ZÁÊÇÕ]{2,}'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if len(match.strip()) > 5:  # Filtrar resultados muito curtos
                entities.add(match.strip())
    
    return list(entities)

def extract_entities_with_maritaca(text):
    """
    Extrai entidades usando a API do Maritaca AI
    
    Args:
        text (str): Texto para análise
        
    Returns:
        list: Lista de organizações identificadas
    """
    if not MARITACA_API_KEY:
        return []
    
    try:
        url = "https://chat.maritaca.ai/api/chat/inference"
        
        prompt = f"""
        Analise o seguinte texto e identifique APENAS os nomes de pessoas jurídicas, empresas, organizações ou entidades empresariais mencionadas.
        
        Texto: {text[:2000]}  # Limita o texto para evitar tokens excessivos
        
        Responda APENAS com uma lista dos nomes identificados, separados por vírgula. Se não encontrar nenhum, responda "NENHUM".
        """
        
        headers = {
            "Authorization": f"Key {MARITACA_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "model": "sabia-2-medium",
            "max_tokens": 500,
            "temperature": 0.1
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('answer', '').strip()
            
            if content and content != "NENHUM":
                entities = [entity.strip() for entity in content.split(',') if entity.strip()]
                return entities
                
        return []
        
    except Exception as e:
        print(f"Erro na API Maritaca: {e}")
        return []

def process_pdf_analysis(pdf_path, tributos_text):
    """
    Processa a análise completa do PDF
    
    Args:
        pdf_path (str): Caminho para o PDF
        tributos_text (str): String com tributos separados por vírgula
        
    Returns:
        dict: Resultados da análise
    """
    # Extrai texto do PDF
    text, success = extract_text_from_pdf(pdf_path)
    if not success:
        return {"error": "Não foi possível extrair texto do PDF. Verifique se o arquivo contém texto pesquisável."}
    
    # Processa lista de tributos
    tributos = [t.strip() for t in tributos_text.split(',') if t.strip()]
    if not tributos:
        return {"error": "Nenhum tributo foi especificado para busca."}
    
    # Busca tributos no texto
    trechos_encontrados = search_tributos_in_text(text, tributos)
    
    if not trechos_encontrados:
        return {"error": "Nenhum dos tributos especificados foi encontrado no PDF."}
    
    # Extrai entidades para cada trecho
    results = []
    for trecho in trechos_encontrados:
        # Extração com regex
        entities_regex = extract_entities_with_regex(trecho['contexto'])
        
        # Extração com Maritaca AI
        entities_ai = extract_entities_with_maritaca(trecho['contexto'])
        
        # Combina resultados (remove duplicatas)
        all_entities = list(set(entities_regex + entities_ai))
        
        results.append({
            'tributo': trecho['tributo'],
            'linha_encontrada': trecho['linha_encontrada'],
            'contexto': trecho['contexto'],
            'linha_numero': trecho['linha_numero'],
            'empresas_identificadas': all_entities
        })
    
    return {"success": True, "results": results, "total_encontrados": len(results)}

@app.route('/')
def index():
    """Página inicial"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Processa upload do arquivo PDF"""
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo foi enviado"}), 400
    
    file = request.files['file']
    tributos = request.form.get('tributos', '')
    
    if file.filename == '':
        return jsonify({"error": "Nenhum arquivo foi selecionado"}), 400
    
    if not tributos.strip():
        return jsonify({"error": "Nenhum tributo foi especificado"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Adiciona timestamp para evitar conflitos
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        try:
            file.save(filepath)
            
            # Processa o arquivo
            result = process_pdf_analysis(filepath, tributos)
            
            # Remove arquivo temporário
            os.remove(filepath)
            
            return jsonify(result)
            
        except Exception as e:
            # Remove arquivo em caso de erro
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({"error": f"Erro ao processar arquivo: {str(e)}"}), 500
    
    return jsonify({"error": "Tipo de arquivo não permitido. Apenas PDFs são aceitos."}), 400

@app.route('/export_csv', methods=['POST'])
def export_csv():
    """Exporta resultados para CSV"""
    data = request.json
    
    if not data or 'results' not in data:
        return jsonify({"error": "Dados inválidos para exportação"}), 400
    
    # Cria CSV em memória
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Cabeçalho
    writer.writerow(['Tributo', 'Linha Encontrada', 'Número da Linha', 'Empresas Identificadas', 'Contexto Completo'])
    
    # Dados
    for result in data['results']:
        empresas = '; '.join(result.get('empresas_identificadas', []))
        writer.writerow([
            result.get('tributo', ''),
            result.get('linha_encontrada', ''),
            result.get('linha_numero', ''),
            empresas,
            result.get('contexto', '').replace('\n', ' | ')
        ])
    
    # Prepara arquivo para download
    output.seek(0)
    csv_data = output.getvalue().encode('utf-8-sig')  # BOM para Excel
    
    return send_file(
        io.BytesIO(csv_data),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'analise_tributos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.errorhandler(413)
def too_large(e):
    """Trata erro de arquivo muito grande"""
    return jsonify({"error": "Arquivo muito grande. Tamanho máximo: 50MB"}), 413

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 