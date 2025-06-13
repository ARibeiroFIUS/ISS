# 🖥️ Analisador de Tributos - Versão Desktop

## 🎯 Visão Geral

Aplicação desktop para análise de tributos em PDFs de Diários Oficiais Municipais. Roda **100% local** na máquina do usuário, sem limitações de timeout ou dependência de servidores externos.

## ✨ Vantagens da Versão Desktop

### 🚀 **Performance Superior**
- ✅ **Sem timeouts**: Processa arquivos grandes sem pressa
- ✅ **Sem limitações de tamanho**: PDFs de qualquer tamanho
- ✅ **Processamento completo**: Analisa todas as páginas
- ✅ **Multithreading**: Interface responsiva durante processamento

### 🔒 **Privacidade Total**
- ✅ **100% offline**: Seus PDFs nunca saem da sua máquina
- ✅ **Dados seguros**: Nenhum upload para servidores
- ✅ **API opcional**: Maritaca AI apenas se você quiser

### 💪 **Funcionalidades Completas**
- ✅ **Interface intuitiva**: Tkinter nativo do Python
- ✅ **Busca avançada**: Regex com word boundaries
- ✅ **Identificação de empresas**: Regex + API Maritaca (opcional)
- ✅ **Exportação CSV**: Com encoding UTF-8-BOM para Excel
- ✅ **Contexto completo**: Visualização detalhada dos resultados
- ✅ **Tributos predefinidos**: Botões para ISS/ISSQN, IPTU/ITBI, etc.

## 🛠️ Como Usar

### 📋 **Pré-requisitos**
- Python 3.8 ou superior
- Windows, macOS ou Linux

### 🚀 **Opção 1: Executar o Código Python**

1. **Clone o repositório:**
```bash
git clone https://github.com/ARibeiroFIUS/ISS.git
cd ISS
```

2. **Instale as dependências:**
```bash
pip install -r requirements_desktop.txt
```

3. **Execute a aplicação:**
```bash
python app_desktop.py
```

### 📦 **Opção 2: Gerar Executável (.exe)**

1. **Instale as dependências:**
```bash
pip install -r requirements_desktop.txt
```

2. **Execute o script de build:**
```bash
python build_exe.py
```

3. **Encontre o executável em:**
```
AnalisadorTributos_v1.0/AnalisadorTributos.exe
```

## 🎮 **Como Usar a Interface**

### 1. **📁 Seleção de Arquivo**
- Clique em "📂 Procurar"
- Selecione seu PDF de Diário Oficial
- Veja informações do arquivo (nome e tamanho)

### 2. **🔍 Configuração de Tributos**
- **Digite manualmente**: ISS, ISSQN, IPTU, ITBI, etc.
- **Use botões predefinidos**:
  - `ISS/ISSQN`: Para tributos de serviços
  - `IPTU/ITBI`: Para tributos imobiliários
  - `Todos`: Para busca completa

### 3. **🤖 API Maritaca (Opcional)**
- Cole sua chave da API no campo "Chave da API"
- Clique em "💾 Salvar" para persistir
- **Sem chave**: Sistema funciona apenas com regex (já muito eficiente)

### 4. **🚀 Análise**
- Clique em "🚀 Analisar PDF"
- Acompanhe o progresso na barra
- Veja status em tempo real

### 5. **📊 Resultados**
- **Tabela interativa** com todos os resultados
- **Duplo clique** em qualquer linha para ver contexto completo
- **Colunas**: Tributo, Linha, Número, Empresas, Contexto

### 6. **📤 Exportação**
- Clique em "📊 Exportar CSV"
- Escolha local para salvar
- Arquivo compatível com Excel (UTF-8-BOM)

## 🔧 **Configurações Avançadas**

### 🌐 **API Maritaca**
Para melhor identificação de empresas:

1. **Acesse**: https://plataforma.maritaca.ai/chaves-de-api
2. **Crie sua conta** e gere uma chave
3. **Cole na aplicação** e salve
4. **Benefícios**: Identificação mais precisa de nomes de empresas

### 📁 **Arquivo .env**
A aplicação cria automaticamente um arquivo `.env` para salvar configurações:
```
MARITACA_API_KEY=sua_chave_aqui
```

## 🎯 **Tributos Suportados**

### 📋 **Tributos Municipais**
- **ISS**: Imposto Sobre Serviços
- **ISSQN**: Imposto Sobre Serviços de Qualquer Natureza
- **IPTU**: Imposto Predial e Territorial Urbano
- **ITBI**: Imposto de Transmissão de Bens Imóveis

