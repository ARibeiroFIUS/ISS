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
import threading
from functools import wraps

# Carrega variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Configurações otimizadas
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
MARITACA_API_KEY = os.environ.get('MARITACA_API_KEY')

# Configurações de timeout (ultra-agressivas para Render.com gratuito)
PDF_PROCESSING_TIMEOUT = 8  # segundos (reduzido drasticamente de 15 para 8)
API_TIMEOUT = 3  # segundos (reduzido de 5 para 3)
MAX_PDF_PAGES = 10  # máximo de páginas para processar (reduzido de 20 para 10)
MAX_TEXT_SIZE = 100000  # 100KB de texto máximo (reduzido de 200KB)
MAX_LINES_PROCESSED = 2000  # máximo de linhas processadas (reduzido de 5000)
MAX_MATCHES_PER_TRIBUTO = 5  # máximo de matches por tributo (reduzido de 10)
MAX_RESULTS_RETURNED = 10  # máximo de resultados retornados (reduzido de 20)

# Cria pasta de uploads se não existir
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class TimeoutError(Exception):
    pass

def with_timeout(seconds):
    """Decorator para adicionar timeout a funções usando threading"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = [None]
            exception = [None]
            success = [False]
            
            def target():
                try:
                    result[0] = func(*args, **kwargs)
                    success[0] = True
                except Exception as e:
                    exception[0] = e
            
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(seconds)
            
            if thread.is_alive():
                # Thread ainda está rodando, timeout ocorreu
                return None, False
            
            if exception[0]:
                # Houve uma exceção na função
                print(f"Erro na função {func.__name__}: {exception[0]}")
                return None, False
                
            return result[0], success[0]
        
        return wrapper
    return decorator

def allowed_file(filename):
    """Verifica se o arquivo tem extensão permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@with_timeout(PDF_PROCESSING_TIMEOUT)
def extract_text_from_pdf(pdf_path):
    """
    Extrai texto do PDF preservando formatação com timeout e limite de páginas
    
    Args:
        pdf_path (str): Caminho para o arquivo PDF
        
    Returns:
        tuple: (texto_extraido, sucesso)
    """
    try:
        text = ""
        pages_processed = 0
        
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            max_pages = min(total_pages, MAX_PDF_PAGES)
            
            for i, page in enumerate(pdf.pages):
                if pages_processed >= max_pages:
                    break
                    
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
                
                pages_processed += 1
                
                # Quebra se o texto já é muito grande (performance)
                if len(text) > MAX_TEXT_SIZE:  # 100KB de texto (reduzido)
                    break
        
        if not text.strip():
            return None, False
            
        return text, True
        
    except Exception as e:
        print(f"Erro ao extrair texto do PDF: {e}")
        return None, False

def search_tributos_in_text(text, tributos):
    """
    Busca menções aos tributos no texto usando regex com word boundaries (otimizada)
    
    Args:
        text (str): Texto do PDF
        tributos (list): Lista de tributos para buscar
        
    Returns:
        list: Lista de dicionários com trechos encontrados
    """
    results = []
    
    # Verifica se text é uma tupla (caso de timeout) e extrai apenas o texto
    if isinstance(text, tuple):
        text = text[0] if text[0] is not None else ""
    
    # Garante que text é uma string
    if not isinstance(text, str):
        return results
    
    lines = text.split('\n')
    
    # Limita número de linhas para performance
    if len(lines) > MAX_LINES_PROCESSED:
        lines = lines[:MAX_LINES_PROCESSED]
    
    for tributo in tributos:
        # Regex com word boundaries para evitar falsos positivos
        pattern = r'\b' + re.escape(tributo.strip()) + r'\b'
        
        matches_found = 0
        for i, line in enumerate(lines):
            if re.search(pattern, line, re.IGNORECASE):
                # Limita número de matches por tributo
                if matches_found >= MAX_MATCHES_PER_TRIBUTO:
                    break
                
                # Captura contexto: 5 linhas antes e depois (reduzido para performance)
                start_idx = max(0, i - 5)
                end_idx = min(len(lines), i + 6)
                
                context_lines = lines[start_idx:end_idx]
                context = '\n'.join(context_lines)
                
                results.append({
                    'tributo': tributo.strip(),
                    'linha_encontrada': line.strip(),
                    'contexto': context[:MAX_TEXT_SIZE],  # Limita tamanho do contexto
                    'linha_numero': i + 1
                })
                
                matches_found += 1
    
    return results

