from flask import render_template
from app.punch import bp

#GET
@bp.route('/punch', methods=['GET'])
def punch():
    return render_template('punch.html')
#POST
@bp.route('/punch', methods=['POST'])
def punch_submit():
    # receber imagem via JSON ou form-data
    image_data = request.json.get('image')
    # decodificar base64 e salvar em uploads, ou processar diretamente
    # registrar timestamp no banco
    return jsonify({'status': 'ok'})