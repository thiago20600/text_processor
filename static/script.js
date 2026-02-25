// Elementos del DOM
const sidebarSummaries = document.getElementById('sidebarSummaries');
const summaryList = document.getElementById('summaryList');
const textForm = document.getElementById('textForm');
const textInput = document.getElementById('textInput') || document.getElementById('texto');
const languageSelect = document.getElementById('languageSelect') || document.getElementById('idioma');
const charCount = document.getElementById('charCount');
const btnText = document.getElementById('btnText');
const spinner = document.getElementById('spinner');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');
const loadingSection = document.getElementById('loadingSection');
const formSection = document.querySelector('.form-section');
const imageInput = document.getElementById('imageInput');
const ocrBtn = document.getElementById('ocrBtn');
const ocrStatus = document.getElementById('ocrStatus');
const pdfInput = document.getElementById('pdfInput');
const pdfOcrBtn = document.getElementById('pdfOcrBtn');
const pdfOcrStatus = document.getElementById('pdfOcrStatus');
const saveSummaryBtn = document.getElementById('saveSummaryBtn');
const saveSummaryStatus = document.getElementById('saveSummaryStatus');
const authModal = document.getElementById('authModal');
const closeAuthModal = document.getElementById('closeAuthModal');
const authForm = document.getElementById('authForm');
const authUsername = document.getElementById('authUsername');
const authPassword = document.getElementById('authPassword');
const authSubmitBtn = document.getElementById('authSubmitBtn');
const authTitle = document.getElementById('authTitle');
const authSwitchText = document.getElementById('authSwitchText');
const switchToRegister = document.getElementById('switchToRegister');
const authStatus = document.getElementById('authStatus');
const headerRegisterBtn = document.getElementById('headerRegisterBtn');
const headerLoginBtn = document.getElementById('headerLoginBtn');
const headerLogoutBtn = document.getElementById('headerLogoutBtn');

function updateAuthButtons() {
    const hasToken = !!localStorage.getItem('jwt');
    if (headerRegisterBtn) headerRegisterBtn.style.display = hasToken ? 'none' : '';
    if (headerLoginBtn) headerLoginBtn.style.display = hasToken ? 'none' : '';
    if (headerLogoutBtn) headerLogoutBtn.style.display = hasToken ? '' : 'none';
}

