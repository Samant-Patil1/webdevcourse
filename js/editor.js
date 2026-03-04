/** ========================================
 * LIVE CODE EDITOR
 * Interactive HTML/CSS/JS editor with preview
 * ===================================== */

(function() {
  'use strict';

  /**
   * CodeEditor Class
   */
  class CodeEditor {
    constructor(container, options = {}) {
      this.container = typeof container === 'string' 
        ? document.querySelector(container) 
        : container;
      
      if (!this.container) {
        console.error('CodeEditor: Container not found');
        return;
      }

      this.options = {
        mode: options.mode || 'html', // html, css, js, or combined
        initialCode: options.initialCode || '',
        height: options.height || '300px',
        showPreview: options.showPreview !== false,
        showConsole: options.showConsole || false,
        readonly: options.readonly || false,
        ...options
      };

      this.originalCode = this.options.initialCode;
      this.init();
    }

    init() {
      this.createStructure();
      this.attachEvents();
      this.updatePreview();
    }

    createStructure() {
      // Create editor HTML structure
      this.container.innerHTML = `
        <div class="code-editor-container">
          <div class="editor-header">
            <div class="editor-tabs">
              <button class="editor-tab active" data-tab="code">Code</button>
              ${this.options.showPreview ? '<button class="editor-tab" data-tab="preview">Preview</button>' : ''}
              ${this.options.showConsole ? '<button class="editor-tab" data-tab="console">Console</button>' : ''}
            </div>
            <div class="editor-actions">
              <button class="editor-btn copy-btn" title="Copy code">📋</button>
              <button class="editor-btn reset-btn" title="Reset code">↺</button>
              <button class="run-btn">Run Code</button>
            </div>
          </div>
          <div class="editor-body">
            <div class="tab-content code-tab active">
              <textarea class="code-input" spellcheck="false" ${this.options.readonly ? 'readonly' : ''}>${this.escapeHtml(this.options.initialCode)}</textarea>
            </div>
            ${this.options.showPreview ? `
            <div class="tab-content preview-tab">
              <iframe class="preview-frame" sandbox="allow-scripts allow-same-origin"></iframe>
            </div>
            ` : ''}
            ${this.options.showConsole ? `
            <div class="tab-content console-tab">
              <div class="console-output"></div>
            </div>
            ` : ''}
          </div>
          <div class="editor-footer">
            <span class="editor-status">Ready</span>
            <span class="editor-info">${this.options.mode.toUpperCase()}</span>
          </div>
        </div>
      `;

      // Cache elements
      this.codeInput = this.container.querySelector('.code-input');
      this.previewFrame = this.container.querySelector('.preview-frame');
      this.consoleOutput = this.container.querySelector('.console-output');
      this.statusEl = this.container.querySelector('.editor-status');
      this.copyBtn = this.container.querySelector('.copy-btn');
      this.resetBtn = this.container.querySelector('.reset-btn');
      this.runBtn = this.container.querySelector('.run-btn');
      this.tabs = this.container.querySelectorAll('.editor-tab');
      this.tabContents = this.container.querySelectorAll('.tab-content');

      // Set height
      if (this.codeInput) {
        this.codeInput.style.minHeight = this.options.height;
      }
    }

    attachEvents() {
      // Tab switching
      this.tabs.forEach(tab => {
        tab.addEventListener('click', () => this.switchTab(tab.dataset.tab));
      });

      // Run code
      if (this.runBtn) {
        this.runBtn.addEventListener('click', () => this.runCode());
      }

      // Copy code
      if (this.copyBtn) {
        this.copyBtn.addEventListener('click', () => this.copyCode());
      }

      // Reset code
      if (this.resetBtn) {
        this.resetBtn.addEventListener('click', () => this.resetCode());
      }

      // Auto-run on input (with debounce)
      if (this.codeInput && !this.options.readonly) {
        let timeout;
        this.codeInput.addEventListener('input', () => {
          clearTimeout(timeout);
          timeout = setTimeout(() => this.updatePreview(), 1000);
        });

        // Tab key support
        this.codeInput.addEventListener('keydown', (e) => {
          if (e.key === 'Tab') {
            e.preventDefault();
            const start = this.codeInput.selectionStart;
            const end = this.codeInput.selectionEnd;
            this.codeInput.value = this.codeInput.value.substring(0, start) + '  ' + this.codeInput.value.substring(end);
            this.codeInput.selectionStart = this.codeInput.selectionEnd = start + 2;
          }
        });
      }
    }

    switchTab(tabName) {
      // Update tab buttons
      this.tabs.forEach(tab => {
        tab.classList.toggle('active', tab.dataset.tab === tabName);
      });

      // Update content
      this.tabContents.forEach(content => {
        content.classList.remove('active');
      });
      
      const targetContent = this.container.querySelector(`.${tabName}-tab`);
      if (targetContent) {
        targetContent.classList.add('active');
      }

      // If switching to preview, update it
      if (tabName === 'preview') {
        this.updatePreview();
      }
    }

    getCode() {
      return this.codeInput ? this.codeInput.value : '';
    }

    setCode(code) {
      if (this.codeInput) {
        this.codeInput.value = code;
        this.updatePreview();
      }
    }

    updatePreview() {
      if (!this.previewFrame) return;

      const code = this.getCode();
      const doc = this.previewFrame.contentDocument || this.previewFrame.contentWindow.document;

      let html = code;
      
      // Wrap different modes appropriately
      if (this.options.mode === 'css') {
        html = `
          <!DOCTYPE html>
          <html>
          <head>
            <style>${code}</style>
          </head>
          <body>
            <div class="preview-content">
              <h1>CSS Preview</h1>
              <p>This is a paragraph to preview your CSS styles.</p>
              <button>Button Example</button>
              <div class="box">Box Element</div>
            </div>
          </body>
          </html>
        `;
      } else if (this.options.mode === 'js') {
        html = `
          <!DOCTYPE html>
          <html>
          <head>
            <style>
              body { 
                font-family: sans-serif; 
                padding: 20px;
                background: #0d1117;
                color: #c9d1d9;
              }
              .output { 
                background: #161b22; 
                padding: 15px; 
                border-radius: 6px;
                border: 1px solid #30363d;
                margin-top: 10px;
              }
              .log { color: #58a6ff; }
              .error { color: #f85149; }
            </style>
          </head>
          <body>
            <div id="output"></div>
            <script>
              const output = document.getElementById('output');
              const originalLog = console.log;
              const originalError = console.error;
              
              console.log = function(...args) {
                const div = document.createElement('div');
                div.className = 'log';
                div.textContent = args.join(' ');
                output.appendChild(div);
                originalLog.apply(console, args);
              };
              
              console.error = function(...args) {
                const div = document.createElement('div');
                div.className = 'error';
                div.textContent = args.join(' ');
                output.appendChild(div);
                originalError.apply(console, args);
              };
              
              try {
                ${code}
              } catch(e) {
                console.error('Error: ' + e.message);
              }
            </script>
          </body>
          </html>
        `;
      }

      doc.open();
      doc.write(html);
      doc.close();

      this.updateStatus('Updated');
    }

    runCode() {
      this.updatePreview();
      this.switchTab('preview');
      this.updateStatus('Running...');
      
      setTimeout(() => {
        this.updateStatus('Ready');
      }, 500);
    }

    async copyCode() {
      try {
        await navigator.clipboard.writeText(this.getCode());
        this.copyBtn.textContent = '✓';
        this.copyBtn.classList.add('copied');
        this.updateStatus('Copied!');
        
        setTimeout(() => {
          this.copyBtn.textContent = '📋';
          this.copyBtn.classList.remove('copied');
          this.updateStatus('Ready');
        }, 2000);
      } catch (err) {
        this.updateStatus('Copy failed');
      }
    }

    resetCode() {
      this.setCode(this.originalCode);
      this.updateStatus('Reset');
    }

    updateStatus(message) {
      if (this.statusEl) {
        this.statusEl.textContent = message;
      }
    }

    escapeHtml(text) {
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
    }
  }

  /**
   * CombinedEditor - For HTML/CSS/JS in one
   */
  class CombinedEditor extends CodeEditor {
    constructor(container, options = {}) {
      super(container, {
        mode: 'combined',
        showPreview: true,
        ...options
      });
    }

    createStructure() {
      this.container.innerHTML = `
        <div class="code-editor-container combined">
          <div class="editor-header">
            <div class="editor-tabs">
              <button class="editor-tab active" data-tab="html">HTML</button>
              <button class="editor-tab" data-tab="css">CSS</button>
              <button class="editor-tab" data-tab="js">JS</button>
              <button class="editor-tab" data-tab="preview">Preview</button>
            </div>
            <div class="editor-actions">
              <button class="editor-btn reset-btn" title="Reset all">↺</button>
              <button class="run-btn">Run</button>
            </div>
          </div>
          <div class="editor-body combined-body">
            <div class="tab-content html-tab active">
              <textarea class="code-input html-input" spellcheck="false" placeholder="<!-- HTML code here -->">${this.options.initialHTML || ''}</textarea>
            </div>
            <div class="tab-content css-tab">
              <textarea class="code-input css-input" spellcheck="false" placeholder="/* CSS code here */">${this.options.initialCSS || ''}</textarea>
            </div>
            <div class="tab-content js-tab">
              <textarea class="code-input js-input" spellcheck="false" placeholder="// JavaScript code here">${this.options.initialJS || ''}</textarea>
            </div>
            <div class="tab-content preview-tab">
              <iframe class="preview-frame" sandbox="allow-scripts allow-same-origin"></iframe>
            </div>
          </div>
        </div>
      `;

      this.htmlInput = this.container.querySelector('.html-input');
      this.cssInput = this.container.querySelector('.css-input');
      this.jsInput = this.container.querySelector('.js-input');
      this.previewFrame = this.container.querySelector('.preview-frame');
      this.tabs = this.container.querySelectorAll('.editor-tab');
      this.tabContents = this.container.querySelectorAll('.tab-content');
      this.runBtn = this.container.querySelector('.run-btn');
      this.resetBtn = this.container.querySelector('.reset-btn');
    }

    getCode() {
      return {
        html: this.htmlInput ? this.htmlInput.value : '',
        css: this.cssInput ? this.cssInput.value : '',
        js: this.jsInput ? this.jsInput.value : ''
      };
    }

    updatePreview() {
      if (!this.previewFrame) return;

      const { html, css, js } = this.getCode();
      const doc = this.previewFrame.contentDocument || this.previewFrame.contentWindow.document;

      const fullHTML = `
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <style>${css}</style>
        </head>
        <body>
          ${html}
          <script>
            try {
              ${js}
            } catch(e) {
              console.error('Error: ' + e.message);
            }
          </script>
        </body>
        </html>
      `;

      doc.open();
      doc.write(fullHTML);
      doc.close();
    }
  }

  // Expose to global scope
  window.CodeEditor = CodeEditor;
  window.CombinedEditor = CombinedEditor;

  // Auto-initialize editors with data attributes
  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-editor]').forEach(el => {
      const mode = el.dataset.editor;
      const codeEl = el.querySelector('code');
      const textareaEl = el.querySelector('textarea');
      const initialCode = codeEl?.textContent || textareaEl?.value || '';
      const options = {
        mode: mode,
        initialCode: initialCode,
        ...el.dataset
      };
      
      if (mode === 'combined') {
        new CombinedEditor(el, options);
      } else {
        new CodeEditor(el, options);
      }
    });
  });
})();
