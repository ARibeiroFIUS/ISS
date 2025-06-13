# 🚀 Guia Rápido - Versão Desktop

## ⚡ **SOLUÇÃO PARA PROBLEMAS DE TIMEOUT**

A versão desktop elimina **completamente** os problemas de timeout do Render.com!

## 🎯 **Duas Opções Disponíveis**

### 🌐 **Opção 1: Flask Local (RECOMENDADA)**
**Funciona em qualquer sistema operacional**

```bash
# 1. Instale as dependências
pip install -r requirements_desktop.txt

# 2. Execute a aplicação
python app_local.py
```

**✨ O que acontece:**
- Abre automaticamente no seu navegador
- Interface moderna e responsiva
- 100% local, sem internet necessária
- Funciona em Windows, macOS e Linux

### 🖥️ **Opção 2: Tkinter Nativo**
**Interface desktop nativa (requer tkinter)**

```bash
# 1. Instale as dependências
pip install -r requirements_desktop.txt

# 2. Execute a aplicação
python app_desktop.py
```

## 🎮 **Como Usar (Ambas as Versões)**

### 1. **📁 Selecione seu PDF**
- Clique em "Procurar" ou arraste o arquivo
- **Sem limite de tamanho** (até 500MB)
- **Todas as páginas** serão processadas

### 2. **🔍 Configure os Tributos**
- Use os botões predefinidos ou digite manualmente
- Exemplos: `ISS, ISSQN, IPTU, ITBI`

### 3. **🤖 API Maritaca (Opcional)**
- Cole sua chave da API para melhor identificação de empresas
- **Funciona perfeitamente sem a chave** (apenas regex)

### 4. **🚀 Analise**
- Clique em "Analisar PDF"
- **Sem pressa** - processa arquivos grandes tranquilamente

### 5. **📊 Resultados**
- Visualize todos os resultados encontrados
- Clique em qualquer linha para ver contexto completo
- Exporte para CSV quando quiser

## ✅ **Vantagens vs Versão Web**

| Aspecto | Versão Web | Versão Desktop |
|---------|------------|----------------|
| **Timeout** | ❌ 25s máximo | ✅ **Sem limite** |
| **Tamanho PDF** | ❌ 10MB máximo | ✅ **500MB** |
| **Páginas** | ❌ 10 máximo | ✅ **Todas** |
| **Privacidade** | ❌ Upload necessário | ✅ **100% local** |
| **Contexto** | ❌ 5 linhas | ✅ **15 linhas** |
| **Performance** | ❌ Limitada | ✅ **Máxima** |

## 🛠️ **Gerar Executável (.exe)**

Para criar um arquivo executável:

```bash
# 1. Instale PyInstaller
pip install pyinstaller

# 2. Execute o script de build
python build_exe.py

# 3. Encontre o .exe em:
AnalisadorTributos_v1.0/AnalisadorTributos.exe
```

## 🆘 **Problemas? Soluções Rápidas**

### **"ModuleNotFoundError: No module named '_tkinter'"**
- **Solução**: Use a versão Flask Local (`python app_local.py`)
- Funciona em qualquer sistema sem dependências extras

### **"Porta em uso"**
- **Solução**: A aplicação Flask Local usa porta 8888
- Se ocupada, ela tentará outra porta automaticamente

### **"Não encontra tributos"**
- **Solução**: Verifique a ortografia
- Teste com termos simples: `ISS` ao invés de `ISS Municipal`

### **"PDF muito grande"**
- **Solução**: A versão desktop suporta até 500MB
- Se ainda der problema, divida o PDF em partes menores

## 🎉 **Resultado Final**

**✨ Aplicação 100% funcional que:**
- ✅ Processa PDFs de qualquer tamanho
- ✅ Não tem limitações de timeout
- ✅ Mantém seus dados privados
- ✅ Oferece resultados completos e precisos
- ✅ Funciona offline (exceto API Maritaca)

---

**🚀 Agora você tem uma solução completa e sem limitações para análise de tributos em PDFs!** 