# 📄 Analisador de Tributos - Diário Oficial

Uma aplicação web simples e eficiente para análise automatizada de PDFs de Diários Oficiais Municipais, focada na identificação de tributos específicos e extração de informações sobre empresas relacionadas.

## 🚀 Funcionalidades

- **Upload de PDFs**: Suporte para arquivos até 50MB
- **Busca Inteligente**: Identificação precisa de tributos usando regex com word boundaries
- **Extração de Entidades**: Reconhecimento de empresas usando NER (regex + Maritaca AI)
- **Interface Responsiva**: Design moderno e intuitivo
- **Filtros Avançados**: Filtragem por tributo e busca por empresa
- **Exportação**: Download dos resultados em formato CSV
- **Contexto Completo**: Visualização de trechos com contexto expandido

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python 3.8+ com Flask
- **Frontend**: HTML5, CSS3, JavaScript (Bootstrap 5)
- **Processamento PDF**: pdfplumber
- **NER**: Maritaca AI API + regex patterns
- **Deploy**: Render.com (recomendado)

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Conta no Maritaca AI (para obter API key)
- Git (para clonar o repositório)

## 🔧 Instalação Local

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd analisador-tributos
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente
```bash
# Copie o arquivo de exemplo
cp env.example .env

# Edite o arquivo .env com suas configurações
# No mínimo, configure a MARITACA_API_KEY
```

### 5. Execute a aplicação
```bash
python app.py
```

A aplicação estará disponível em: `http://localhost:5000`

## 🔑 Configuração da API Maritaca

1. Acesse [https://chat.maritaca.ai](https://chat.maritaca.ai)
2. Crie uma conta ou faça login
3. Obtenha sua API key
4. Adicione a chave no arquivo `.env`:
```
MARITACA_API_KEY=sua_chave_aqui
```

## 🌐 Deploy no Render.com

### 1. Preparação
- Certifique-se de que o código está em um repositório Git (GitHub, GitLab, etc.)
- Remova arquivos .env do repositório (já está no .gitignore)

### 2. Configuração no Render
1. Acesse [render.com](https://render.com) e crie uma conta
2. Clique em "New" → "Web Service"
3. Conecte seu repositório Git
4. Configure:
   - **Name**: analisador-tributos (ou nome de sua escolha)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT app:app`

### 3. Variáveis de Ambiente
No painel do Render, adicione as variáveis:
- `MARITACA_API_KEY`: sua chave da API
- `SECRET_KEY`: uma chave secreta aleatória
- `FLASK_ENV`: production

### 4. Deploy
- Clique em "Create Web Service"
- Aguarde o deploy (pode levar alguns minutos)
- Sua aplicação estará disponível na URL fornecida pelo Render

## 📖 Como Usar

### 1. Upload do PDF
- Selecione um arquivo PDF de até 50MB
- O PDF deve conter texto pesquisável (não apenas imagens)

### 2. Especificar Tributos
- Digite os tributos que deseja buscar, separados por vírgula
- Exemplos: `ISS, ISSQN, IPTU, ITBI, ICMS`

### 3. Análise
- Clique em "Analisar PDF"
- Aguarde o processamento (mostrado na barra de progresso)

### 4. Resultados
- Visualize os trechos encontrados na tabela
- Use os filtros para refinar os resultados
- Clique em "Ver Contexto" para mais detalhes
- Exporte os resultados em CSV

## 🔍 Como Funciona

### Extração de Texto
- Utiliza `pdfplumber` para extrair texto preservando formatação
- Verifica se o PDF contém texto pesquisável

### Busca de Tributos
- Regex com word boundaries para evitar falsos positivos
- Case-insensitive matching
- Captura contexto (7 linhas antes e depois)

### Identificação de Empresas
1. **Regex básica**: Identifica padrões como CNPJ, LTDA, S/A
2. **Maritaca AI**: NER avançado para organizações
3. **Combinação**: Merge dos resultados removendo duplicatas

## 📁 Estrutura do Projeto

```
analisador-tributos/
├── app.py                 # Aplicação principal Flask
├── requirements.txt       # Dependências Python
├── README.md             # Documentação
├── .gitignore            # Arquivos ignorados pelo Git
├── env.example           # Exemplo de variáveis de ambiente
├── templates/
│   └── index.html        # Interface principal
├── static/
│   ├── css/
│   │   └── styles.css    # Estilos customizados
│   └── js/
│       └── app.js        # JavaScript da aplicação
└── uploads/              # Pasta temporária (criada automaticamente)
```

## 🔒 Segurança

- ✅ Variáveis de ambiente para chaves de API
- ✅ Sanitização de nomes de arquivos
- ✅ Validação de tipos e tamanhos de arquivo
- ✅ Remoção automática de arquivos temporários
- ✅ Limite de tamanho de upload (50MB)
- ✅ Timeout para chamadas de API
- ✅ .gitignore configurado para arquivos sensíveis

## 🚨 Tratamento de Erros

- **PDF sem texto**: Informa que o arquivo deve ser pesquisável
- **Tributos não encontrados**: Notifica quando nenhum tributo é localizado
- **Arquivo muito grande**: Rejeita arquivos acima de 50MB
- **Erro de API**: Fallback para regex quando Maritaca AI falha
- **Timeout**: Configurado timeout de 30s para APIs externas

## 📊 Exemplos de Uso

### Tributos Comuns
- `ISS` - Imposto Sobre Serviços
- `ISSQN` - Imposto Sobre Serviços de Qualquer Natureza
- `IPTU` - Imposto Predial e Territorial Urbano
- `ITBI` - Imposto de Transmissão de Bens Imóveis
- `ICMS` - Imposto sobre Circulação de Mercadorias

### Padrões de Empresas Identificadas
- CNPJs: `12.345.678/0001-90`
- Razões sociais: `EMPRESA EXEMPLO LTDA`
- Sociedades anônimas: `COMPANHIA EXEMPLO S/A`

## 🔄 Expansões Futuras

### Funcionalidades Sugeridas
- **OCR**: Suporte para PDFs com apenas imagens
- **Múltiplas APIs**: Integração com outras ferramentas de NER
- **Base de dados**: Armazenamento de histórico de análises
- **Autenticação**: Sistema de usuários e controle de acesso
- **API REST**: Endpoints para integração com outros sistemas
- **Análise em lote**: Processamento de múltiplos PDFs
- **Dashboard**: Estatísticas e relatórios avançados
- **Webhooks**: Notificações automáticas
- **Cache**: Sistema de cache para análises repetidas
- **Logs avançados**: Sistema de auditoria completo

### Melhorias Técnicas
- **Tests**: Implementar testes unitários e de integração
- **Docker**: Containerização da aplicação
- **Redis**: Cache e sessões
- **PostgreSQL**: Banco de dados robusto
- **Celery**: Processamento assíncrono
- **Monitoring**: Integração com ferramentas de monitoramento

## 🐛 Problemas Conhecidos

- A API Maritaca AI pode ter limitações de rate limiting
- PDFs muito complexos podem demorar para processar
- Regex pode gerar falsos positivos em casos específicos

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique se todas as dependências estão instaladas
2. Confirme se a API key do Maritaca está configurada
3. Consulte os logs da aplicação para erros específicos

## 📄 Licença

Este projeto é fornecido como MVP para análise de tributos em Diários Oficiais. Use e modifique conforme necessário.

---

**Desenvolvido para automatizar a análise de processos administrativos relativos a tributos específicos em PDFs de Diários Oficiais, identificando empresas mencionadas e apresentando resultados para consulta rápida e exportação.** 