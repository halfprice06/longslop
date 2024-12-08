document.addEventListener("DOMContentLoaded", async () => {
    const styleSelect = document.getElementById('style');
    const form = document.getElementById('generateForm');
    const outputSection = document.getElementById('outputSection');
    const statusMessage = document.getElementById('statusMessage');
    const finalArticle = document.getElementById('finalArticle');
    const articleContent = document.getElementById('articleContent');
    const audioSection = document.getElementById('audioSection');
    const articleAudio = document.getElementById('articleAudio');

    // Auto-grow textarea functionality
    const topicTextarea = document.getElementById('topic');
    function autoGrow() {
        topicTextarea.style.height = 'auto';
        topicTextarea.style.height = (topicTextarea.scrollHeight) + 'px';
    }
    topicTextarea.addEventListener('input', autoGrow);
    // Initial call to set proper height
    autoGrow();

    // Waiting game elements
    const waitingGame = document.getElementById('waitingGame');
    const guessInput = document.getElementById('guessInput');
    const guessButton = document.getElementById('guessButton');
    const guessFeedback = document.getElementById('guessFeedback');
    let targetNumber = null;

    function startGuessingGame() {
        targetNumber = Math.floor(Math.random() * 100) + 1;
        guessFeedback.textContent = "Enter a guess above!";
    }

    guessButton.addEventListener('click', () => {
        const guess = parseInt(guessInput.value, 10);
        if (isNaN(guess)) {
            guessFeedback.textContent = "Please enter a valid number.";
            return;
        }

        if (guess < targetNumber) {
            guessFeedback.textContent = "Too low! Try again.";
        } else if (guess > targetNumber) {
            guessFeedback.textContent = "Too high! Try again.";
        } else {
            guessFeedback.textContent = "You got it! The number was " + targetNumber + ".";
            setTimeout(startGuessingGame, 2000);
        }
    });

    startGuessingGame(); // Start the guessing game immediately.

    // Modals
    const modalContents = {
        plan: document.getElementById('planContent'),
        outline: document.getElementById('outlineContent'),
        revised_plan: document.getElementById('revisedPlanContent'),
        revised_outline: document.getElementById('revisedOutlineContent')
    };

    document.querySelectorAll('.clickable[data-modal]').forEach(trigger => {
        trigger.addEventListener('click', () => {
            const modalId = trigger.getAttribute('data-modal');
            const modal = document.getElementById(modalId);
            if (modal) modal.style.display = 'block';
        });
    });

    document.querySelectorAll('.modal-close').forEach(closeBtn => {
        closeBtn.addEventListener('click', () => {
            closeBtn.closest('.modal').style.display = 'none';
        });
    });

    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            e.target.style.display = 'none';
        }
    });

    let sseSource = null;
    let cumulativeData = [];

    // Fetch styles
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
      const includeAudio = document.getElementById('includeAudio').value;

      if (!topic) {
        alert("Please enter a topic.");
        return;
      }

      startGeneration(topic, style, length, includeAudio);
    });

    function startGeneration(topic, style, length, includeAudio) {
      resetUI();
      statusMessage.textContent = "Contacting server...";

      const params = new URLSearchParams({
        topic: topic,
        style: style,
        length: length,
        provider: 'anthropic',
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
      document.querySelectorAll('.status-icon').forEach(icon => {
        icon.style.backgroundColor = '#000000';
      });

      statusMessage.textContent = "Waiting for generation...";
      cumulativeData = [];

      Object.values(modalContents).forEach(content => {
          if (content) {
              if (content.classList.contains('markdown-content')) {
                  content.innerHTML = '';
              } else {
                  content.textContent = '';
              }
          }
      });

      articleContent.innerHTML = "<p class='text-white'>Generating your story...</p>";
      articleAudio.src = "";
    }

    marked.setOptions({
        breaks: true,
        gfm: true
    });

    function renderContent(content, isMarkdown = false) {
        if (typeof content === 'string' && isMarkdown) {
            return marked.parse(content);
        }
        return JSON.stringify(content, null, 2);
    }

    function formatOutline(outline) {
        if (typeof outline === 'string') {
            try {
                outline = JSON.parse(outline);
            } catch (e) {
                return `<div class="outline-content">${outline}</div>`;
            }
        }

        let html = '<div class="outline-content">';
        if (Array.isArray(outline)) {
            html += '<ul class="outline-list">';
            outline.forEach(item => {
                if (typeof item === 'object') {
                    html += `<li class="outline-item">
                        <span class="outline-title">${item.title || item.heading || ''}</span>
                        ${item.content ? `<div class="outline-description">${item.content}</div>` : ''}
                        ${item.subheadings ? formatOutline(item.subheadings) : ''}
                    </li>`;
                } else {
                    html += `<li class="outline-item">${item}</li>`;
                }
            });
            html += '</ul>';
        } else if (typeof outline === 'object') {
            Object.entries(outline).forEach(([key, value]) => {
                html += `<div class="outline-section">
                    <h3 class="outline-section-title">${key}</h3>
                    ${Array.isArray(value) ? formatOutline(value) : `<div class="outline-content">${value}</div>`}
                </div>`;
            });
        }
        html += '</div>';
        return html;
    }

    function handleEvent(msg) {
      switch(msg.type) {
        case 'plan':
          updateStep('plan', true);
          statusMessage.textContent = "Plan received.";
          if (modalContents.plan) {
              modalContents.plan.innerHTML = renderContent(msg.content, true);
          }
          break;
        case 'outline':
          updateStep('outline', true);
          statusMessage.textContent = "Outline received.";
          if (modalContents.outline) {
              modalContents.outline.innerHTML = formatOutline(msg.content);
          }
          break;
        case 'revised_plan':
          updateStep('revised_plan', true);
          statusMessage.textContent = "Revised plan received.";
          if (modalContents.revised_plan) {
              modalContents.revised_plan.innerHTML = renderContent(msg.content, true);
          }
          break;
        case 'revised_outline':
          updateStep('revised_outline', true);
          statusMessage.textContent = "Revised outline received.";
          if (modalContents.revised_outline) {
              modalContents.revised_outline.innerHTML = formatOutline(msg.content);
          }
          break;
        case 'complete_content':
          updateStep('article', true);
          statusMessage.textContent = "Content generation complete.";

          if (msg.content.audio_path) {
            updateStep('audio', true);
            displayAudio(msg.content.audio_path);
          } else if (msg.content.audio_error) {
            updateStep('audio', false);
            statusMessage.textContent = "Error generating audio: " + msg.content.audio_error;
          }

          displayArticle(msg.content.article);
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
        icon.style.backgroundColor = success ? '#00ff00' : '#ff0000';
      }
    }

    function displayArticle(content) {
        try {
            if (typeof content === 'string') {
                const htmlContent = content
                    .split('\n\n')
                    .map(par => {
                        if (par.trim().startsWith('![')) {
                            return par;
                        }
                        return `<p>${par}</p>`;
                    })
                    .join('\n');

                const finalHtml = htmlContent.replace(
                    /!\[([^\]]*)\]\(([^)]+)\)/g,
                    '<img src="$2" alt="$1" class="w-full max-w-2xl mx-auto my-4 rounded-lg shadow-lg"/>'
                );

                articleContent.innerHTML = finalHtml;
                return;
            }

            const articleData = typeof content === 'string' ? JSON.parse(content) : content;

            const processScene = (scene) => {
                let html = '';
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

                if (scene.image_url) {
                    html += `<div class="scene-image">
                        <img src="${scene.image_url}" alt="Scene Illustration" class="w-full max-w-2xl mx-auto my-4 rounded-lg shadow-lg"/>
                    </div>`;
                }
                return html;
            };

            let htmlContent = '';

            if (articleData.content.intro_paragraphs) {
                articleData.content.intro_paragraphs.forEach(scene => {
                    htmlContent += processScene(scene);
                });

                articleData.content.main_headings.forEach(heading => {
                    htmlContent += `<h2 class="text-xl font-bold mt-8 mb-4">${heading.title}</h2>`;
                    heading.scenes.forEach(scene => {
                        htmlContent += processScene(scene);
                    });

                    if (heading.sub_headings) {
                        heading.sub_headings.forEach(subHeading => {
                            htmlContent += `<h3 class="text-lg font-semibold mt-6 mb-3">${subHeading.title}</h3>`;
                            subHeading.scenes.forEach(scene => {
                                htmlContent += processScene(scene);
                            });
                        });
                    }
                });

                if (articleData.content.conclusion_paragraphs) {
                    articleData.content.conclusion_paragraphs.forEach(scene => {
                        htmlContent += processScene(scene);
                    });
                }
            } else {
                articleData.content.scenes.forEach(scene => {
                    htmlContent += processScene(scene);
                });
            }

            articleContent.innerHTML = htmlContent;
        } catch (error) {
            console.error('Error processing article content:', error);
            const escapedContent = (content + '')
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
      const fullPath = audioPath.startsWith('output/') ? `/frontend/${audioPath}` : audioPath;
      articleAudio.src = fullPath;
    }

    const tabs = document.querySelectorAll('.game-tab');
    const snakeContainer = document.getElementById('snakeGameContainer');
    const glitchoutContainer = document.getElementById('glitchoutGameContainer');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            const game = tab.getAttribute('data-game');
            if (game === 'snake') {
                snakeContainer.classList.add('active');
                glitchoutContainer.classList.remove('active');
            } else {
                glitchoutContainer.classList.add('active');
                snakeContainer.classList.remove('active');
            }
        });
    });
});
