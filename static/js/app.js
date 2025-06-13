// JavaScript para o Analisador de Tributos
class TributosAnalyzer {
    constructor() {
        this.results = [];
        this.filteredResults = [];
        this.init();
    }

    init() {
        this.bindEvents();
        this.setupProgressAnimation();
    }

    bindEvents() {
        // Formulário de upload
        document.getElementById('uploadForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleUpload();
        });

        // Botão de exportar
        document.getElementById('exportBtn').addEventListener('click', () => {
            this.exportResults();
        });

        // Filtros
        document.getElementById('filterTributo').addEventListener('change', () => {
            this.applyFilters();
        });

        document.getElementById('filterEmpresa').addEventListener('input', () => {
            this.applyFilters();
        });

        // Validação de arquivo
        document.getElementById('pdfFile').addEventListener('change', (e) => {
            this.validateFile(e.target.files[0]);
        });
    }

    validateFile(file) {
        const alertContainer = document.getElementById('alertContainer');
        alertContainer.innerHTML = '';

        if (!file) return;

        // Verifica o tipo de arquivo
        if (file.type !== 'application/pdf') {
            this.showAlert('Apenas arquivos PDF são permitidos.', 'danger');
            document.getElementById('pdfFile').value = '';
            return;
        }

        // Verifica o tamanho (50MB)
        const maxSize = 50 * 1024 * 1024;
        if (file.size > maxSize) {
            this.showAlert('O arquivo é muito grande. Tamanho máximo: 50MB.', 'danger');
            document.getElementById('pdfFile').value = '';
            return;
        }

        // Mostra informações do arquivo
        const fileSize = (file.size / (1024 * 1024)).toFixed(2);
        this.showAlert(`Arquivo selecionado: ${file.name} (${fileSize} MB)`, 'info');
    }

    async handleUpload() {
        const formData = new FormData();
        const fileInput = document.getElementById('pdfFile');
        const tributos = document.getElementById('tributos').value;

        if (!fileInput.files[0]) {
            this.showAlert('Selecione um arquivo PDF.', 'danger');
            return;
        }

        if (!tributos.trim()) {
            this.showAlert('Digite os tributos para buscar.', 'danger');
            return;
        }

        formData.append('file', fileInput.files[0]);
        formData.append('tributos', tributos);

        this.showProgress();
        this.disableForm(true);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok && result.success) {
                this.results = result.results;
                this.filteredResults = [...this.results];
                this.displayResults();
                this.setupFilters();
                this.showAlert(`Análise concluída! ${result.total_encontrados} trechos encontrados.`, 'success');
            } else {
                this.showAlert(result.error || 'Erro ao processar o arquivo.', 'danger');
            }
        } catch (error) {
            console.error('Erro:', error);
            this.showAlert('Erro de conexão. Tente novamente.', 'danger');
        } finally {
            this.hideProgress();
            this.disableForm(false);
        }
    }

    showProgress() {
        const progressSection = document.getElementById('progressSection');
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');

        progressSection.style.display = 'block';
        progressSection.classList.add('fade-in');

        // Simula progresso
        let progress = 0;
        const steps = [
            { progress: 20, text: 'Extraindo texto do PDF...' },
            { progress: 50, text: 'Buscando tributos...' },
            { progress: 80, text: 'Identificando empresas...' },
            { progress: 100, text: 'Finalizando análise...' }
        ];

        const interval = setInterval(() => {
            if (progress < steps.length) {
                const step = steps[progress];
                progressBar.style.width = step.progress + '%';
                progressText.textContent = step.text;
                progress++;
            } else {
                clearInterval(interval);
            }
        }, 1000);
    }

    hideProgress() {
        const progressSection = document.getElementById('progressSection');
        setTimeout(() => {
            progressSection.style.display = 'none';
        }, 500);
    }

    setupProgressAnimation() {
        // Animação contínua da barra de progresso
        setInterval(() => {
            const progressBar = document.getElementById('progressBar');
            if (progressBar && progressBar.parentElement.parentElement.parentElement.style.display !== 'none') {
                if (progressBar.style.width === '100%') {
                    progressBar.style.width = '0%';
                }
            }
        }, 3000);
    }

    disableForm(disabled) {
        const form = document.getElementById('uploadForm');
        const inputs = form.querySelectorAll('input, button');
        inputs.forEach(input => {
            input.disabled = disabled;
        });

        const analyzeBtn = document.getElementById('analyzeBtn');
        if (disabled) {
            analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Analisando...';
            analyzeBtn.classList.add('loading');
        } else {
            analyzeBtn.innerHTML = '<i class="fas fa-analytics me-2"></i>Analisar PDF';
            analyzeBtn.classList.remove('loading');
        }
    }

    displayResults() {
        const resultsSection = document.getElementById('resultsSection');
        const tbody = document.getElementById('resultsTableBody');
        const totalResults = document.getElementById('totalResults');

        // Mostra seção de resultados
        resultsSection.style.display = 'block';
        resultsSection.classList.add('fade-in');

        // Atualiza contador
        totalResults.textContent = `${this.filteredResults.length} resultados`;

        // Limpa tabela
        tbody.innerHTML = '';

        // Popula tabela
        this.filteredResults.forEach((result, index) => {
            const row = this.createResultRow(result, index);
            tbody.appendChild(row);
        });

        // Scroll suave para os resultados
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    createResultRow(result, index) {
        const row = document.createElement('tr');
        
        const empresas = result.empresas_identificadas.length > 0 
            ? result.empresas_identificadas.join(', ')
            : 'Nenhuma identificada';

        const linhaDisplay = result.linha_encontrada.length > 100 
            ? result.linha_encontrada.substring(0, 100) + '...'
            : result.linha_encontrada;

        row.innerHTML = `
            <td>
                <span class="badge bg-primary">${result.tributo}</span>
            </td>
            <td class="text-truncate-custom" title="${result.linha_encontrada}">
                ${linhaDisplay}
            </td>
            <td>
                <span class="badge bg-secondary">${result.linha_numero}</span>
            </td>
            <td class="text-truncate-custom" title="${empresas}">
                ${empresas}
            </td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="tributosAnalyzer.showContext(${index})">
                    <i class="fas fa-eye me-1"></i>Ver Contexto
                </button>
            </td>
        `;

        return row;
    }

    showContext(index) {
        const result = this.filteredResults[index];
        
        document.getElementById('modalTributo').textContent = result.tributo;
        document.getElementById('modalLinha').textContent = result.linha_numero;
        document.getElementById('modalEmpresas').textContent = 
            result.empresas_identificadas.length > 0 
                ? result.empresas_identificadas.join(', ')
                : 'Nenhuma identificada';
        document.getElementById('modalContexto').textContent = result.contexto;

        const modal = new bootstrap.Modal(document.getElementById('contextModal'));
        modal.show();
    }

    setupFilters() {
        // Popula filtro de tributos
        const filterTributo = document.getElementById('filterTributo');
        const tributos = [...new Set(this.results.map(r => r.tributo))];
        
        filterTributo.innerHTML = '<option value="">Todos os tributos</option>';
        tributos.forEach(tributo => {
            const option = document.createElement('option');
            option.value = tributo;
            option.textContent = tributo;
            filterTributo.appendChild(option);
        });
    }

    applyFilters() {
        const tributoFilter = document.getElementById('filterTributo').value;
        const empresaFilter = document.getElementById('filterEmpresa').value.toLowerCase();

        this.filteredResults = this.results.filter(result => {
            const matchTributo = !tributoFilter || result.tributo === tributoFilter;
            const matchEmpresa = !empresaFilter || 
                result.empresas_identificadas.some(empresa => 
                    empresa.toLowerCase().includes(empresaFilter)
                ) ||
                result.linha_encontrada.toLowerCase().includes(empresaFilter) ||
                result.contexto.toLowerCase().includes(empresaFilter);

            return matchTributo && matchEmpresa;
        });

        this.displayResults();
    }

    async exportResults() {
        if (this.filteredResults.length === 0) {
            this.showAlert('Nenhum resultado para exportar.', 'warning');
            return;
        }

        try {
            const response = await fetch('/export_csv', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ results: this.filteredResults })
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `analise_tributos_${new Date().toISOString().slice(0, 10)}.csv`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                this.showAlert('Arquivo CSV exportado com sucesso!', 'success');
            } else {
                this.showAlert('Erro ao exportar arquivo.', 'danger');
            }
        } catch (error) {
            console.error('Erro na exportação:', error);
            this.showAlert('Erro ao exportar arquivo.', 'danger');
        }
    }

    showAlert(message, type) {
        const alertContainer = document.getElementById('alertContainer');
        
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            <i class="fas fa-${this.getAlertIcon(type)} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        alertContainer.appendChild(alertDiv);

        // Remove alerta automaticamente após 5 segundos (exceto para erros)
        if (type !== 'danger') {
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.remove();
                }
            }, 5000);
        }
    }

    getAlertIcon(type) {
        const icons = {
            'success': 'check-circle',
            'danger': 'exclamation-triangle',
            'warning': 'exclamation-circle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
}

// Inicializa a aplicação quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', () => {
    window.tributosAnalyzer = new TributosAnalyzer();
    
    // Adiciona tooltips do Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Animação de entrada
    document.body.classList.add('fade-in');
});

// Funções utilitárias
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(date) {
    return new Intl.DateTimeFormat('pt-BR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
}

// Tratamento de erros globais
window.addEventListener('error', (e) => {
    console.error('Erro JavaScript:', e.error);
    if (window.tributosAnalyzer) {
        window.tributosAnalyzer.showAlert('Ocorreu um erro inesperado. Recarregue a página.', 'danger');
    }
});

// Prevenção de comportamento padrão para drag & drop
document.addEventListener('dragover', (e) => {
    e.preventDefault();
});

document.addEventListener('drop', (e) => {
    e.preventDefault();
}); 