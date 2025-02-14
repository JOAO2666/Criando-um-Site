document.addEventListener('DOMContentLoaded', function () {
    // Variáveis globais
    const searchInput = document.getElementById('searchInput');
    const addTaskBtn = document.getElementById('addTaskBtn');
    const taskModal = document.getElementById('taskModal');
    const closeModalBtns = document.querySelectorAll('.close-modal');
    const sortSelect = document.getElementById('sortTasks');
    const tasksGrid = document.querySelector('.tasks-grid');
    const flashMessages = document.querySelectorAll('.flash-message');
    const authTabs = document.querySelectorAll('.auth-tab');
    const authForms = document.querySelectorAll('.auth-form');
    const passwordToggles = document.querySelectorAll('.toggle-password');

    // Sistema de busca
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function () {
            const searchTerm = this.value.toLowerCase();
            const taskCards = document.querySelectorAll('.task-card');

            taskCards.forEach(card => {
                const title = card.querySelector('.task-title').textContent.toLowerCase();
                const description = card.querySelector('.task-description')?.textContent.toLowerCase() || '';
                const category = card.querySelector('.task-category').textContent.toLowerCase();

                if (title.includes(searchTerm) || description.includes(searchTerm) || category.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        }, 300));
    }

    // Modal de Nova Tarefa
    if (addTaskBtn) {
        addTaskBtn.addEventListener('click', () => {
            taskModal.classList.add('active');
            document.body.style.overflow = 'hidden';
        });
    }

    closeModalBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            taskModal.classList.remove('active');
            document.body.style.overflow = 'auto';
        });
    });

    // Fechar modal ao clicar fora
    window.addEventListener('click', (e) => {
        if (e.target === taskModal) {
            taskModal.classList.remove('active');
            document.body.style.overflow = 'auto';
        }
    });

    // Ordenação de tarefas
    if (sortSelect) {
        sortSelect.addEventListener('change', () => {
            const tasks = Array.from(document.querySelectorAll('.task-card'));
            const sortBy = sortSelect.value;

            tasks.sort((a, b) => {
                switch (sortBy) {
                    case 'priority':
                        const priorityOrder = { 'Urgente': 0, 'Alta': 1, 'Média': 2, 'Baixa': 3 };
                        const priorityA = a.dataset.priority;
                        const priorityB = b.dataset.priority;
                        return priorityOrder[priorityA] - priorityOrder[priorityB];

                    case 'date':
                        const dateA = new Date(a.querySelector('.task-due-date')?.textContent || '9999-12-31');
                        const dateB = new Date(b.querySelector('.task-due-date')?.textContent || '9999-12-31');
                        return dateA - dateB;

                    case 'category':
                        const categoryA = a.querySelector('.task-category').textContent;
                        const categoryB = b.querySelector('.task-category').textContent;
                        return categoryA.localeCompare(categoryB);
                }
            });

            tasksGrid.innerHTML = '';
            tasks.forEach(task => tasksGrid.appendChild(task));
        });
    }

    // Animação das mensagens flash
    flashMessages.forEach(message => {
        // Adiciona animação de entrada
        message.style.animation = 'slideIn 0.5s ease-out';

        // Configura o tempo de exibição
        setTimeout(() => {
            message.style.animation = 'slideOut 0.5s ease-out forwards';
            setTimeout(() => message.remove(), 500);
        }, 5000);

        // Botão de fechar
        const closeBtn = message.querySelector('.close-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                message.style.animation = 'slideOut 0.5s ease-out forwards';
                setTimeout(() => message.remove(), 500);
            });
        }
    });

    // Tabs de autenticação
    authTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetForm = tab.dataset.tab;

            // Atualiza classes ativas
            authTabs.forEach(t => t.classList.remove('active'));
            authForms.forEach(f => f.classList.remove('active'));

            tab.classList.add('active');
            document.getElementById(`${targetForm}Form`).classList.add('active');
        });
    });

    // Toggle de senha
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', () => {
            const input = toggle.previousElementSibling;
            const icon = toggle.querySelector('i');

            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    });

    // Validação de formulários
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('error');

                    // Remove a classe de erro quando o usuário começar a digitar
                    field.addEventListener('input', () => {
                        field.classList.remove('error');
                    }, { once: true });
                }
            });

            if (!isValid) {
                e.preventDefault();
                showError('Por favor, preencha todos os campos obrigatórios.');
            }
        });
    });

    // Funções auxiliares
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func.apply(this, args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    function showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'flash-message error';
        errorDiv.innerHTML = `
            <i class="fas fa-exclamation-circle"></i>
            ${message}
            <button class="close-btn"><i class="fas fa-times"></i></button>
        `;

        document.querySelector('.flash-messages').appendChild(errorDiv);

        // Remove após 5 segundos
        setTimeout(() => {
            errorDiv.style.animation = 'slideOut 0.5s ease-out forwards';
            setTimeout(() => errorDiv.remove(), 500);
        }, 5000);
    }

    // Animações de hover nas task cards
    const taskCards = document.querySelectorAll('.task-card');
    taskCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-5px)';
            card.style.boxShadow = 'var(--shadow-lg)';
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
            card.style.boxShadow = 'var(--shadow-md)';
        });
    });
}); 