### 📋 **Tributos Federais/Estaduais**
- **ICMS**: Imposto sobre Circulação de Mercadorias e Serviços
- **COFINS**: Contribuição para o Financiamento da Seguridade Social
- **PIS**: Programa de Integração Social
- **CSLL**: Contribuição Social sobre o Lucro Líquido
- **IRPJ**: Imposto de Renda Pessoa Jurídica

### 📋 **Tributos Personalizados**
- Digite qualquer tributo ou termo
- Busca case-insensitive
- Suporte a múltiplos termos separados por vírgula

## 🔍 **Como Funciona a Busca**

### 1. **Extração de Texto**
- Usa `pdfplumber` para extrair texto preservando formatação
- Processa todas as páginas do PDF
- Mantém estrutura de linhas e parágrafos

### 2. **Busca de Tributos**
- **Regex com word boundaries**: `\bISS\b` (evita falsos positivos)
- **Case-insensitive**: Encontra "iss", "ISS", "Iss"
- **Contexto**: Captura 10 linhas antes e depois

### 3. **Identificação de Empresas**
- **Regex patterns**:
  - CNPJ: `XX.XXX.XXX/XXXX-XX`
  - Razão social: Palavras em maiúsculo + LTDA/ME/etc.
  - Nomes próprios em maiúsculo
- **API Maritaca** (opcional): IA para identificação mais precisa

## 📊 **Formato de Exportação CSV**

```csv
Tributo,Linha Encontrada,Número da Linha,Empresas Identificadas,Contexto Completo
ISS,"Empresa ABC Ltda - ISS devido",150,"ABC LTDA; ABC","Contexto completo..."
ISSQN,"Serviços ISSQN 2024",200,"SERVIÇOS XYZ","Contexto completo..."
```

## 🛠️ **Desenvolvimento**

### 📁 **Estrutura do Projeto**
```
ISS/
├── app_desktop.py          # Aplicação principal
├── build_exe.py           # Script para gerar .exe
├── requirements_desktop.txt # Dependências
├── README_DESKTOP.md       # Este arquivo
└── .env                   # Configurações (criado automaticamente)
```

### 🔧 **Tecnologias Utilizadas**
- **Python 3.8+**: Linguagem principal
- **Tkinter**: Interface gráfica nativa
- **pdfplumber**: Extração de texto de PDFs
- **requests**: Comunicação HTTP
- **openai**: Cliente para API Maritaca
- **PyInstaller**: Geração de executáveis

### 🏗️ **Build do Executável**
```bash
# Instala dependências
pip install -r requirements_desktop.txt

# Gera executável
python build_exe.py

# Resultado em:
AnalisadorTributos_v1.0/
├── AnalisadorTributos.exe
└── README.txt
```

## 🆘 **Troubleshooting**

### ❌ **Problemas Comuns**

**1. "Não foi possível extrair texto do PDF"**
- ✅ Verifique se o PDF contém texto (não é apenas imagem)
- ✅ Tente com outro PDF para testar
- ✅ PDFs escaneados precisam de OCR primeiro

**2. "Nenhum tributo encontrado"**
- ✅ Verifique a ortografia dos tributos
- ✅ Use termos exatos como aparecem no PDF
- ✅ Teste com termos mais simples (ex: "ISS" ao invés de "ISS Municipal")

**3. "Erro na API Maritaca"**
- ✅ Verifique se a chave da API está correta
- ✅ Confirme se há conexão com internet
- ✅ Sistema funciona sem API (apenas com regex)

**4. "Executável não abre"**
- ✅ Execute como administrador
- ✅ Verifique antivírus (pode bloquear executáveis Python)
- ✅ Use a versão Python diretamente

### 🔧 **Logs e Debug**
- Execute via Python para ver mensagens de erro
- Verifique arquivo `.env` para configurações
- Teste com PDFs menores primeiro

## 🎉 **Vantagens vs Versão Web**

| Aspecto | Versão Web | Versão Desktop |
|---------|------------|----------------|
| **Timeout** | ❌ 25s máximo | ✅ Sem limite |
| **Tamanho PDF** | ❌ 10MB máximo | ✅ Qualquer tamanho |
| **Páginas** | ❌ 10 máximo | ✅ Todas as páginas |
| **Privacidade** | ❌ Upload necessário | ✅ 100% local |
| **Performance** | ❌ Limitada | ✅ Máxima |
| **Dependência** | ❌ Internet obrigatória | ✅ Funciona offline |
| **Instalação** | ✅ Não precisa | ❌ Precisa instalar |
| **Atualizações** | ✅ Automáticas | ❌ Manuais |

## 🚀 **Próximos Passos**

1. **Teste a aplicação** com seus PDFs
2. **Configure a API Maritaca** se desejar (opcional)
3. **Gere o executável** para distribuição
4. **Compartilhe** com sua equipe

---

**✨ Versão Desktop: Máxima performance, privacidade total, sem limitações!** 