document.addEventListener("DOMContentLoaded", async () => {
    const styleSelect = document.getElementById('style');
    const form = document.getElementById('generateForm');
    const outputSection = document.getElementById('outputSection');
    const statusMessage = document.getElementById('statusMessage');
    const rawData = document.getElementById('rawData');
    const rawDataToggle = document.getElementById('rawDataToggle');
    const finalArticle = document.getElementById('finalArticle');
    const articleContent = document.getElementById('articleContent');
    const audioSection = document.getElementById('audioSection');
    const articleAudio = document.getElementById('articleAudio');
  
    let sseSource = null;
    let rawDataVisible = false;
    let cumulativeData = [];
  
    // Fetch styles from backend and populate styles dropdown
    async function fetchStyles() {
      try {
        const res = await fetch('/api/v1/styles');
        if (!res.ok) throw new Error('Failed to fetch styles');
        const styles = await res.json();
        Object.keys(styles).forEach(key => {
          const opt = document.createElement('option');
          opt.value = key;
          opt.innerText = styles[key].name;
          styleSelect.appendChild(opt);
        });
      } catch (e) {
        console.error(e);
        alert("Error fetching styles. Check console for details.");
      }
    }
  
    await fetchStyles();
  
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const topic = document.getElementById('topic').value.trim();
      const style = document.getElementById('style').value;
      const length = document.getElementById('length').value;
      const includeHeaders = document.getElementById('includeHeaders').value === "true";
  
      if (!topic) {
        alert("Please enter a topic.");
        return;
      }
  
      startGeneration(topic, style, length, includeHeaders);
    });
  
    function startGeneration(topic, style, length, includeHeaders) {
      resetUI();
      outputSection.classList.remove('hidden');
  
      const params = new URLSearchParams({
        topic: topic,
        style: style,
        length: length,
        provider: 'openai',
        includeHeaders: includeHeaders
      });
  
      sseSource = new EventSource(`/api/v1/write-article-stream?${params.toString()}`);
  
      sseSource.onmessage = (event) => {
        if (event.data === "" && event.lastEventId === "end") {
          sseSource.close();
          statusMessage.textContent = "Generation complete.";
          return;
        }
  
        try {
          const msg = JSON.parse(event.data);
          cumulativeData.push(msg);
          rawDataToggle.classList.remove('hidden');
  
          // Update raw data display
          rawData.textContent = JSON.stringify(cumulativeData, null, 2);
  
          // Handle different event types
          handleEvent(msg);
        } catch (err) {
          console.error("Error parsing SSE message:", err);
        }
      };
  
      sseSource.onerror = (error) => {
        console.error("SSE error:", error);
        statusMessage.textContent = "Error occurred. Check console.";
        if (sseSource) {
          sseSource.close();
        }
      };
    }
  
    function resetUI() {
      // Reset progress steps
      document.querySelectorAll('.status-icon').forEach(icon => {
        icon.classList.remove('bg-green-500', 'bg-red-500', 'bg-indigo-500');
        icon.classList.add('bg-gray-300');
      });
      statusMessage.textContent = "Waiting for server response...";
      rawData.textContent = "";
      rawData.classList.add('hidden');
      rawDataVisible = false;
      rawDataToggle.classList.add('hidden');
      articleContent.innerHTML = "";
      finalArticle.classList.add('hidden');
      audioSection.classList.add('hidden');
      articleAudio.src = "";
      cumulativeData = [];
    }
  
    function handleEvent(msg) {
      switch(msg.type) {
        case 'plan':
          updateStep('plan', true);
          statusMessage.textContent = "Plan received.";
          break;
        case 'outline':
          updateStep('outline', true);
          statusMessage.textContent = "Outline received.";
          break;
        case 'revised_plan':
          updateStep('revised_plan', true);
          statusMessage.textContent = "Revised plan received.";
          break;
        case 'revised_outline':
          updateStep('revised_outline', true);
          statusMessage.textContent = "Revised outline received.";
          break;
        case 'article':
          updateStep('article', true);
          statusMessage.textContent = "Final article received.";
          displayArticle(msg.content);
          break;
        case 'audio':
          updateStep('audio', true);
          statusMessage.textContent = "Audio file received.";
          displayAudio(msg.content);
          break;
        case 'audio_error':
          updateStep('audio', false);
          statusMessage.textContent = "Error generating audio.";
          break;
        case 'error':
          statusMessage.textContent = "An error occurred: " + msg.content;
          console.error("Error from server:", msg.content);
          break;
        default:
          // Other events
          console.log("Unknown event type:", msg);
      }
    }
  
    function updateStep(step, success) {
      const icon = document.querySelector(`.status-icon[data-step="${step}"]`);
      if (icon) {
        icon.classList.remove('bg-gray-300');
        icon.classList.add(success ? 'bg-green-500' : 'bg-red-500');
      }
    }
  
    function displayArticle(content) {
      finalArticle.classList.remove('hidden');
      // Content is pre-formatted markdown, we can just insert as HTML
      const escapedContent = content
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
      // Convert newlines to paragraphs or just trust the formatting
      // We'll trust formatting and add <p> tags where double newlines appear:
      const htmlContent = escapedContent
        .split(/\n\n+/)
        .map(par => `<p>${par.replace(/\n/g, ' ')}</p>`)
        .join("");
      articleContent.innerHTML = htmlContent;
    }
  
    function displayAudio(audioPath) {
      audioSection.classList.remove('hidden');
      // audioPath is relative to frontend/output, so prepend /frontend/ if needed
      const fullPath = audioPath.startsWith('output/') ? `/frontend/${audioPath}` : audioPath;
      articleAudio.src = fullPath;
    }
  
    window.toggleRawData = function() {
      rawDataVisible = !rawDataVisible;
      if (rawDataVisible) {
        rawData.classList.remove('hidden');
      } else {
        rawData.classList.add('hidden');
      }
    }
  });
  