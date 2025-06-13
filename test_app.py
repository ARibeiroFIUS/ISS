#!/usr/bin/env python3
"""
Script de teste básico para o Analisador de Tributos
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, extract_text_from_pdf, search_tributos_in_text, extract_entities_with_regex

class TestAnalisadorTributos(unittest.TestCase):
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.app = app.test_client()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        
    def test_index_page(self):
        """Testa se a página principal carrega corretamente"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Analisador de Tributos', response.data)
    
    def test_search_tributos_in_text(self):
        """Testa a função de busca de tributos"""
        texto = """
        Este é um teste sobre ISS.
        Também temos informações sobre IPTU aqui.
        E algumas menções ao ISSQN no documento.
        Mas não devemos pegar palavras como "isso" ou "mississippi".
        """
        
        tributos = ['ISS', 'IPTU', 'ISSQN']
        resultados = search_tributos_in_text(texto, tributos)
        
        # Deve encontrar os 3 tributos
        tributos_encontrados = [r['tributo'] for r in resultados]
        self.assertIn('ISS', tributos_encontrados)
        self.assertIn('IPTU', tributos_encontrados)
        self.assertIn('ISSQN', tributos_encontrados)
        
        # Não deve encontrar palavras parciais
        linhas_encontradas = ' '.join([r['linha_encontrada'] for r in resultados])
        self.assertNotIn('isso', linhas_encontradas.lower())
        self.assertNotIn('mississippi', linhas_encontradas.lower())
    
    def test_extract_entities_with_regex(self):
        """Testa a extração de entidades com regex"""
        texto = """
        A empresa EXEMPLO COMERCIAL LTDA, CNPJ 12.345.678/0001-90,
        foi autuada juntamente com OUTRA EMPRESA S/A.
        Também temos TERCEIRA COMPANHIA EIRELI.
        """
        
        entidades = extract_entities_with_regex(texto)
        
        # Deve encontrar pelo menos algumas entidades
        self.assertGreater(len(entidades), 0)
        
        # Verifica se encontrou CNPJ
        cnpj_encontrado = any('12.345.678/0001-90' in entidade for entidade in entidades)
        self.assertTrue(cnpj_encontrado)
    
    def test_upload_without_file(self):
        """Testa upload sem arquivo"""
        response = self.app.post('/upload', data={
            'tributos': 'ISS, IPTU'
        })
        self.assertEqual(response.status_code, 400)
        
    def test_upload_without_tributos(self):
        """Testa upload sem especificar tributos"""
        # Simula um arquivo PDF vazio
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(b'%PDF-1.4\nfake pdf content')
            tmp_path = tmp.name
            
        try:
            with open(tmp_path, 'rb') as test_file:
                response = self.app.post('/upload', data={
                    'file': (test_file, 'test.pdf'),
                    'tributos': ''
                })
                self.assertEqual(response.status_code, 400)
        finally:
            os.unlink(tmp_path)
    
    def test_export_csv_without_data(self):
        """Testa exportação CSV sem dados"""
        response = self.app.post('/export_csv', 
                                json={'results': []},
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)
    
    def test_export_csv_with_data(self):
        """Testa exportação CSV com dados válidos"""
        test_data = {
            'results': [
                {
                    'tributo': 'ISS',
                    'linha_encontrada': 'Teste ISS linha',
                    'linha_numero': 10,
                    'empresas_identificadas': ['EMPRESA TESTE LTDA'],
                    'contexto': 'Contexto completo do teste'
                }
            ]
        }
        
        response = self.app.post('/export_csv',
                                json=test_data,
                                content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'text/csv')

class TestSecurityValidations(unittest.TestCase):
    """Testes de segurança e validações"""
    
    def setUp(self):
        self.app = app.test_client()
        app.config['TESTING'] = True
        
    def test_file_size_limit(self):
        """Testa limite de tamanho de arquivo"""
        # Cria um arquivo "muito grande" (simulado)
        large_content = b'x' * (51 * 1024 * 1024)  # 51MB
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(large_content[:1000])  # Escreve apenas uma parte para não usar muito espaço
            tmp_path = tmp.name
            
        try:
            with open(tmp_path, 'rb') as test_file:
                # Simula arquivo grande modificando o header Content-Length
                response = self.app.post('/upload', data={
                    'file': (test_file, 'large.pdf'),
                    'tributos': 'ISS'
                }, headers={'Content-Length': str(51 * 1024 * 1024)})
                # O Flask deve rejeitar automaticamente
                self.assertIn(response.status_code, [400, 413])
        finally:
            os.unlink(tmp_path)
    
    def test_invalid_file_type(self):
        """Testa rejeição de tipos de arquivo inválidos"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            tmp.write(b'Este e um arquivo de texto, nao PDF')
            tmp_path = tmp.name
            
        try:
            with open(tmp_path, 'rb') as test_file:
                response = self.app.post('/upload', data={
                    'file': (test_file, 'test.txt'),
                    'tributos': 'ISS'
                })
                self.assertEqual(response.status_code, 400)
        finally:
            os.unlink(tmp_path)

def run_basic_checks():
    """Executa verificações básicas do ambiente"""
    print("🔍 Executando verificações básicas...")
    
    # Verifica se todas as dependências estão instaladas
    try:
        import flask
        import pdfplumber
        import requests
        from dotenv import load_dotenv
        print("✅ Todas as dependências principais estão instaladas")
    except ImportError as e:
        print(f"❌ Dependência faltante: {e}")
        return False
    
    # Verifica estrutura de pastas
    required_dirs = ['templates', 'static/css', 'static/js']
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ Diretório {dir_path} existe")
        else:
            print(f"❌ Diretório {dir_path} não encontrado")
            return False
    
    # Verifica arquivos essenciais
    required_files = [
        'app.py', 'requirements.txt', 'templates/index.html',
        'static/css/styles.css', 'static/js/app.js'
    ]
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ Arquivo {file_path} existe")
        else:
            print(f"❌ Arquivo {file_path} não encontrado")
            return False
    
    # Verifica se o arquivo .env existe (opcional mas recomendado)
    if os.path.exists('.env'):
        print("✅ Arquivo .env encontrado")
    else:
        print("⚠️  Arquivo .env não encontrado - crie baseado no env.example")
    
    print("✅ Verificações básicas concluídas com sucesso!")
    return True

if __name__ == '__main__':
    print("🧪 Iniciando testes do Analisador de Tributos...\n")
    
    # Executa verificações básicas primeiro
    if not run_basic_checks():
        print("\n❌ Verificações básicas falharam. Corrija os problemas antes de continuar.")
        sys.exit(1)
    
    print("\n🏃 Executando testes unitários...\n")
    
    # Executa testes unitários
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    print("\n✅ Testes concluídos! Se todos passaram, a aplicação está pronta para uso.")
    print("\n📝 Para executar a aplicação:")
    print("   python app.py")
    print("\n🌐 Para fazer deploy no Render.com:")
    print("   1. Envie o código para um repositório Git")
    print("   2. Configure as variáveis de ambiente no Render")
    print("   3. Faça o deploy seguindo as instruções do README.md") 