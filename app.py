from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
from processor import process_notes
import logging

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

# 在应用启动时确保上传目录存在并有正确的权限
upload_dir = app.config['UPLOAD_FOLDER']
if not os.path.exists(upload_dir):
    try:
        os.makedirs(upload_dir, mode=0o755)
        logging.info(f'创建上传目录: {upload_dir}')
    except Exception as e:
        logging.error(f'创建上传目录失败: {str(e)}')

# 存储当前的 cookie
current_cookie = ''

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        logging.error('没有文件被上传')
        return jsonify({'error': '没有文件被上传'}), 400
    
    file = request.files['file']
    if file.filename == '':
        logging.error('没有选择文件')
        return jsonify({'error': '没有选择文件'}), 400
        
    if not file.filename.endswith('.xlsx'):
        logging.error(f'不支持的文件格式: {file.filename}')
        return jsonify({'error': '只支持 .xlsx 格式的文件'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    logging.info(f'保存文件到: {filepath}')
    file.save(filepath)
    
    if os.path.exists(filepath):
        logging.info(f'文件保存成功: {filepath}')
    else:
        logging.error(f'文件保存失败: {filepath}')
        return jsonify({'error': '文件保存失败'}), 500
    
    return jsonify({
        'message': '文件上传成功',
        'filename': filename
    })

@app.route('/set-cookie', methods=['POST'])
def set_cookie():
    global current_cookie
    current_cookie = request.json.get('cookie', '')
    return jsonify({'message': 'Cookie 已保存'})

@app.route('/process', methods=['POST'])
def start_process():
    filename = request.json.get('filename')
    if not filename:
        logging.error('未提供文件名')
        return jsonify({'error': '请先上传文件'}), 400
        
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    logging.info(f'处理文件: {filepath}')
    
    if not os.path.exists(filepath):
        logging.error(f'文件不存在: {filepath}')
        return jsonify({'error': '文件不存在'}), 400
    
    try:
        output_file = process_notes(filepath, current_cookie)
        return jsonify({
            'message': '处理完成',
            'output_file': output_file
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 