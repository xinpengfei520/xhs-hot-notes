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
    const downloadButton = document.getElementById('downloadButton');
    
    let currentFile = null;
    let serverFilename = null;
    let outputFilename = null;
    
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
        downloadButton.style.display = 'none';  // 隐藏下载按钮
        showStatus('准备开始处理...', 'info');
        
        // 开始轮询进度
        const progressInterval = setInterval(() => {
            fetch('/progress')
                .then(response => response.json())
                .then(progress => {
                    console.log('Progress:', progress);  // 添加调试日志
                    if (progress.current && progress.total) {
                        const percentage = progress.percentage || Math.round((progress.current / progress.total) * 100);
                        showStatus(`正在处理第 ${progress.current} 条笔记，共 ${progress.total} 条 (${percentage}%)`, 'info');
                    }
                })
                .catch(error => console.error('获取进度失败:', error));  // 添加错误日志
        }, 1000);
        
        fetch('/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                filename: serverFilename
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
                outputFilename = data.output_file.split('/').pop();  // 获取文件名
                showStatus('处理完成！', 'success');
                downloadButton.style.display = 'inline-block';  // 显示下载按钮
            }
        })
        .catch(error => showStatus('处理失败: ' + error, 'error'))
        .finally(() => {
            processButton.disabled = false;
            clearInterval(progressInterval);
        });
    });
    
    // 添加下载按钮事件处理
    downloadButton.addEventListener('click', function() {
        if (!outputFilename) return;
        
        window.location.href = `/download/${outputFilename}`;
    });
    
    function showStatus(message, type) {
        status.textContent = message;
        status.className = `status-${type}`;
    }
}); 