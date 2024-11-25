// Initialize markdown-it at the start
const md = window.markdownit();

// Style Loading Functions
async function loadStyles() {
    try {
        const response = await fetch('/api/v1/styles');
        const styles = await response.json();
        
        const styleSelect = document.getElementById('style-select');
        const styleInfo = document.querySelector('.style-info');
        
        // Update style info when selection changes
        styleSelect.addEventListener('change', () => {
            const selectedStyle = styles[styleSelect.value];
            if (selectedStyle) {
                styleInfo.innerHTML = `
                    <h3>${selectedStyle.name}</h3>
                    <p>${selectedStyle.description}</p>
                    <div class="example"><em>Example:</em> ${selectedStyle.example}</div>
                `;
            }
        });
        
        // Trigger initial style info display for the default selection
        const defaultStyle = styles[styleSelect.value];
        if (defaultStyle) {
            styleInfo.innerHTML = `
                <h3>${defaultStyle.name}</h3>
                <p>${defaultStyle.description}</p>
                <div class="example"><em>Example:</em> ${defaultStyle.example}</div>
            `;
        }
    } catch (error) {
        console.error('Failed to load styles:', error);
    }
}

async function showStyleInfo(event) {
    event.preventDefault();
    const overlay = document.querySelector('.style-modal-overlay');
    const styleSelect = document.getElementById('style-select');
    
    try {
        // Fetch styles if not already loaded
        if (!window.styles) {
            const response = await fetch('/api/v1/styles');
            window.styles = await response.json();
        }
        
        const selectedStyle = window.styles[styleSelect.value];
        if (selectedStyle) {
            const styleInfo = document.querySelector('.style-modal .style-info');
            styleInfo.innerHTML = `
                <h3>${selectedStyle.name}</h3>
                <p>${selectedStyle.description}</p>
                <div class="example"><em>Example:</em> ${selectedStyle.example}</div>
            `;
        }
        
        overlay.classList.add('active');
        
        // Add escape key listener
        const escapeHandler = (e) => {
            if (e.key === 'Escape') {
                hideStyleInfo();
                document.removeEventListener('keydown', escapeHandler);
            }
        };
        document.addEventListener('keydown', escapeHandler);
        
    } catch (error) {
        console.error('Failed to load style info:', error);
    }
}

function hideStyleInfo() {
    const overlay = document.querySelector('.style-modal-overlay');
    overlay.classList.remove('active');
}

function updateUIForLength() {
    const lengthSelect = document.getElementById('length-select');
    const styleSelect = document.getElementById('style-select');
    
    // Remove the length-based restrictions
    Array.from(styleSelect.options).forEach(option => {
        option.disabled = false;
    });
}

// Utility Functions
function hideInputContainer() {
    const inputContainer = document.querySelector('.input-container');
    inputContainer.style.opacity = '0';
    setTimeout(() => {
        inputContainer.style.display = 'none';
    }, 200); // Match transition duration
}

function showTryAgainButton() {
    const tryAgainButton = document.createElement('button');
    tryAgainButton.className = 'try-again-button';
    tryAgainButton.textContent = 'Try Again';
    tryAgainButton.onclick = () => window.location.reload();
    
    // Insert after the written article
    const writtenArticle = document.querySelector('.written-article');
    writtenArticle.insertAdjacentElement('afterend', tryAgainButton);
    
    // Trigger animation
    setTimeout(() => {
        tryAgainButton.classList.add('visible');
    }, 100);
}

function autoResizeTextarea() {
    const textarea = document.getElementById('topic');
    textarea.style.height = 'auto';
    const newHeight = Math.min(textarea.scrollHeight, 150);
    textarea.style.height = newHeight + 'px';
}