// OCR: Leer texto de imagen
if (ocrBtn && imageInput) {
    ocrBtn.addEventListener('click', async function() {
        if (!imageInput.files || imageInput.files.length === 0) {
            showError('Selecciona una imagen primero');
            return;
        }
        ocrBtn.disabled = true;
        if (ocrStatus) {
            ocrStatus.style.display = 'inline';
            ocrStatus.textContent = '⏳ Extrayendo texto de la imagen...';
        }
        const formData = new FormData();
        formData.append('file', imageInput.files[0]);
        try {
            const response = await fetch('/api/ocr', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            if (data.success) {
                textInput.value = data.text;
                updateCharCount();
                if (ocrStatus) ocrStatus.textContent = '✅ Texto extraído de la imagen';
            } else {
                if (ocrStatus) ocrStatus.textContent = '❌ ' + (data.error || 'No se pudo extraer texto');
            }
        } catch (err) {
            if (ocrStatus) ocrStatus.textContent = '❌ Error al procesar la imagen';
        } finally {
            ocrBtn.disabled = false;
        }
        if (ocrStatus) {
            setTimeout(() => { ocrStatus.style.display = 'none'; }, 3500);
        }
    });
}

// OCR: Leer texto de PDF
if (pdfOcrBtn && pdfInput) {
    pdfOcrBtn.addEventListener('click', async function() {
        if (!pdfInput.files || pdfInput.files.length === 0) {
            showError('Selecciona un PDF primero');
            return;
        }
        pdfOcrBtn.disabled = true;
        if (pdfOcrStatus) {
            pdfOcrStatus.style.display = 'inline';
            pdfOcrStatus.textContent = '⏳ Extrayendo texto del PDF...';
        }
        const formData = new FormData();
        formData.append('file', pdfInput.files[0]);
        try {
            const response = await fetch('/api/pdf-ocr', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            if (data.success) {
                textInput.value = data.text;
                updateCharCount();
                if (pdfOcrStatus) pdfOcrStatus.textContent = '✅ Texto extraído del PDF';
            } else {
                if (pdfOcrStatus) pdfOcrStatus.textContent = '❌ ' + (data.error || 'No se pudo extraer texto');
            }
        } catch (err) {
            if (pdfOcrStatus) pdfOcrStatus.textContent = '❌ Error al procesar el PDF';
        } finally {
            pdfOcrBtn.disabled = false;
        }
        if (pdfOcrStatus) {
            setTimeout(() => { pdfOcrStatus.style.display = 'none'; }, 3500);
        }
    });
}

// Event Listeners
if (textForm) {
    textForm.addEventListener('submit', handleFormSubmit);
}
if (textInput) {
    textInput.addEventListener('input', updateCharCount);
}

// Guardar idioma seleccionado en localStorage
if (languageSelect) {
    languageSelect.addEventListener('change', function() {
        localStorage.setItem('selectedLanguage', this.value);
    });
    
    // Restaurar idioma guardado
    const savedLanguage = localStorage.getItem('selectedLanguage');
    if (savedLanguage) {
        languageSelect.value = savedLanguage;
    }
}

// Actualizar contador de caracteres
function updateCharCount() {
    if (!textInput || !charCount) return;
    const count = textInput.value.length;
    charCount.textContent = count;
    
    // Cambiar color si se acerca al límite
    if (count > 9000) {
        charCount.parentElement.style.color = 'var(--warning-color)';
    } else if (count > 9500) {
        charCount.parentElement.style.color = 'var(--danger-color)';
    } else {
        charCount.parentElement.style.color = 'var(--text-light)';
    }
}

// Manejar envío del formulario
async function handleFormSubmit(e) {
    e.preventDefault();
    if (!textInput || !textForm) return;
    
    const text = textInput.value.trim();
    const language = languageSelect ? languageSelect.value : 'es';
    
    // Validaciones
    if (!text) {
        showError('Por favor ingresa un texto');
        return;
    }
    
    if (text.length < 10) {
        showError('El texto debe tener al menos 10 caracteres');
        return;
    }
    
    if (text.length > 10000) {
        showError('El texto no puede exceder 10000 caracteres');
        return;
    }
    
    // Mostrar sección de carga
    hideAllSections();
    if (loadingSection) loadingSection.style.display = 'block';
    textForm.style.display = 'none';
    
    // Deshabilitar botón
    const submitBtn = textForm.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    if (spinner) spinner.style.display = 'inline-block';
    if (btnText) btnText.textContent = 'Procesando...';
    
    try {
        // Enviar solicitud al backend con idioma
        const response = await fetch('/api/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                text: text,
                language: language
            })
        });
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            displayResults(data);
        } else {
            showError(data.error || 'Error desconocido al procesar el texto');
        }
        
    } catch (error) {
        console.error('Error:', error);
        showError(`Error al procesar: ${error.message}`);
    } finally {
        // Rehabilitar botón
        submitBtn.disabled = false;
        if (spinner) spinner.style.display = 'none';
        if (btnText) btnText.textContent = '🚀 Procesar texto';
    }
}

