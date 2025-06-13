#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analisador de Tributos em PDFs - Versão Desktop
Aplicação para análise de Diários Oficiais Municipais
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import re
import csv
import threading
from datetime import datetime
import pdfplumber
import requests
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class TributoAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("📊 Analisador de Tributos em PDFs - Diários Oficiais")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Configurações
        self.maritaca_api_key = os.environ.get('MARITACA_API_KEY', '')
        self.current_results = []
        
        # Estilo
        self.setup_style()
        
        # Interface
        self.create_widgets()
        
        # Centraliza janela
        self.center_window()
    
    def setup_style(self):
        """Configura o estilo da aplicação"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Cores personalizadas
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#2c3e50')
        style.configure('Subtitle.TLabel', font=('Arial', 12, 'bold'), foreground='#34495e')
        style.configure('Info.TLabel', font=('Arial', 10), foreground='#7f8c8d')
        style.configure('Success.TLabel', font=('Arial', 10), foreground='#27ae60')
        style.configure('Error.TLabel', font=('Arial', 10), foreground='#e74c3c')
        
    def center_window(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Cria todos os widgets da interface"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuração de redimensionamento
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="📊 Analisador de Tributos em PDFs", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, text="Análise de Diários Oficiais Municipais", style='Subtitle.TLabel')
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # Seção de arquivo
        file_frame = ttk.LabelFrame(main_frame, text="📁 Seleção de Arquivo", padding="15")
        file_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="Arquivo PDF:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, state='readonly')
        self.file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.browse_button = ttk.Button(file_frame, text="📂 Procurar", command=self.browse_file)
        self.browse_button.grid(row=0, column=2)
        
        # Info do arquivo
        self.file_info_label = ttk.Label(file_frame, text="", style='Info.TLabel')
        self.file_info_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
        # Seção de tributos
        tributos_frame = ttk.LabelFrame(main_frame, text="🔍 Tributos para Buscar", padding="15")
        tributos_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        tributos_frame.columnconfigure(1, weight=1)
        
        ttk.Label(tributos_frame, text="Tributos:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.tributos_var = tk.StringVar(value="ISS, ISSQN, IPTU, ITBI, ICMS")
        self.tributos_entry = ttk.Entry(tributos_frame, textvariable=self.tributos_var)
        self.tributos_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Botões de tributos predefinidos
        predefined_frame = ttk.Frame(tributos_frame)
        predefined_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(predefined_frame, text="ISS/ISSQN", 
                  command=lambda: self.set_tributos("ISS, ISSQN")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(predefined_frame, text="IPTU/ITBI", 
                  command=lambda: self.set_tributos("IPTU, ITBI")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(predefined_frame, text="Todos", 
                  command=lambda: self.set_tributos("ISS, ISSQN, IPTU, ITBI, ICMS, COFINS, PIS, CSLL")).pack(side=tk.LEFT, padx=(0, 5))
        
        # Configurações da API
        api_frame = ttk.LabelFrame(main_frame, text="🤖 Configurações da API Maritaca (Opcional)", padding="15")
        api_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        api_frame.columnconfigure(1, weight=1)
        
        ttk.Label(api_frame, text="Chave da API:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.api_key_var = tk.StringVar(value=self.maritaca_api_key)
        self.api_key_entry = ttk.Entry(api_frame, textvariable=self.api_key_var, show="*")
        self.api_key_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(api_frame, text="💾 Salvar", command=self.save_api_key).grid(row=0, column=2)
        
        info_label = ttk.Label(api_frame, text="ℹ️ Sem a chave da API, o sistema usa apenas regex (já muito eficiente)", style='Info.TLabel')
        info_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
        # Botão de análise
        self.analyze_button = ttk.Button(main_frame, text="🚀 Analisar PDF", command=self.start_analysis)
        self.analyze_button.grid(row=5, column=0, columnspan=3, pady=15)
        
        # Barra de progresso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, mode='indeterminate')
        self.progress_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status
        self.status_var = tk.StringVar(value="Pronto para análise")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, style='Info.TLabel')
        self.status_label.grid(row=7, column=0, columnspan=3)
        
        # Resultados
        results_frame = ttk.LabelFrame(main_frame, text="📋 Resultados", padding="15")
        results_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(15, 0))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(8, weight=1)
        
        # Treeview para resultados
        columns = ('Tributo', 'Linha', 'Número', 'Empresas', 'Contexto')
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=10)
        
        # Configuração das colunas
        self.results_tree.heading('Tributo', text='Tributo')
        self.results_tree.heading('Linha', text='Linha Encontrada')
        self.results_tree.heading('Número', text='Nº Linha')
        self.results_tree.heading('Empresas', text='Empresas')
        self.results_tree.heading('Contexto', text='Contexto')
        
        self.results_tree.column('Tributo', width=80, minwidth=60)
        self.results_tree.column('Linha', width=200, minwidth=150)
        self.results_tree.column('Número', width=80, minwidth=60)
        self.results_tree.column('Empresas', width=150, minwidth=100)
        self.results_tree.column('Contexto', width=300, minwidth=200)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        h_scrollbar = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid dos resultados
        self.results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Botões de ação
        buttons_frame = ttk.Frame(results_frame)
        buttons_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        self.export_button = ttk.Button(buttons_frame, text="📊 Exportar CSV", command=self.export_csv, state='disabled')
        self.export_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_button = ttk.Button(buttons_frame, text="🗑️ Limpar", command=self.clear_results, state='disabled')
        self.clear_button.pack(side=tk.LEFT)
        
        # Bind para duplo clique
        self.results_tree.bind('<Double-1>', self.show_full_context)
    
    def set_tributos(self, tributos):
        """Define tributos predefinidos"""
        self.tributos_var.set(tributos)
    
    def browse_file(self):
        """Abre diálogo para selecionar arquivo PDF"""
        file_path = filedialog.askopenfilename(
            title="Selecionar arquivo PDF",
            filetypes=[("Arquivos PDF", "*.pdf"), ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            self.file_path_var.set(file_path)
            
            # Mostra informações do arquivo
            try:
                size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                self.file_info_label.config(text=f"📄 {os.path.basename(file_path)} ({size:.1f} MB)")
            except:
                self.file_info_label.config(text=f"📄 {os.path.basename(file_path)}")
    
    def save_api_key(self):
        """Salva a chave da API"""
        api_key = self.api_key_var.get().strip()
        
        # Salva no arquivo .env
        try:
            env_content = ""
            if os.path.exists('.env'):
                with open('.env', 'r', encoding='utf-8') as f:
                    env_content = f.read()
            
            # Remove linha existente da API key
            lines = env_content.split('\n')
            lines = [line for line in lines if not line.startswith('MARITACA_API_KEY=')]
            
            # Adiciona nova chave
            if api_key:
                lines.append(f'MARITACA_API_KEY={api_key}')
            
            # Salva arquivo
            with open('.env', 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            self.maritaca_api_key = api_key
            messagebox.showinfo("Sucesso", "Chave da API salva com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar chave da API: {e}")
    
    def start_analysis(self):
        """Inicia a análise em thread separada"""
        file_path = self.file_path_var.get().strip()
        tributos = self.tributos_var.get().strip()
        
        if not file_path:
            messagebox.showerror("Erro", "Selecione um arquivo PDF")
            return
        
        if not tributos:
            messagebox.showerror("Erro", "Digite os tributos para buscar")
            return
        
        if not os.path.exists(file_path):
            messagebox.showerror("Erro", "Arquivo não encontrado")
            return
        
        # Desabilita botão e inicia progresso
        self.analyze_button.config(state='disabled')
        self.progress_bar.start()
        self.status_var.set("Analisando PDF...")
        
        # Inicia análise em thread separada
        thread = threading.Thread(target=self.analyze_pdf, args=(file_path, tributos))
        thread.daemon = True
        thread.start()
    
    def analyze_pdf(self, file_path, tributos_text):
        """Analisa o PDF (executado em thread separada)"""
        try:
            # Extrai texto do PDF
            self.update_status("Extraindo texto do PDF...")
            text = self.extract_text_from_pdf(file_path)
            
            if not text:
                self.show_error("Não foi possível extrair texto do PDF")
                return
            
            # Processa tributos
            tributos = [t.strip() for t in tributos_text.split(',') if t.strip()]
            
            # Busca tributos
            self.update_status("Buscando tributos no texto...")
            results = self.search_tributos_in_text(text, tributos)
            
            if not results:
                self.show_error("Nenhum dos tributos especificados foi encontrado no PDF")
                return
            
            # Extrai entidades
            self.update_status("Identificando empresas...")
            for i, result in enumerate(results):
                self.update_status(f"Processando resultado {i+1}/{len(results)}...")
                
                # Regex
                entities_regex = self.extract_entities_with_regex(result['contexto'])
                
                # API Maritaca (se disponível)
                entities_ai = []
                if self.maritaca_api_key:
                    entities_ai = self.extract_entities_with_maritaca(result['contexto'])
                
                # Combina resultados
                all_entities = list(set(entities_regex + entities_ai))
                result['empresas_identificadas'] = all_entities
            
            # Atualiza interface
            self.root.after(0, self.show_results, results)
            
        except Exception as e:
            self.root.after(0, self.show_error, f"Erro durante análise: {str(e)}")
    
    def extract_text_from_pdf(self, pdf_path):
        """Extrai texto do PDF"""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
            return text
        except Exception as e:
            print(f"Erro ao extrair texto: {e}")
            return None
    
    def search_tributos_in_text(self, text, tributos):
        """Busca tributos no texto"""
        results = []
        lines = text.split('\n')
        
        for tributo in tributos:
            pattern = r'\b' + re.escape(tributo.strip()) + r'\b'
            
            for i, line in enumerate(lines):
                if re.search(pattern, line, re.IGNORECASE):
                    # Contexto: 10 linhas antes e depois
                    start_idx = max(0, i - 10)
                    end_idx = min(len(lines), i + 11)
                    
                    context_lines = lines[start_idx:end_idx]
                    context = '\n'.join(context_lines)
                    
                    results.append({
                        'tributo': tributo.strip(),
                        'linha_encontrada': line.strip(),
                        'contexto': context,
                        'linha_numero': i + 1,
                        'empresas_identificadas': []
                    })
        
        return results
    
    def extract_entities_with_regex(self, text):
        """Extrai entidades usando regex"""
        entities = set()
        
        # Padrões para identificar empresas
        patterns = [
            # CNPJ
            r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}',
            # Razão social (palavras em maiúsculo seguidas de LTDA, ME, etc.)
            r'[A-ZÁÊÇÕ][A-ZÁÊÇÕ\s]{10,50}(?:LTDA|ME|EIRELI|S\.A\.|SA|EPP)',
            # Nomes próprios em maiúsculo
            r'[A-ZÁÊÇÕ][A-ZÁÊÇÕ\s]{5,30}(?=\s|$)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.strip()) > 3:
                    entities.add(match.strip())
                    if len(entities) >= 10:
                        break
        
        return list(entities)
    
    def extract_entities_with_maritaca(self, text):
        """Extrai entidades usando API Maritaca"""
        if not self.maritaca_api_key:
            return []
        
        try:
            from openai import OpenAI
            
            client = OpenAI(
                api_key=self.maritaca_api_key,
                base_url="https://chat.maritaca.ai/api"
            )
            
            # Limita texto
            text_limited = text[:1000]
            
            response = client.chat.completions.create(
                model="sabiazinho-3",
                messages=[
                    {
                        "role": "system",
                        "content": "Identifique nomes de empresas no texto e retorne apenas os nomes principais (sem LTDA, ME, etc.)."
                    },
                    {
                        "role": "user",
                        "content": f"Empresas no texto:\n\n{text_limited}"
                    }
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            if response.choices[0].message.content:
                # Extrai nomes das empresas da resposta
                content = response.choices[0].message.content
                lines = content.split('\n')
                empresas = []
                
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('Empresas') and len(line) > 3:
                        # Remove numeração e pontuação
                        line = re.sub(r'^\d+[\.\-\)]\s*', '', line)
                        line = re.sub(r'^[\-\*]\s*', '', line)
                        if line:
                            empresas.append(line)
                
                return empresas[:5]
            
            return []
            
        except Exception as e:
            print(f"Erro na API Maritaca: {e}")
            return []
    
    def update_status(self, message):
        """Atualiza status na thread principal"""
        self.root.after(0, lambda: self.status_var.set(message))
    
    def show_results(self, results):
        """Mostra resultados na interface"""
        self.current_results = results
        
        # Limpa resultados anteriores
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Adiciona novos resultados
        for result in results:
            empresas = '; '.join(result.get('empresas_identificadas', []))
            contexto_short = result['contexto'][:100] + "..." if len(result['contexto']) > 100 else result['contexto']
            
            self.results_tree.insert('', 'end', values=(
                result['tributo'],
                result['linha_encontrada'][:50] + "..." if len(result['linha_encontrada']) > 50 else result['linha_encontrada'],
                result['linha_numero'],
                empresas[:50] + "..." if len(empresas) > 50 else empresas,
                contexto_short.replace('\n', ' ')
            ))
        
        # Atualiza interface
        self.progress_bar.stop()
        self.analyze_button.config(state='normal')
        self.export_button.config(state='normal')
        self.clear_button.config(state='normal')
        self.status_var.set(f"✅ Análise concluída! {len(results)} resultados encontrados")
    
    def show_error(self, message):
        """Mostra erro na interface"""
        self.progress_bar.stop()
        self.analyze_button.config(state='normal')
        self.status_var.set(f"❌ {message}")
        messagebox.showerror("Erro", message)
    
    def show_full_context(self, event):
        """Mostra contexto completo em janela separada"""
        selection = self.results_tree.selection()
        if not selection:
            return
        
        item = self.results_tree.item(selection[0])
        values = item['values']
        
        if not values:
            return
        
        # Encontra o resultado completo
        tributo = values[0]
        linha_num = values[2]
        
        result = None
        for r in self.current_results:
            if r['tributo'] == tributo and r['linha_numero'] == linha_num:
                result = r
                break
        
        if not result:
            return
        
        # Cria janela de contexto
        context_window = tk.Toplevel(self.root)
        context_window.title(f"Contexto - {tributo} (Linha {linha_num})")
        context_window.geometry("800x600")
        
        # Frame principal
        frame = ttk.Frame(context_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Informações
        info_frame = ttk.Frame(frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(info_frame, text=f"Tributo: {result['tributo']}", style='Subtitle.TLabel').pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Linha: {result['linha_numero']}", style='Info.TLabel').pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Empresas: {'; '.join(result.get('empresas_identificadas', []))}", style='Info.TLabel').pack(anchor=tk.W)
        
        # Contexto
        ttk.Label(frame, text="Contexto completo:", style='Subtitle.TLabel').pack(anchor=tk.W, pady=(10, 5))
        
        context_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=20)
        context_text.pack(fill=tk.BOTH, expand=True)
        context_text.insert(tk.END, result['contexto'])
        context_text.config(state=tk.DISABLED)
    
    def export_csv(self):
        """Exporta resultados para CSV"""
        if not self.current_results:
            messagebox.showwarning("Aviso", "Nenhum resultado para exportar")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Salvar CSV",
            defaultextension=".csv",
            filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")],
            initialname=f"analise_tributos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                
                # Cabeçalho
                writer.writerow(['Tributo', 'Linha Encontrada', 'Número da Linha', 'Empresas Identificadas', 'Contexto Completo'])
                
                # Dados
                for result in self.current_results:
                    empresas = '; '.join(result.get('empresas_identificadas', []))
                    writer.writerow([
                        result['tributo'],
                        result['linha_encontrada'],
                        result['linha_numero'],
                        empresas,
                        result['contexto'].replace('\n', ' | ')
                    ])
            
            messagebox.showinfo("Sucesso", f"Arquivo exportado com sucesso!\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar arquivo: {e}")
    
    def clear_results(self):
        """Limpa os resultados"""
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        self.current_results = []
        self.export_button.config(state='disabled')
        self.clear_button.config(state='disabled')
        self.status_var.set("Resultados limpos")

def main():
    """Função principal"""
    root = tk.Tk()
    app = TributoAnalyzer(root)
    root.mainloop()

if __name__ == "__main__":
    main() 