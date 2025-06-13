# 🚀 Instruções Rápidas - Analisador de Tributos

## ⚡ Inicio Rápido (3 minutos)

### 1. Instale as dependências:
```bash
pip3 install -r requirements.txt
```

### 2. Configure a API Maritaca (opcional, mas recomendado):
```bash
# Copie o arquivo de exemplo
cp env.example .env

# Edite .env e adicione sua chave:
# MARITACA_API_KEY=sua_chave_aqui
```

### 3. Execute a aplicação:
```bash
python3 app.py
```

### 4. Acesse: http://localhost:5000

---

## 📱 Como Usar

1. **Upload**: Selecione um PDF (até 50MB)
2. **Tributos**: Digite: `ISS, ISSQN, IPTU, ITBI`
3. **Analisar**: Clique no botão azul
4. **Resultados**: Veja a tabela e use os filtros
5. **Exportar**: Baixe em CSV

---

## 🌐 Deploy Render.com (5 minutos)

1. **Suba para Git**: Faça commit do código
2. **Render**: Conecte seu repositório 
3. **Configurar**:
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn --bind 0.0.0.0:$PORT app:app`
4. **Variáveis**: Adicione `MARITACA_API_KEY`
5. **Deploy**: Clique em "Create Web Service"

---

## 🔑 API Maritaca (gratuita)

1. Acesse: https://chat.maritaca.ai
2. Crie conta grátis
3. Obtenha API key
4. Adicione no `.env` ou Render

---

## ✅ Funcionando?

- ✅ A aplicação iniciou em localhost:5000?
- ✅ O upload de PDF funciona?
- ✅ A busca por tributos encontra resultados?
- ✅ A exportação CSV funciona?

Se todos "sim" → **Pronto para produção! 🎉**

---

## 🆘 Problemas Comuns

**Erro de dependência**: `pip3 install flask pdfplumber requests python-dotenv`

**PDF sem texto**: Use PDFs com texto pesquisável (não só imagens)

**API Maritaca**: Funciona sem, mas identifica menos empresas

**Deploy falha**: Verifique se requirements.txt está correto

---

## 📞 Suporte Rápido

1. Verifique os logs da aplicação
2. Teste localmente primeiro
3. Confirme as variáveis de ambiente
4. Use PDF de teste pequeno primeiro 