// Mostrar resultados
function displayResults(data) {
    hideAllSections();
    if (resultsSection) resultsSection.style.display = 'block';
    
    // Poblar resumen
    const summaryDiv = document.getElementById('summary');
    if (summaryDiv) {
        summaryDiv.textContent = data.summary || 'No se generó resumen';
    }
    
    // Poblar puntos clave (puede ser array o string)
    const keyPointsDiv = document.getElementById('keyPoints');
    if (keyPointsDiv && Array.isArray(data.key_points)) {
        keyPointsDiv.innerHTML = data.key_points.map(point => `<li>${point}</li>`).join('');
    } else if (keyPointsDiv) {
        keyPointsDiv.textContent = data.key_points || 'No se generaron puntos clave';
    }
    
    // Poblar preguntas (puede ser array o string)
    const questionsDiv = document.getElementById('questions');
    if (questionsDiv && Array.isArray(data.questions)) {
        questionsDiv.innerHTML = data.questions.map(q => `<li>${q}</li>`).join('');
    } else if (questionsDiv) {
        questionsDiv.textContent = data.questions || 'No se generaron preguntas';
    }
    
    // Scroll a los resultados
    setTimeout(() => {
        if (resultsSection) {
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }, 100);
}

// Mostrar error
function showError(message) {
    hideAllSections();
    if (errorSection) errorSection.style.display = 'block';
    
    const errorMessage = document.getElementById('errorMessage');
    if (errorMessage) errorMessage.textContent = message;
    
    textForm.style.display = 'block';
    
    // Scroll al error
    setTimeout(() => {
        if (errorSection) {
            errorSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }, 100);
}

// Ocultar todas las secciones de resultados
function hideAllSections() {
    if (resultsSection) resultsSection.style.display = 'none';
    if (errorSection) errorSection.style.display = 'none';
    if (loadingSection) loadingSection.style.display = 'none';
    if (formSection) formSection.style.display = 'block';
}

// Resetear formulario
function resetForm() {
    if (!textInput) return;
    textInput.value = '';
    if (charCount) charCount.textContent = '0';
    if (textForm) textForm.style.display = 'block';
    hideAllSections();
    textInput.focus();
}

// Copiar al portapapeles
async function copyToClipboard(elementId, triggerButton = null) {
    try {
        const element = document.getElementById(elementId);
        if (!element) return;
        const text = element.textContent;
        
        // Intentar usar la API moderna
        if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(text);
            showCopyFeedback(triggerButton);
        } else {
            // Fallback para navegadores antiguos
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            showCopyFeedback(triggerButton);
        }
    } catch (error) {
        console.error('Error al copiar:', error);
        alert('No se pudo copiar el texto');
    }
}

// Mostrar feedback de copia
function showCopyFeedback(btn) {
    if (!btn) return;
    const originalText = btn.textContent;
    btn.textContent = '✓ Copiado!';
    btn.style.backgroundColor = 'var(--secondary-color)';
    btn.style.color = 'white';
    
    setTimeout(() => {
        btn.textContent = originalText;
        btn.style.backgroundColor = '';
        btn.style.color = '';
    }, 2000);
}

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
    if (textInput) textInput.focus();
    updateAuthButtons();
    loadUserSummaries();
});

async function loadUserSummaries() {
    if (!summaryList) return;
    const jwt = localStorage.getItem('jwt');
    if (!jwt) {
        summaryList.innerHTML = '<li style="color:var(--text-light);">Inicia sesión para ver tus resúmenes</li>';
        return;
    }
    try {
        const response = await fetch('/api/my-summaries', {
            method: 'GET',
            headers: {
                'Authorization': 'Bearer ' + jwt
            }
        });
        const data = await response.json();
        if (data.success && Array.isArray(data.summaries)) {
            if (data.summaries.length === 0) {
                summaryList.innerHTML = '<li style="color:var(--text-light);">No tienes resúmenes guardados</li>';
                return;
            }
            summaryList.innerHTML = '';
            data.summaries.forEach((item, idx) => {
                const li = document.createElement('li');
                li.textContent = item.title || 'Sin título';
                li.dataset.idx = idx;
                li.style.cursor = 'pointer';
                li.onclick = () => showSummaryDetail(item, li);
                summaryList.appendChild(li);
            });
        } else {
            summaryList.innerHTML = '<li style="color:var(--danger-color);">Error al cargar resúmenes</li>';
        }
    } catch (err) {
        summaryList.innerHTML = '<li style="color:var(--danger-color);">Error de red</li>';
    }
}

function parseStoredList(value) {
    if (!value) return [];

    if (Array.isArray(value)) {
        return value.map(v => String(v).trim()).filter(Boolean);
    }

    const raw = String(value).trim();
    if (!raw) return [];

    if (raw.startsWith('[') && raw.endsWith(']')) {
        try {
            const parsed = JSON.parse(raw);
            if (Array.isArray(parsed)) {
                return parsed.map(v => String(v).trim()).filter(Boolean);
            }
        } catch (_) {
            // continúa a parseo por líneas
        }
    }

    const lines = raw
        .split(/\r?\n+/)
        .map(line => line.replace(/^[-*•]\s*/, '').trim())
        .filter(Boolean);

    return lines;
}

function renderList(elementId, items) {
    const container = document.getElementById(elementId);
    if (!container) return;
    container.innerHTML = '';

    items.forEach(item => {
        const li = document.createElement('li');
        li.textContent = item;
        container.appendChild(li);
    });
}