def extract_entities_with_regex(text):
    """
    Extrai nomes de empresas usando regex simples (otimizada)
    
    Args:
        text (str): Texto para análise
        
    Returns:
        list: Lista de possíveis nomes de empresas
    """
    entities = set()
    
    # Verifica se text é uma tupla (caso de timeout) e extrai apenas o texto
    if isinstance(text, tuple):
        text = text[0] if text[0] is not None else ""
    
    # Garante que text é uma string
    if not isinstance(text, str):
        return list(entities)
    
    # Limita tamanho do texto para performance
    text = text[:MAX_TEXT_SIZE]
    
    # Padrões para identificar empresas (otimizados)
    patterns = [
        # CNPJ
        r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}',
        # Palavras em maiúsculas seguidas de LTDA, S/A, etc.
        r'[A-ZÁÊÇÕ\s]{3,30}(?:\s(?:LTDA|S/A|S\.A\.|EIRELI|EPP|ME)\.?)',
    ]
    
    for pattern in patterns:
        try:
            matches = re.findall(pattern, text)
            for match in matches:
                if 5 < len(match.strip()) < 100:  # Filtrar resultados muito curtos ou longos
                    entities.add(match.strip())
                    
                # Limita número de entidades encontradas
                if len(entities) >= MAX_RESULTS_RETURNED:
                    break
        except:
            continue
    
    return list(entities)

@with_timeout(API_TIMEOUT)
def extract_entities_with_maritaca(text):
    """
    Extrai entidades usando a API Maritaca AI com timeout e otimizações agressivas
    
    Args:
        text (str): Texto para análise
        
    Returns:
        list: Lista de nomes de empresas identificadas
    """
    # Verifica se text é uma tupla (caso de timeout) e extrai apenas o texto
    if isinstance(text, tuple):
        text = text[0] if text[0] is not None else ""
    
    # Garante que text é uma string
    if not isinstance(text, str):
        return []
    
    # Se não há chave da API, retorna lista vazia
    if not MARITACA_API_KEY or MARITACA_API_KEY == 'sua_chave_aqui':
        return []
    
    try:
        from openai import OpenAI
        
        client = OpenAI(
            api_key=MARITACA_API_KEY,
            base_url="https://chat.maritaca.ai/api"
        )
        
        # Limita o texto para a API (ainda mais agressivo)
        text_limited = text[:500]  # Reduzido drasticamente para 500 caracteres
        
        # Schema para saída estruturada (simplificado)
        empresa_schema = {
            "name": "empresas_identificadas",
            "schema": {
                "type": "object",
                "properties": {
                    "empresas": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "nome_simplificado": {"type": "string"}
                            },
                            "required": ["nome_simplificado"]
                        }
                    }
                },
                "required": ["empresas"]
            }
        }
        
        response = client.beta.chat.completions.parse(
            model="sabiazinho-3",
            messages=[
                {
                    "role": "system", 
                    "content": "Identifique empresas e forneça apenas o nome principal (sem LTDA, ME, etc.)."
                },
                {
                    "role": "user", 
                    "content": f"Empresas no texto:\n\n{text_limited}"
                }
            ],
            response_format={"type": "json_schema", "json_schema": empresa_schema},
            max_tokens=100,  # Reduzido drasticamente
            temperature=0.1
        )
        
        if response.choices[0].message.content:
            import json
            result = json.loads(response.choices[0].message.content)
            empresas = result.get('empresas', [])
            
            # Retorna os nomes simplificados
            nomes_simplificados = [emp.get('nome_simplificado', '') 
                                 for emp in empresas if emp.get('nome_simplificado')]
            
            return nomes_simplificados[:3]  # Limita ainda mais o retorno
                
        return []
        
    except Exception as e:
        print(f"Erro na API Maritaca: {e}")
        return []