// Output Update Functions
function updateArticleOutput(content) {
    const articleOutput = document.getElementById('article-output');
    const includeHeaders = document.getElementById('includeHeaders').checked;
    
    let processedContent = content
        .replace(/<\/?[^>]+(>|$)/g, '')
        .replace(/\n{2,}/g, '\n\n')
        .split('\n\n')
        .filter(para => para.trim())
        .map(para => para.trim())
        .join('\n\n');

    processedContent = processedContent.replace(/§CAPS§(.*?)(\n|$)/g, (match, p1) => {
        return p1;
    });

    // Skip markdown rendering for headers if they're disabled
    let htmlContent;
    if (!includeHeaders) {
        // Remove any markdown headers (#, ##, ###, etc.)
        processedContent = processedContent.replace(/^#+\s+.*$/gm, '');
        // Remove empty lines that might be left after removing headers
        processedContent = processedContent.replace(/\n{3,}/g, '\n\n');
    }
    
    htmlContent = md.render(processedContent);
    articleOutput.innerHTML = htmlContent;

    articleOutput.querySelectorAll('p').forEach((p, index) => {
        p.style.textAlign = 'justify';
        p.style.textJustify = 'inter-word';
        
        const prevElement = p.previousElementSibling;
        if (index === 0 || (prevElement && prevElement.tagName.match(/^H[1-6]$/))) {
            p.dataset.caps = 'true';
            const text = p.textContent;
            // Take first 3-4 words for small caps
            const words = text.split(' ');
            const capsWords = words.slice(0, 4).join(' ');
            const restOfText = words.slice(4).join(' ');
            
            // Create the modified content with only first few words in small caps
            p.innerHTML = `<span class="small-caps">${capsWords}</span> ${restOfText}`;
        }
    });
}

function updateNarrativeOutput(content) {
    const narrativeOutput = document.getElementById('narrative-output');
    let processedContent = content
        .replace(/<\/?p>/g, '')
        .replace(/([^\n])\n([^\n])/g, '$1 $2')
        .replace(/\n\n+/g, '\n\n')
        .split('\n\n')
        .filter(para => para.trim())
        .map(para => para.trim())
        .join('\n\n');

    const htmlContent = md.render(processedContent);
    narrativeOutput.innerHTML = htmlContent;
}

function updateStructuredOutput(content) {
    const structuredOutput = document.getElementById('structured-output');
    
    if (typeof content === 'object') {
        const formattedJson = JSON.stringify(content, null, 2)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/(".*?")/g, '<span class="json-string">$1</span>')
            .replace(/\b(true|false|null)\b/g, '<span class="json-keyword">$1</span>');
        structuredOutput.innerHTML = `<pre>${formattedJson}</pre>`;
    } else {
        const htmlContent = md.render(content);
        structuredOutput.innerHTML = htmlContent;
    }
}

// Main Article Generation Function
function writeArticle() {
    const topic = document.getElementById('topic').value;
    const style = document.getElementById('style-select').value;
    const length = document.getElementById('length-select').value;
    const provider = document.getElementById('provider').value;
    const includeHeaders = document.getElementById('includeHeaders').checked;
    
    if (!topic) {
        alert('Please enter a topic');
        return;
    }

    hideInputContainer();

    // Clear previous outputs
    document.getElementById('narrative-output').innerHTML = '';
    document.getElementById('structured-output').innerHTML = '';
    document.getElementById('article-output').innerHTML = '';

    // Update the loading state selectors
    document.querySelector('.narrative-plan').classList.add('loading');
    document.querySelector('.structured-plan').classList.add('loading');
    document.querySelector('.written-article').classList.add('loading');

    const eventSource = new EventSource('/api/v1/write-article-stream?' + new URLSearchParams({
        topic: topic,
        style: style,
        length: length,
        provider: provider,
        includeHeaders: includeHeaders
    }));

    eventSource.onmessage = function(event) {
        console.log('Received event data:', event.data);
        const data = JSON.parse(event.data);

        if (data.type === 'plan') {
            updateNarrativeOutput(data.content);
            document.querySelector('.narrative-plan').classList.remove('loading');
        } else if (data.type === 'outline') {
            updateStructuredOutput(data.content);
            document.querySelector('.structured-plan').classList.remove('loading');
        } else if (data.type === 'article') {
            updateArticleOutput(data.content);
            document.querySelector('.written-article').classList.remove('loading');
            showTryAgainButton();
        } else if (data.type === 'error') {
            console.error('Error:', data.content);
            eventSource.close();
            alert('An error occurred while generating the article.');
            document.querySelectorAll('.panel').forEach(panel => {
                panel.classList.remove('loading');
            });
        }
    };

    eventSource.addEventListener('end', function(event) {
        eventSource.close();
        console.log('Article generation completed.');
        document.querySelectorAll('.panel').forEach(panel => {
            panel.classList.remove('loading');
        });
    });

    eventSource.onerror = function(event) {
        console.error('Error event:', event);
        eventSource.close();
        alert('An error occurred while generating the article.');
        document.querySelectorAll('.panel').forEach(panel => {
            panel.classList.remove('loading');
        });
    };
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    loadStyles();
    
    const textarea = document.getElementById('topic');
    textarea.addEventListener('input', autoResizeTextarea);
    
    const articleOutput = document.getElementById('article-output');
    if (articleOutput && articleOutput.textContent.trim()) {
        updateArticleOutput(articleOutput.textContent);
    }

    const narrativeOutput = document.getElementById('narrative-output');
    if (narrativeOutput && narrativeOutput.textContent.trim()) {
        updateNarrativeOutput(narrativeOutput.textContent);
    }

    document.querySelector('.style-modal-close').addEventListener('click', (e) => {
        e.preventDefault();
        hideStyleInfo();
    });
    
    document.querySelector('.style-modal-overlay').addEventListener('click', (e) => {
        if (e.target === e.currentTarget) {
            hideStyleInfo();
        }
    });

    // Initialize length-based UI updates
    updateUIForLength();
    document.getElementById('length-select').addEventListener('change', updateUIForLength);
});