function showSummaryDetail(item, li) {
    if (!summaryList) return;
    // Quitar clase activa de otros
    Array.from(summaryList.children).forEach(el => el.classList.remove('active'));
    li.classList.add('active');
    // Mostrar datos en resultados
    hideAllSections();
    resultsSection.style.display = 'block';

    const summary = item && item.summary ? String(item.summary) : '';
    const keyPoints = parseStoredList(item ? item.key_points : '');
    const questions = parseStoredList(item ? item.questions : '');

    const summaryEl = document.getElementById('summary');
    if (summaryEl) summaryEl.textContent = summary;

    renderList('keyPoints', keyPoints);
    renderList('questions', questions);

    setTimeout(() => {
        if (resultsSection) {
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }, 100);
}

// Mostrar modal de login/registro si no hay token
function showAuthModal(isRegister = false) {
    if (!authModal || !authTitle || !authSubmitBtn || !authSwitchText || !authStatus || !authForm) return;
    authModal.style.display = 'block';
    authTitle.textContent = isRegister ? 'Registrarse' : 'Iniciar sesión';
    authSubmitBtn.textContent = isRegister ? 'Registrarse' : 'Entrar';
    authSwitchText.innerHTML = isRegister
        ? '¿Ya tienes cuenta? <a href="#" id="switchToLogin">Inicia sesión</a>'
        : '¿No tienes cuenta? <a href="#" id="switchToRegister">Regístrate</a>';
    authStatus.textContent = '';
    authForm.dataset.mode = isRegister ? 'register' : 'login';
}

// Cerrar modal
if (closeAuthModal) {
    closeAuthModal.onclick = () => { authModal.style.display = 'none'; };
}

// Cambiar entre login y registro
if (authModal) {
    authModal.addEventListener('click', function(e) {
        if (e.target.id === 'switchToRegister') {
            showAuthModal(true);
        } else if (e.target.id === 'switchToLogin') {
            showAuthModal(false);
        }
    });
}

// Enviar login/registro
if (authForm) {
    authForm.onsubmit = async function(e) {
        e.preventDefault();
        const username = authUsername.value.trim();
        const password = authPassword.value.trim();
        const mode = authForm.dataset.mode;
        authStatus.textContent = 'Procesando...';
        try {
            const url = mode === 'register' ? '/api/register' : '/api/token';
            const body = mode === 'register'
                ? { username, password }
                : { username, password };
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            const data = await response.json();
            if (data.access_token) {
                localStorage.setItem('jwt', data.access_token);
                updateAuthButtons();
                loadUserSummaries();
                authStatus.textContent = '¡Éxito!';
                setTimeout(() => { authModal.style.display = 'none'; }, 800);
            } else {
                authStatus.textContent = data.detail || 'Error de autenticación';
            }
        } catch (err) {
            authStatus.textContent = 'Error de red';
        }
    };
}

// Guardar resumen
if (saveSummaryBtn) {
    saveSummaryBtn.onclick = async function() {
        const jwt = localStorage.getItem('jwt');
        if (!jwt) {
            showAuthModal(false);
            return;
        }
        const summary = document.getElementById('summary').textContent;
        const keyPoints = Array.from(document.getElementById('keyPoints').querySelectorAll('li')).map(li => li.textContent).join('\n');
        const questions = Array.from(document.getElementById('questions').querySelectorAll('li')).map(li => li.textContent).join('\n');
        const title = prompt('Título para el resumen:', 'Resumen guardado');
        saveSummaryStatus.style.display = 'inline';
        saveSummaryStatus.textContent = 'Guardando...';
        try {
            const response = await fetch('/api/save-summary', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + jwt
                },
                body: JSON.stringify({ summary, key_points: keyPoints, questions, title })
            });
            const data = await response.json();
            if (data.success) {
                saveSummaryStatus.textContent = '✅ Resumen guardado';
                // Actualizar el listado de resúmenes
                loadUserSummaries();
            } else {
                saveSummaryStatus.textContent = '❌ ' + (data.error || 'No se pudo guardar');
            }
        } catch (err) {
            saveSummaryStatus.textContent = '❌ Error de red';
        }
        setTimeout(() => { saveSummaryStatus.style.display = 'none'; }, 3500);
    };
}

// Botones de registro e inicio de sesión
if (headerRegisterBtn) {
    headerRegisterBtn.onclick = () => showAuthModal(true);
}
if (headerLoginBtn) {
    headerLoginBtn.onclick = () => showAuthModal(false);
}
if (headerLogoutBtn) {
    headerLogoutBtn.onclick = () => {
        localStorage.removeItem('jwt');
        updateAuthButtons();
        loadUserSummaries();
    };
}
