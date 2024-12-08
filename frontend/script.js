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
    const includeAudioParam = document.getElementById('includeAudio').value; 
    const generateFormSection = document.querySelector('.pixel-border.terminal-panel.mb-8');
    const progressSection = document.querySelector('#outputSection > .pixel-border.terminal-panel.mb-8');
    const mainContainer = document.querySelector('main .max-w-3xl');
    
    if (includeAudioParam === "false") {
        audioSection.classList.add('hidden');
    }
    
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

      const includeAudio = document.getElementById('includeAudio').value; 

      const params = new URLSearchParams({
        topic: topic,
        style: style,
        length: length,
        provider: 'openai',
        includeHeaders: includeHeaders,
        includeAudio: includeAudio
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
        case 'complete_content':
          updateStep('article', true);
          statusMessage.textContent = "Content generation complete.";
          
          // Handle audio if present
          if (msg.content.audio_path) {
            updateStep('audio', true);
            displayAudio(msg.content.audio_path);
          } else if (msg.content.audio_error) {
            updateStep('audio', false);
            statusMessage.textContent = "Error generating audio: " + msg.content.audio_error;
          }

          // Display the article
          displayArticle(msg.content.article);
          
          // Reorder sections
          mainContainer.innerHTML = ''; // Clear the container
          
          // Add sections in the desired order
          if (audioSection && !audioSection.classList.contains('hidden')) {
            mainContainer.appendChild(audioSection);
          }
          mainContainer.appendChild(finalArticle);
          mainContainer.appendChild(generateFormSection);
          mainContainer.appendChild(progressSection);
          
          break;
        case 'error':
          statusMessage.textContent = "An error occurred: " + msg.content;
          console.error("Error from server:", msg.content);
          break;
        default:
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
        
        try {
            // If content is a string and contains markdown-style images or paragraphs
            if (typeof content === 'string') {
                // Split content into paragraphs and wrap each in <p> tags
                const htmlContent = content
                    .split('\n\n')
                    .map(par => {
                        // If it's an image markdown, keep it as is
                        if (par.trim().startsWith('![')) {
                            return par;
                        }
                        // Otherwise wrap in <p> tags
                        return `<p>${par}</p>`;
                    })
                    .join('\n');
                
                // Convert markdown image syntax to HTML img tags
                const finalHtml = htmlContent.replace(
                    /!\[([^\]]*)\]\(([^)]+)\)/g, 
                    '<img src="$2" alt="$1" class="w-full max-w-2xl mx-auto my-4 rounded-lg shadow-lg"/>'
                );
                
                articleContent.innerHTML = finalHtml;
                return;
            }

            // If we get here, try to handle as JSON
            const articleData = typeof content === 'string' ? JSON.parse(content) : content;
            
            // Function to process scene content
            const processScene = (scene) => {
                let html = '';
                
                // Add the scene description/text
                if (scene.text) {
                    const sceneText = JSON.parse(scene.text);
                    html += `<div class="scene">`;
                    sceneText.paragraphs.forEach(paragraph => {
                        paragraph.lines.forEach(line => {
                            html += `<p>${line.text}</p>`;
                        });
                    });
                    html += `</div>`;
                }
                
                // Add the scene image if present
                if (scene.image_url) {
                    html += `<div class="scene-image">
                        <img src="${scene.image_url}" alt="Scene Illustration" class="w-full max-w-2xl mx-auto my-4 rounded-lg shadow-lg"/>
                    </div>`;
                }
                
                return html;
            };

            let htmlContent = '';

            // Process content based on article length type
            if (articleData.content.intro_paragraphs) {
                // Medium or Long article
                // Process intro paragraphs
                articleData.content.intro_paragraphs.forEach(scene => {
                    htmlContent += processScene(scene);
                });

                // Process main headings
                articleData.content.main_headings.forEach(heading => {
                    htmlContent += `<h2 class="text-xl font-bold mt-8 mb-4">${heading.title}</h2>`;
                    heading.scenes.forEach(scene => {
                        htmlContent += processScene(scene);
                    });

                    // Process sub-headings if they exist
                    if (heading.sub_headings) {
                        heading.sub_headings.forEach(subHeading => {
                            htmlContent += `<h3 class="text-lg font-semibold mt-6 mb-3">${subHeading.title}</h3>`;
                            subHeading.scenes.forEach(scene => {
                                htmlContent += processScene(scene);
                            });
                        });
                    }
                });

                // Process conclusion paragraphs
                if (articleData.content.conclusion_paragraphs) {
                    articleData.content.conclusion_paragraphs.forEach(scene => {
                        htmlContent += processScene(scene);
                    });
                }
            } else {
                // Short article
                articleData.content.scenes.forEach(scene => {
                    htmlContent += processScene(scene);
                });
            }

            articleContent.innerHTML = htmlContent;
        } catch (error) {
            console.error('Error processing article content:', error);
            // If all else fails, display as plain text
            const escapedContent = content
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;");
            const simpleHtmlContent = escapedContent
                .split(/\n\n+/)
                .map(par => `<p>${par.replace(/\n/g, ' ')}</p>`)
                .join("");
            articleContent.innerHTML = simpleHtmlContent;
        }
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
  