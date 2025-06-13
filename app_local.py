#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analisador de Tributos em PDFs - Versão Local Desktop
Aplicação Flask que roda localmente e abre automaticamente no navegador
Simula uma aplicação desktop sem limitações de timeout
"""

import os
import re
import csv
import io
import webbrowser
import threading
import time
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, send_file
import pdfplumber
import requests
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'local-desktop-key')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max (sem limitações!)

# Configurações para versão local (sem limitações de timeout)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
MARITACA_API_KEY = os.environ.get('MARITACA_API_KEY', '')

# Cria pasta de uploads se não existir
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Verifica se o arquivo tem extensão permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_path):
    """
    Extrai texto do PDF preservando formatação (SEM LIMITAÇÕES)
    
    Args:
        pdf_path (str): Caminho para o arquivo PDF
        
    Returns:
        str: Texto extraído ou None se erro
    """
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"📄 Processando {total_pages} páginas...")
            
            for i, page in enumerate(pdf.pages):
                print(f"📖 Processando página {i+1}/{total_pages}")
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
        
        if not text.strip():
            return None
            
        print(f"✅ Texto extraído: {len(text)} caracteres")
        return text
        
    except Exception as e:
        print(f"❌ Erro ao extrair texto do PDF: {e}")
        return None

def search_tributos_in_text(text, tributos):
    """
    Busca menções aos tributos no texto usando regex (SEM LIMITAÇÕES)
    
    Args:
        text (str): Texto do PDF
        tributos (list): Lista de tributos para buscar
        
    Returns:
        list: Lista de dicionários com trechos encontrados
    """
    results = []
    lines = text.split('\n')
    
    print(f"🔍 Buscando em {len(lines)} linhas de texto...")
    
    for tributo in tributos:
        print(f"🎯 Buscando: {tributo}")
        # Regex com word boundaries para evitar falsos positivos
        pattern = r'\b' + re.escape(tributo.strip()) + r'\b'
        
        matches_found = 0
        for i, line in enumerate(lines):
            if re.search(pattern, line, re.IGNORECASE):
                # Captura contexto: 15 linhas antes e depois (mais contexto que a versão web)
                start_idx = max(0, i - 15)
                end_idx = min(len(lines), i + 16)
                
                context_lines = lines[start_idx:end_idx]
                context = '\n'.join(context_lines)
                
                results.append({
                    'tributo': tributo.strip(),
                    'linha_encontrada': line.strip(),
                    'contexto': context,
                    'linha_numero': i + 1
                })
                
                matches_found += 1
        
        print(f"✅ {tributo}: {matches_found} ocorrências encontradas")
    
    return results

def extract_entities_with_regex(text):
    """
    Extrai nomes de empresas usando regex (SEM LIMITAÇÕES)
    
    Args:
        text (str): Texto para análise
        
    Returns:
        list: Lista de possíveis nomes de empresas
    """
    entities = set()
    
    # Padrões para identificar empresas (mais abrangentes)
    patterns = [
        # CNPJ
        r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}',
        # Razão social completa
        r'[A-ZÁÊÇÕ][A-ZÁÊÇÕ\s]{10,80}(?:LTDA|ME|EIRELI|S\.A\.|SA|EPP|MICROEMPRESA|EMPRESA)',
        # Nomes próprios em maiúsculo
        r'[A-ZÁÊÇÕ][A-ZÁÊÇÕ\s]{8,50}(?=\s|$)',
        # Empresas com números
        r'[A-ZÁÊÇÕ][A-ZÁÊÇÕ\s\d]{5,50}(?:LTDA|ME|EIRELI)',
    ]
    
    for pattern in patterns:
        try:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                cleaned = match.strip()
                if len(cleaned) > 5 and not cleaned.isdigit():
                    entities.add(cleaned)
        except:
            continue
    
    return list(entities)

def extract_entities_with_maritaca(text):
    """
    Extrai entidades usando a API Maritaca AI (SEM LIMITAÇÕES DE TIMEOUT)
    
    Args:
        text (str): Texto para análise
        
    Returns:
        list: Lista de nomes de empresas identificadas
    """
    if not MARITACA_API_KEY or MARITACA_API_KEY == 'sua_chave_aqui':
        return []
    
    try:
        from openai import OpenAI
        
        client = OpenAI(
            api_key=MARITACA_API_KEY,
            base_url="https://chat.maritaca.ai/api"
        )
        
        # Limita o texto para a API (mas mais generoso que a versão web)
        text_limited = text[:2000]  # 2KB ao invés de 500 bytes
        
        response = client.chat.completions.create(
            model="sabiazinho-3",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um especialista em identificar nomes de empresas em textos oficiais. Identifique todas as empresas mencionadas e forneça apenas os nomes principais (removendo LTDA, ME, EIRELI, etc.)."
                },
                {
                    "role": "user",
                    "content": f"Identifique todas as empresas no texto abaixo:\n\n{text_limited}"
                }
            ],
            max_tokens=500,  # Mais tokens que a versão web
            temperature=0.1
        )
        
        if response.choices[0].message.content:
            # Extrai nomes das empresas da resposta
            content = response.choices[0].message.content
            lines = content.split('\n')
            empresas = []
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith(('Empresas', 'As empresas', 'Identifiquei')) and len(line) > 3:
                    # Remove numeração e pontuação
                    line = re.sub(r'^\d+[\.\-\)]\s*', '', line)
                    line = re.sub(r'^[\-\*]\s*', '', line)
                    if line:
                        empresas.append(line)
            
            return empresas
            
        return []
        
    except Exception as e:
        print(f"⚠️ Erro na API Maritaca: {e}")
        return []

def process_pdf_analysis(pdf_path, tributos_text):
    """
    Processa a análise completa do PDF (SEM LIMITAÇÕES)
    
    Args:
        pdf_path (str): Caminho para o PDF
        tributos_text (str): String com tributos separados por vírgula
        
    Returns:
        dict: Resultados da análise
    """
    try:
        print(f"🚀 Iniciando análise de: {os.path.basename(pdf_path)}")
        
        # Extrai texto do PDF
        text = extract_text_from_pdf(pdf_path)
        
        if not text:
            return {"error": "Não foi possível extrair texto do PDF. Verifique se o arquivo contém texto (não é apenas imagem)."}
        
        # Processa lista de tributos
        tributos = [t.strip() for t in tributos_text.split(',') if t.strip()]
        if not tributos:
            return {"error": "Nenhum tributo foi especificado para busca."}
        
        print(f"🎯 Buscando {len(tributos)} tributos: {', '.join(tributos)}")
        
        # Busca tributos no texto
        trechos_encontrados = search_tributos_in_text(text, tributos)
        
        if not trechos_encontrados:
            return {"error": "Nenhum dos tributos especificados foi encontrado no PDF."}
        
        print(f"📋 Processando {len(trechos_encontrados)} trechos encontrados...")
        
        # Extrai entidades para cada trecho
        results = []
        for i, trecho in enumerate(trechos_encontrados):
            print(f"🔍 Processando trecho {i+1}/{len(trechos_encontrados)}")
            
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
        
        print(f"✅ Análise concluída! {len(results)} resultados processados")
        return {"success": True, "results": results, "total_encontrados": len(results)}
        
    except Exception as e:
        print(f"❌ Erro durante processamento: {str(e)}")
        return {"error": f"Erro durante processamento: {str(e)}"}

@app.route('/')
def index():
    """Página inicial"""
    return render_template('index_local.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Processa upload do arquivo PDF (SEM LIMITAÇÕES)"""
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
            print(f"💾 Salvando arquivo: {filename}")
            file.save(filepath)
            
            # Mostra tamanho do arquivo
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            print(f"📊 Tamanho do arquivo: {size_mb:.1f} MB")
            
            # Processa o arquivo (SEM TIMEOUT!)
            result = process_pdf_analysis(filepath, tributos)
            
            # Remove arquivo temporário
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"🗑️ Arquivo temporário removido")
            
            return jsonify(result)
            
        except Exception as e:
            # Remove arquivo em caso de erro
            if os.path.exists(filepath):
                os.remove(filepath)
            print(f"❌ Erro: {str(e)}")
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
    return jsonify({"error": "Arquivo muito grande. Tamanho máximo: 500MB"}), 413

def open_browser():
    """Abre o navegador automaticamente"""
    time.sleep(1.5)  # Aguarda o servidor iniciar
    webbrowser.open('http://127.0.0.1:8888')

def main():
    """Função principal - simula aplicação desktop"""
    print("=" * 60)
    print("🖥️  ANALISADOR DE TRIBUTOS - VERSÃO LOCAL DESKTOP")
    print("=" * 60)
    print("🚀 Iniciando aplicação local...")
    print("🌐 Servidor rodando em: http://127.0.0.1:8888")
    print("📱 Abrindo navegador automaticamente...")
    print("⚠️  Para fechar: Pressione Ctrl+C no terminal")
    print("=" * 60)
    
    # Abre navegador em thread separada
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Inicia servidor Flask
    try:
        app.run(debug=False, host='127.0.0.1', port=8888, use_reloader=False)
    except KeyboardInterrupt:
        print("\n🛑 Aplicação encerrada pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro ao iniciar aplicação: {e}")

if __name__ == '__main__':
    main() 