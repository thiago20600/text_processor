// Elementos del DOM
const textForm = document.getElementById('textForm');
const textInput = document.getElementById('textInput');
const languageSelect = document.getElementById('languageSelect');
const charCount = document.getElementById('charCount');
const btnText = document.getElementById('btnText');
const spinner = document.getElementById('spinner');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');
const loadingSection = document.getElementById('loadingSection');
const formSection = document.querySelector('.form-section');

// Event Listeners
textForm.addEventListener('submit', handleFormSubmit);
textInput.addEventListener('input', updateCharCount);

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
    loadingSection.style.display = 'block';
    textForm.style.display = 'none';
    
    // Deshabilitar botón
    const submitBtn = textForm.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    spinner.style.display = 'inline-block';
    btnText.textContent = 'Procesando...';
    
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
        spinner.style.display = 'none';
        btnText.textContent = '🚀 Procesar texto';
    }
}

// Mostrar resultados
function displayResults(data) {
    hideAllSections();
    resultsSection.style.display = 'block';
    
    // Poblar resumen
    const summaryDiv = document.getElementById('summary');
    summaryDiv.textContent = data.summary || 'No se generó resumen';
    
    // Poblar puntos clave (puede ser array o string)
    const keyPointsDiv = document.getElementById('keyPoints');
    if (Array.isArray(data.key_points)) {
        keyPointsDiv.innerHTML = data.key_points.map(point => `<li>${point}</li>`).join('');
    } else {
        keyPointsDiv.textContent = data.key_points || 'No se generaron puntos clave';
    }
    
    // Poblar preguntas (puede ser array o string)
    const questionsDiv = document.getElementById('questions');
    if (Array.isArray(data.questions)) {
        questionsDiv.innerHTML = data.questions.map(q => `<li>${q}</li>`).join('');
    } else {
        questionsDiv.textContent = data.questions || 'No se generaron preguntas';
    }
    
    // Scroll a los resultados
    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

// Mostrar error
function showError(message) {
    hideAllSections();
    errorSection.style.display = 'block';
    
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.textContent = message;
    
    textForm.style.display = 'block';
    
    // Scroll al error
    setTimeout(() => {
        errorSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

// Ocultar todas las secciones de resultados
function hideAllSections() {
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
    loadingSection.style.display = 'none';
    formSection.style.display = 'block';
}

// Resetear formulario
function resetForm() {
    textInput.value = '';
    charCount.textContent = '0';
    textForm.style.display = 'block';
    hideAllSections();
    textInput.focus();
}

// Copiar al portapapeles
async function copyToClipboard(elementId) {
    try {
        const element = document.getElementById(elementId);
        const text = element.textContent;
        
        // Intentar usar la API moderna
        if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(text);
            showCopyFeedback(event.target);
        } else {
            // Fallback para navegadores antiguos
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            showCopyFeedback(event.target);
        }
    } catch (error) {
        console.error('Error al copiar:', error);
        alert('No se pudo copiar el texto');
    }
}

// Mostrar feedback de copia
function showCopyFeedback(btn) {
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
    textInput.focus();
});
