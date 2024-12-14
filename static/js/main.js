document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileInput');
    const selectButton = document.getElementById('selectButton');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = fileInfo.querySelector('.file-name');
    const removeFile = fileInfo.querySelector('.remove-file');
    const processButton = document.getElementById('processButton');
    const cookieInput = document.getElementById('cookieInput');
    const cookieButton = document.getElementById('cookieButton');
    const status = document.getElementById('status');
    
    let currentFile = null;
    let serverFilename = null;
    
    // 文件选择
    selectButton.addEventListener('click', () => fileInput.click());
    
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        if (!file.name.endsWith('.xlsx')) {
            showStatus('只支持 .xlsx 格式的文件', 'error');
            return;
        }
        
        currentFile = file;
        fileName.textContent = file.name;
        fileInfo.style.display = 'block';
        processButton.disabled = false;
        
        // 上传文件
        const formData = new FormData();
        formData.append('file', file);
        
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showStatus(data.error, 'error');
                // 上传失败时重置状态
                currentFile = null;
                serverFilename = null;
                fileInfo.style.display = 'none';
                processButton.disabled = true;
            } else {
                // 保存服务器返回的文件名
                serverFilename = data.filename;
                showStatus('文件上传成功', 'success');
            }
        })
        .catch(error => {
            showStatus('上传失败: ' + error, 'error');
            // 上传失败时重置状态
            currentFile = null;
            serverFilename = null;
            fileInfo.style.display = 'none';
            processButton.disabled = true;
        });
    });
    
    // 移除文件
    removeFile.addEventListener('click', function() {
        currentFile = null;
        serverFilename = null;
        fileInput.value = '';
        fileInfo.style.display = 'none';
        processButton.disabled = true;
    });
    
    // Cookie 设置
    cookieButton.addEventListener('click', function() {
        if (cookieButton.textContent === '确定') {
            const cookie = cookieInput.value.trim();
            if (!cookie) {
                showStatus('请输入Cookie', 'error');
                return;
            }
            
            fetch('/set-cookie', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ cookie: cookie })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showStatus(data.error, 'error');
                } else {
                    cookieInput.disabled = true;
                    cookieButton.textContent = '编辑';
                    showStatus('Cookie已保存', 'success');
                }
            })
            .catch(error => showStatus('保存失败: ' + error, 'error'));
        } else {
            cookieInput.disabled = false;
            cookieButton.textContent = '确定';
        }
    });
    
    // 开始处理
    processButton.addEventListener('click', function() {
        if (!currentFile || !serverFilename) {
            showStatus('请先选择文件', 'error');
            return;
        }
        
        processButton.disabled = true;
        showStatus('正在处理...', 'info');
        
        fetch('/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                filename: serverFilename  // 使用服务器端的文件名
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('处理请求失败');
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                showStatus(data.error, 'error');
            } else {
                showStatus('处理完成: ' + data.output_file, 'success');
            }
        })
        .catch(error => showStatus('处理失败: ' + error, 'error'))
        .finally(() => {
            processButton.disabled = false;
        });
    });
    
    function showStatus(message, type) {
        status.textContent = message;
        status.className = `status-${type}`;
    }
}); 