def process_pdf_analysis(pdf_path, tributos_text):
    """
    Processa a análise completa do PDF (ultra-otimizada para Render.com)
    
    Args:
        pdf_path (str): Caminho para o PDF
        tributos_text (str): String com tributos separados por vírgula
        
    Returns:
        dict: Resultados da análise
    """
    try:
        # Extrai texto do PDF
        result = extract_text_from_pdf(pdf_path)
        
        # Verifica se o resultado é uma tupla (com timeout) ou apenas o texto
        if isinstance(result, tuple):
            text, success = result
            if not success or text is None:
                return {"error": "Tempo limite excedido. Tente um PDF menor ou com menos páginas."}
        else:
            # Resultado direto (sem timeout)
            text = result
            if text is None:
                return {"error": "Não foi possível extrair texto do PDF."}
        
        # Processa lista de tributos (limita a 3 tributos)
        tributos = [t.strip() for t in tributos_text.split(',') if t.strip()]
        if not tributos:
            return {"error": "Nenhum tributo foi especificado para busca."}
        
        # Limita número de tributos drasticamente
        tributos = tributos[:3]
        
        # Busca tributos no texto
        trechos_encontrados = search_tributos_in_text(text, tributos)
        
        if not trechos_encontrados:
            return {"error": "Nenhum dos tributos especificados foi encontrado no PDF."}
        
        # Limita número de trechos processados drasticamente
        trechos_encontrados = trechos_encontrados[:5]
        
        # Extrai entidades para cada trecho (processamento mínimo)
        results = []
        for i, trecho in enumerate(trechos_encontrados):
            # Para economizar tempo, só processa entidades nos primeiros 3 trechos
            if i >= 3:
                results.append({
                    'tributo': trecho['tributo'],
                    'linha_encontrada': trecho['linha_encontrada'],
                    'contexto': trecho['contexto'][:500],  # Contexto muito reduzido
                    'linha_numero': trecho['linha_numero'],
                    'empresas_identificadas': []  # Sem processamento de entidades para economizar tempo
                })
                continue
            
            # Extração com regex (apenas para os primeiros trechos)
            entities_regex = extract_entities_with_regex(trecho['contexto'])
            
            # Extração com Maritaca AI (apenas para o primeiro trecho)
            entities_ai = []
            if i == 0 and MARITACA_API_KEY and MARITACA_API_KEY != 'sua_chave_aqui':
                ai_result = extract_entities_with_maritaca(trecho['contexto'])
                if isinstance(ai_result, tuple):
                    entities_ai = ai_result[0] if ai_result[0] is not None else []
                else:
                    entities_ai = ai_result if ai_result is not None else []
            
            # Combina resultados (remove duplicatas)
            all_entities = list(set(entities_regex + entities_ai))[:3]  # Máximo 3 entidades
            
            results.append({
                'tributo': trecho['tributo'],
                'linha_encontrada': trecho['linha_encontrada'],
                'contexto': trecho['contexto'][:500],  # Contexto reduzido
                'linha_numero': trecho['linha_numero'],
                'empresas_identificadas': all_entities
            })
        
        return {"success": True, "results": results, "total_encontrados": len(results)}
        
    except Exception as e:
        return {"error": f"Erro durante processamento: {str(e)}"}

@app.route('/')
def index():
    """Página inicial"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Processa upload do arquivo PDF (otimizado para Render.com)"""
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo foi enviado"}), 400
    
    file = request.files['file']
    tributos = request.form.get('tributos', '')
    
    if file.filename == '':
        return jsonify({"error": "Nenhum arquivo foi selecionado"}), 400
    
    if not tributos.strip():
        return jsonify({"error": "Nenhum tributo foi especificado"}), 400
    
    # Verifica tamanho do arquivo (mais restritivo para Render.com)
    file.seek(0, 2)  # Move para o final do arquivo
    file_size = file.tell()
    file.seek(0)  # Volta para o início
    
    # Limite mais restritivo: 10MB para Render.com gratuito
    if file_size > 10 * 1024 * 1024:
        return jsonify({"error": "Arquivo muito grande. Máximo 10MB para melhor performance."}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Adiciona timestamp para evitar conflitos
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        try:
            file.save(filepath)
            
            # Processa o arquivo com timeout global
            import time
            start_time = time.time()
            
            result = process_pdf_analysis(filepath, tributos)
            
            # Verifica se excedeu tempo total (failsafe)
            if time.time() - start_time > 25:  # 25 segundos máximo total
                result = {"error": "Processamento muito longo. Tente um arquivo menor."}
            
            # Remove arquivo temporário
            if os.path.exists(filepath):
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
    # Configuração para produção no Render.com
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port) 