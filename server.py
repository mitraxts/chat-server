from flask import Flask, request, jsonify
import threading

app = Flask(__name__)

# Lista para armazenar os clientes e mensagens
clients = []
lock = threading.Lock()

@app.route('/')
def home():
    return "Servidor de chat está rodando!", 200

@app.route('/register', methods=['POST'])
def register_client():
    """
    Endpoint para registrar um novo cliente.
    Enviar um JSON com {"name": "Nome do cliente"}.
    """
    data = request.json
    name = data.get('name', '')
    if not name:
        return jsonify({"error": "Nome é obrigatório"}), 400
    
    with lock:
        # Verifica se o cliente já está registrado
        for client in clients:
            if client['name'] == name:
                return jsonify({"message": "Cliente já registrado"}), 200
        
        # Adiciona o cliente
        clients.append({'name': name, 'messages': []})
    return jsonify({"message": f"Cliente {name} registrado com sucesso!"}), 200

@app.route('/send', methods=['POST'])
def send_message():
    """
    Endpoint para enviar uma mensagem.
    Enviar um JSON com {"sender": "Nome do remetente", "message": "Texto da mensagem"}.
    """
    data = request.json
    sender = data.get('sender', '')
    message = data.get('message', '')

    if not sender or not message:
        return jsonify({"error": "Remetente e mensagem são obrigatórios"}), 400

    with lock:
        for client in clients:
            # Adiciona a mensagem para todos os clientes, exceto o remetente
            if client['name'] != sender:
                client['messages'].append({'sender': sender, 'message': message})
    
    return jsonify({"message": "Mensagem enviada com sucesso!"}), 200

@app.route('/receive', methods=['GET'])
def receive_messages():
    """
    Endpoint para receber mensagens de um cliente.
    Enviar como parâmetro na URL: ?name=NomeDoCliente.
    """
    name = request.args.get('name', '')

    if not name:
        return jsonify({"error": "Nome do cliente é obrigatório"}), 400

    with lock:
        for client in clients:
            if client['name'] == name:
                messages = client['messages']
                client['messages'] = []  # Limpa as mensagens após o recebimento
                return jsonify({"messages": messages}), 200
    
    return jsonify({"error": "Cliente não encontrado"}), 404

@app.route('/shutdown', methods=['POST'])
def shutdown():
    """
    Endpoint para desligar o servidor.
    Enviar uma requisição POST sem parâmetros.
    """
    shutdown_server = request.environ.get('werkzeug.server.shutdown')
    if shutdown_server:
        shutdown_server()
        return jsonify({"message": "Servidor desligado com sucesso!"}), 200
    else:
        return jsonify({"error": "Não foi possível desligar o servidor"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=12345)
