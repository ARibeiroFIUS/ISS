#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para gerar executável da aplicação desktop
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_executable():
    """Constrói o executável usando PyInstaller"""
    
    print("🚀 Iniciando build do executável...")
    
    # Verifica se o PyInstaller está instalado
    try:
        import PyInstaller
        print(f"✅ PyInstaller {PyInstaller.__version__} encontrado")
    except ImportError:
        print("❌ PyInstaller não encontrado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller==6.3.0"])
    
    # Limpa builds anteriores
    if os.path.exists("build"):
        shutil.rmtree("build")
        print("🗑️ Pasta build anterior removida")
    
    if os.path.exists("dist"):
        shutil.rmtree("dist")
        print("🗑️ Pasta dist anterior removida")
    
    # Comando do PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",                    # Arquivo único
        "--windowed",                   # Sem console (Windows)
        "--name=AnalisadorTributos",    # Nome do executável
        "--icon=icon.ico",              # Ícone (se existir)
        "--add-data=.env;.",           # Inclui arquivo .env
        "--hidden-import=pdfplumber",   # Imports ocultos
        "--hidden-import=openai",
        "--hidden-import=requests",
        "--hidden-import=dotenv",
        "--clean",                      # Limpa cache
        "app_desktop.py"
    ]
    
    # Remove ícone se não existir
    if not os.path.exists("icon.ico"):
        cmd.remove("--icon=icon.ico")
        print("ℹ️ Ícone não encontrado, continuando sem ícone")
    
    # Remove .env se não existir
    if not os.path.exists(".env"):
        cmd.remove("--add-data=.env;.")
        print("ℹ️ Arquivo .env não encontrado, continuando sem ele")
    
    print(f"🔨 Executando: {' '.join(cmd)}")
    
    try:
        # Executa PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("✅ Build concluído com sucesso!")
        
        # Verifica se o executável foi criado
        exe_path = Path("dist/AnalisadorTributos.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"📦 Executável criado: {exe_path} ({size_mb:.1f} MB)")
            
            # Cria pasta de distribuição
            dist_folder = Path("AnalisadorTributos_v1.0")
            if dist_folder.exists():
                shutil.rmtree(dist_folder)
            
            dist_folder.mkdir()
            
            # Copia executável
            shutil.copy2(exe_path, dist_folder / "AnalisadorTributos.exe")
            
            # Cria arquivo README
            readme_content = """# 📊 Analisador de Tributos em PDFs

## 🚀 Como usar:

1. **Execute** o arquivo `AnalisadorTributos.exe`
2. **Selecione** um arquivo PDF de Diário Oficial
3. **Digite** os tributos que deseja buscar (ex: ISS, ISSQN, IPTU)
4. **Clique** em "Analisar PDF"
5. **Visualize** os resultados na tabela
6. **Exporte** para CSV se necessário

## 🔧 Configuração da API Maritaca (Opcional):

- Para melhor identificação de empresas, configure sua chave da API Maritaca
- Acesse: https://plataforma.maritaca.ai/chaves-de-api
- Cole a chave no campo "Chave da API" e clique em "Salvar"
- **Sem a chave, o sistema funciona apenas com regex (já muito eficiente)**

## 📋 Tributos suportados:

- ISS (Imposto Sobre Serviços)
- ISSQN (Imposto Sobre Serviços de Qualquer Natureza)
- IPTU (Imposto Predial e Territorial Urbano)
- ITBI (Imposto de Transmissão de Bens Imóveis)
- ICMS (Imposto sobre Circulação de Mercadorias e Serviços)
- COFINS (Contribuição para o Financiamento da Seguridade Social)
- PIS (Programa de Integração Social)
- CSLL (Contribuição Social sobre o Lucro Líquido)

## ⚠️ Requisitos:

- Windows 10 ou superior
- Arquivos PDF com texto (não escaneados)
- Conexão com internet (apenas para API Maritaca)

## 🆘 Suporte:

Em caso de problemas, verifique:
- Se o PDF contém texto (não é apenas imagem)
- Se os tributos estão escritos corretamente
- Se há conexão com internet (para API)

---
**Versão 1.0 - Desenvolvido para análise de Diários Oficiais Municipais**
"""
            
            with open(dist_folder / "README.txt", "w", encoding="utf-8") as f:
                f.write(readme_content)
            
            print(f"📁 Pasta de distribuição criada: {dist_folder}")
            print("🎉 Build finalizado! Pronto para distribuição.")
            
        else:
            print("❌ Executável não encontrado após build")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro durante build: {e}")
        print(f"Saída: {e.stdout}")
        print(f"Erro: {e.stderr}")
        return False
    
    return True

def create_spec_file():
    """Cria arquivo .spec personalizado para builds avançadas"""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app_desktop.py'],
    pathex=[],
    binaries=[],
    datas=[('.env', '.') if os.path.exists('.env') else None],
    hiddenimports=['pdfplumber', 'openai', 'requests', 'dotenv'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove None entries
a.datas = [x for x in a.datas if x is not None]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AnalisadorTributos',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
"""
    
    with open("AnalisadorTributos.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    print("📝 Arquivo .spec criado para builds personalizadas")

if __name__ == "__main__":
    print("=" * 60)
    print("🏗️  GERADOR DE EXECUTÁVEL - ANALISADOR DE TRIBUTOS")
    print("=" * 60)
    
    # Verifica se está no diretório correto
    if not os.path.exists("app_desktop.py"):
        print("❌ Arquivo app_desktop.py não encontrado!")
        print("Execute este script na pasta do projeto.")
        sys.exit(1)
    
    # Cria arquivo .spec
    create_spec_file()
    
    # Constrói executável
    success = build_executable()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ BUILD CONCLUÍDO COM SUCESSO!")
        print("📦 Executável disponível na pasta 'AnalisadorTributos_v1.0'")
        print("🚀 Pronto para distribuição!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ BUILD FALHOU!")
        print("Verifique os erros acima e tente novamente.")
        print("=" * 60)
        sys.exit(1) 