const form = document.querySelector('#upload-form');
const fileInput = document.querySelector('#file-input');
const dropZone = document.querySelector('#drop-zone');
const selectedFile = document.querySelector('#selected-file');
const fileName = document.querySelector('#file-name');
const fileSize = document.querySelector('#file-size');
const removeFile = document.querySelector('#remove-file');
const processButton = document.querySelector('#process-button');
const progressCard = document.querySelector('#progress-card');
const progressTitle = document.querySelector('#progress-title');
const progressMessage = document.querySelector('#progress-message');
const progressPercent = document.querySelector('#progress-percent');
const progressFill = document.querySelector('#progress-fill');
const elapsedTime = document.querySelector('#elapsed-time');
const successCard = document.querySelector('#success-card');
const successMessage = document.querySelector('#success-message');
const downloadButton = document.querySelector('#download-button');
const errorMessage = document.querySelector('#error-message');

let selectedWorkbook = null;
let downloadBlob = null;
let downloadName = 'updated_workbook.xlsx';
let timerId = null;
let startedAt = 0;

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function showError(message) {
  errorMessage.textContent = message;
  errorMessage.hidden = false;
}

function resetView() {
  selectedWorkbook = null;
  downloadBlob = null;
  fileInput.value = '';
  selectedFile.hidden = true;
  dropZone.hidden = false;
  processButton.disabled = true;
  progressCard.hidden = true;
  successCard.hidden = true;
  errorMessage.hidden = true;
  window.clearInterval(timerId);
}

function selectFile(file) {
  if (!file) return;
  const validExtension = /\.(xlsx|xls|csv)$/i.test(file.name);
  if (!validExtension) {
    showError('Please choose an XLSX, XLS, or CSV file.');
    return;
  }
  selectedWorkbook = file;
  fileName.textContent = file.name;
  fileSize.textContent = formatBytes(file.size);
  selectedFile.hidden = false;
  dropZone.hidden = true;
  processButton.disabled = false;
  errorMessage.hidden = true;
}

function updateElapsedTime() {
  const elapsed = Math.floor((Date.now() - startedAt) / 1000);
  elapsedTime.textContent = `${String(Math.floor(elapsed / 60)).padStart(2, '0')}:${String(elapsed % 60).padStart(2, '0')}`;
}

function getDownloadName(contentDisposition) {
  const match = contentDisposition && contentDisposition.match(/filename="?([^";]+)"?/i);
  return match ? match[1] : `updated_${selectedWorkbook.name.replace(/\.(xlsx|xls|csv)$/i, '')}.xlsx`;
}

fileInput.addEventListener('change', () => selectFile(fileInput.files[0]));
removeFile.addEventListener('click', resetView);
dropZone.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault();
    fileInput.click();
  }
});
['dragenter', 'dragover'].forEach((eventName) => dropZone.addEventListener(eventName, (event) => {
  event.preventDefault();
  dropZone.classList.add('dragover');
}));
['dragleave', 'drop'].forEach((eventName) => dropZone.addEventListener(eventName, (event) => {
  event.preventDefault();
  dropZone.classList.remove('dragover');
}));
dropZone.addEventListener('drop', (event) => selectFile(event.dataTransfer.files[0]));

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (!selectedWorkbook) return;

  const payload = new FormData();
  payload.append('file', selectedWorkbook);
  progressCard.hidden = false;
  successCard.hidden = true;
  errorMessage.hidden = true;
  processButton.disabled = true;
  progressTitle.textContent = 'Enrichment in progress';
  progressMessage.textContent = 'Reading your workbook and looking for missing details.';
  progressPercent.textContent = 'Working...';
  progressFill.style.width = '35%';
  startedAt = Date.now();
  timerId = window.setInterval(updateElapsedTime, 1000);
  updateElapsedTime();

  try {
    const response = await fetch('/process-excel/', { method: 'POST', body: payload });
    if (!response.ok) throw new Error(`The server returned ${response.status}.`);
    const contentType = response.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
      const result = await response.json();
      throw new Error(result.message || 'The workbook could not be processed.');
    }

    const totalBytes = Number(response.headers.get('content-length')) || 0;
    const reader = response.body && response.body.getReader();
    const chunks = [];
    let receivedBytes = 0;
    if (reader) {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        chunks.push(value);
        receivedBytes += value.length;
        if (totalBytes) {
          const percent = Math.round((receivedBytes / totalBytes) * 100);
          progressPercent.textContent = `${percent}%`;
          progressFill.style.width = `${percent}%`;
          progressMessage.textContent = 'Preparing your updated workbook for download.';
        }
      }
      downloadBlob = new Blob(chunks, { type: contentType });
    } else {
      downloadBlob = await response.blob();
    }
    downloadName = getDownloadName(response.headers.get('content-disposition'));
    window.clearInterval(timerId);
    progressCard.hidden = true;
    successCard.hidden = false;
    successMessage.textContent = `${downloadName} is ready to download.`;
  } catch (error) {
    window.clearInterval(timerId);
    progressCard.hidden = true;
    processButton.disabled = false;
    showError(error.message || 'Something went wrong while processing the workbook.');
  }
});

downloadButton.addEventListener('click', () => {
  if (!downloadBlob) return;
  const url = URL.createObjectURL(downloadBlob);
  const link = document.createElement('a');
  link.href = url;
  link.download = downloadName;
  link.click();
  URL.revokeObjectURL(url);
});
