from flask import request, jsonify
from .models import db, Usuario, Mercado, Transacao
from flask import current_app as app
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import datetime
import jwt




def register_routes():
    @app.route('/', methods=['GET'])
    def home():
        return jsonify({"message": "Bem-vindo a API!"})

    # CRUD para Usuário
    @app.route('/usuario', methods=['POST'])
    def criar_usuario():
        data = request.get_json()

        # Validação de senha
        senha = data.get('senha')
        if not senha or len(senha) < 8 or len(senha) > 32:
            return jsonify({"error": "A senha deve ter entre 8 e 32 caracteres."}), 400

        # Criptografar a senha
        senha_criptografada = generate_password_hash(senha)

        # Verificar se o e-mail já existe
        if Usuario.query.filter_by(email=data['email']).first():
            return jsonify({"error": "E-mail já está em uso."}), 400

        # Criar o novo usuário
        novo_usuario = Usuario(nome=data['nome'], email=data['email'], senha=senha_criptografada)
        db.session.add(novo_usuario)
        db.session.commit()

        return jsonify({"message": "Usuário criado com sucesso!"}), 201

    @app.route('/usuario/<int:id>', methods=['GET'])
    def obter_usuario(id):
        usuario = Usuario.query.get(id)
        if not usuario:
            return jsonify({"error": "Usuário não encontrado."}), 404
        return jsonify({
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email
        }), 200

    @app.route('/usuario', methods=['GET'])
    def listar_usuarios():
        usuarios = Usuario.query.all()
        return jsonify([{
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email
        } for usuario in usuarios]), 200

    @app.route('/usuario/<int:id>', methods=['PUT'])
    def atualizar_usuario(id):
        usuario = Usuario.query.get(id)
        if not usuario:
            return jsonify({"error": "Usuário não encontrado."}), 404

        data = request.get_json()
        usuario.nome = data.get('nome', usuario.nome)
        usuario.email = data.get('email', usuario.email)
        
        senha = data.get('senha')
        if senha:
            if len(senha) < 8 or len(senha) > 32:
                return jsonify({"error": "A senha deve ter entre 8 e 32 caracteres."}), 400
            usuario.senha = generate_password_hash(senha)

        db.session.commit()
        return jsonify({"message": "Usuário atualizado com sucesso!"}), 200

    @app.route('/usuario/<int:id>', methods=['PATCH'])
    def atualizar_parcial_usuario(id):
        usuario = Usuario.query.get(id)
        if not usuario:
            return jsonify({"error": "Usuário não encontrado."}), 404

        data = request.get_json()
        if 'nome' in data:
            usuario.nome = data['nome']
        if 'email' in data:
            usuario.email = data['email']
        if 'senha' in data:
            senha = data['senha']
            if len(senha) < 8 or len(senha) > 32:
                return jsonify({"error": "A senha deve ter entre 8 e 32 caracteres."}), 400
            usuario.senha = generate_password_hash(senha)

        db.session.commit()
        return jsonify({"message": "Usuário atualizado parcialmente com sucesso!"}), 200

    @app.route('/usuario/<int:id>', methods=['DELETE'])
    def deletar_usuario(id):
        usuario = Usuario.query.get(id)
        if not usuario:
            return jsonify({"error": "Usuário não encontrado."}), 404
        db.session.delete(usuario)
        db.session.commit()
        return jsonify({"message": "Usuário deletado com sucesso!"}), 200


    @app.route('/login', methods=['POST'])
    def login_usuario():
        data = request.get_json()

        # Buscar o usuário pelo e-mail
        usuario = Usuario.query.filter_by(email=data['email']).first()

        if usuario and check_password_hash(usuario.senha, data['senha']):
            token = jwt.encode({
                'user_id': usuario.id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            }, app.config['SECRET_KEY'])

            return jsonify({"token": token,"usuario_id":usuario.id}), 200
        else:
            return jsonify({"error": "E-mail ou senha incorretos."}), 401


    # @app.route('/protected', methods=['GET'])
    # def protected():
    #     token = request.headers.get('Authorization')
    #     if not token:
    #         return jsonify({'message': 'Token is missing!'}), 401

    #     try:
    #         data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
    #         current_user = Usuario.query.get(data['user_id'])
    #     except:
    #         return jsonify({'message': 'Token is invalid!'}), 401

    #     return jsonify({'message': f'Welcome {current_user.email}!'})

    @app.route('/protected', methods=['GET'])
    def protected():
        token = request.headers.get('Authorization')
        print(token)
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        # Remove o prefixo 'Bearer ' do token, se estiver presente
        if token.startswith('Bearer '):
            token = token.split(' ')[1]

        try:
            # Decodifica o token JWT
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            
            current_user = Usuario.query.get(data['user_id'])
            
            if not current_user:
                return jsonify({'message': 'User not found!'}), 401
            
        except jwt.ExpiredSignatureError:
            print('except 1')
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            print('except 1')
            return jsonify({'message': 'Token is invalid!'}), 401

        return jsonify({'message': f'Welcome {current_user.email}!'})






    # CRUD para Mercado
    
        # Criar um novo mercado
    @app.route('/mercados', methods=['POST'])
    def criar_mercado():
        data = request.get_json()

        nome = data.get('nome')
        usuario_id = data.get('usuario_id')

        if not nome or not usuario_id:
            return jsonify({"error": "Todos os campos (nome, usuario_id) são obrigatórios."}), 400

        try:
            # Cria um novo mercado com os dados fornecidos
            novo_mercado = Mercado(nome=nome, usuario_id=usuario_id)

            # Adiciona ao banco de dados
            db.session.add(novo_mercado)
            db.session.commit()

            return jsonify({
                "message": "Mercado criado com sucesso.",
                "mercado": {
                    "id": novo_mercado.id,
                    "nome": novo_mercado.nome,
                    "usuario_id": novo_mercado.usuario_id
                }
            }), 201

        except Exception as e:
            db.session.rollback()  # Desfaz a transação em caso de erro
            return jsonify({"error": str(e)}), 500



    
    
    @app.route('/mercado/<int:id>', methods=['GET'])
    def obter_mercado(id):
        mercado = Mercado.query.get(id)
        if not mercado:
            return jsonify({"error": "Mercado não encontrado."}), 404
        usuario = Usuario.query.get(mercado.usuario_id)
        return jsonify({
            "id": mercado.id,
            "nome": mercado.nome,
            "usuario": {
                "id": usuario.id,
                "nome": usuario.nome,
                "email": usuario.email
            }
        }), 200



    @app.route('/mercado', methods=['GET'])
    def listar_mercados():
        mercados = Mercado.query.all()

        if not mercados:
            return jsonify({"message": "Nenhum mercado registrado."}), 200

        mercados_lista = [{
            "id": mercado.id,
            "nome": mercado.nome,
            "usuario": {
                "id": mercado.usuario.id,
                "nome": mercado.usuario.nome,
                "email": mercado.usuario.email
            }
        } for mercado in mercados]

        return jsonify(mercados_lista), 200







    # Rota para listar mercados de um usuário específico
    @app.route('/mercado/usuario/<int:usuario_id>', methods=['GET'])
    def listar_mercados_por_usuario(usuario_id):
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return jsonify({"error": "Usuário não encontrado."}), 404

        mercados = Mercado.query.filter_by(usuario_id=usuario_id).all()
        
        if not mercados:
            return jsonify({"message": "Nenhum mercado encontrado para este usuário."}), 200

        return jsonify([{
            "id": mercado.id,
            "nome": mercado.nome,
            "usuario": {
                "id": usuario.id,
                "nome": usuario.nome,
                "email": usuario.email
            }
        } for mercado in mercados]), 200






    @app.route('/mercado/<int:id>', methods=['PUT'])
    def atualizar_mercado(id):
        mercado = Mercado.query.get(id)
        if not mercado:
            return jsonify({"error": "Mercado não encontrado."}), 404

        data = request.get_json()
        mercado.nome = data.get('nome', mercado.nome)
        mercado.usuario_id = data.get('usuario_id', mercado.usuario_id)
        db.session.commit()

        return jsonify({"message": "Mercado atualizado com sucesso!"}), 200

    @app.route('/mercado/<int:id>', methods=['PATCH'])
    def atualizar_parcial_mercado(id):
        mercado = Mercado.query.get(id)
        if not mercado:
            return jsonify({"error": "Mercado não encontrado."}), 404

        data = request.get_json()
        if 'nome' in data:
            mercado.nome = data['nome']
        if 'usuario_id' in data:
            mercado.usuario_id = data['usuario_id']
        
        db.session.commit()
        return jsonify({"message": "Mercado atualizado parcialmente com sucesso!"}), 200

    @app.route('/mercado/<int:id>', methods=['DELETE'])
    def deletar_mercado(id):
        mercado = Mercado.query.get(id)
        if not mercado:
            return jsonify({"error": "Mercado não encontrado."}), 404
        db.session.delete(mercado)
        db.session.commit()
        return jsonify({"message": "Mercado deletado com sucesso!"}), 200

    # CRUD para Transação
    
    @app.route('/transacoes', methods=['POST'])
    def criar_transacao():
        data = request.get_json()
        
        valor = data.get('valor')
        tipo = data.get('tipo')
        odd = data.get('odd', None)
        total = data.get('total', None)
        usuario_id = data.get('usuario_id')
        
        if not valor or not tipo or not usuario_id:
            return jsonify({"error": "Todos os campos (valor, tipo, usuario_id) são obrigatórios."}), 400
        
        try:
            # Validação específica para tipos de transação
            if tipo == 'green' and (not odd or total is None):
                return jsonify({"error": "Campos 'odd' e 'total' são obrigatórios para transações do tipo green."}), 400
            
            # Cria uma nova transação com os dados fornecidos
            nova_transacao = Transacao(valor=valor, tipo=tipo, odd=odd, total=total, usuario_id=usuario_id)
            
            # Adiciona ao banco de dados
            db.session.add(nova_transacao)
            db.session.commit()

            return jsonify({
                "message": "Transação criada com sucesso.",
                "transacao": {
                    "id": nova_transacao.id,
                    "valor": nova_transacao.valor,
                    "tipo": nova_transacao.tipo,
                    "odd": nova_transacao.odd,
                    "total": nova_transacao.total,
                    "usuario_id": nova_transacao.usuario_id
                }
            }), 201

        except Exception as e:
            db.session.rollback()  # Desfaz a transação em caso de erro
            return jsonify({"error": str(e)}), 500

        
        
    
    
    
    
    
    @app.route('/transacao/<int:id>', methods=['GET'])
    def obter_transacao(id):
        transacao = Transacao.query.get(id)
        if not transacao:
            return jsonify({"error": "Transação não encontrada."}), 404
        usuario = Usuario.query.get(transacao.usuario_id)
        return jsonify({
            "id": transacao.id,
            "valor": transacao.valor,
            "tipo": transacao.tipo,
            "usuario": {
                "id": usuario.id,
                "nome": usuario.nome,
                "email": usuario.email
            }
        }), 200

    @app.route('/transacao/usuario/<int:usuario_id>', methods=['GET'])
    def listar_transacoes_por_usuario(usuario_id):
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return jsonify({"error": "Usuário não encontrado."}), 404

        transacoes = Transacao.query.filter_by(usuario_id=usuario_id).all()
        
        if not transacoes:
            return jsonify({"message": "Nenhuma transação encontrada para este usuário."}), 200

        # Inicializar o valor total
        soma_total = 11400  # Partimos de 11.400, você pode usar outro valor inicial conforme sua lógica de negócio

        # Calcular a soma total considerando os tipos de transação
        for transacao in transacoes:
            if transacao.tipo == 'green' and transacao.odd is not None:
                soma_total += transacao.valor * transacao.odd  # Multiplicar valor pela odd e somar
            elif transacao.tipo == 'red':
                soma_total -= transacao.valor  # Subtrair o valor do total
            elif transacao.tipo == 'aporte':
                soma_total += transacao.valor  # Somar o valor ao total
            elif transacao.tipo == 'retirada':
                soma_total -= transacao.valor  # Subtrair o valor do total

        return jsonify({
            "transacoes": [{
                "valor": transacao.valor,
                "tipo": transacao.tipo,
                "odd": transacao.odd if transacao.odd is not None else '',  # Deixa vazio se None
                "total": transacao.total if transacao.total is not None else ''  # Deixa vazio se None
            } for transacao in transacoes],
            "soma_total": soma_total
        }), 200









    @app.route('/transacao/<int:id>', methods=['PUT'])
    def atualizar_transacao(id):
        transacao = Transacao.query.get(id)
        if not transacao:
            return jsonify({"error": "Transação não encontrada."}), 404

        data = request.get_json()
        transacao.valor = data.get('valor', transacao.valor)
        transacao.tipo = data.get('tipo', transacao.tipo)
        transacao.usuario_id = data.get('usuario_id', transacao.usuario_id)
        db.session.commit()

        return jsonify({"message": "Transação atualizada com sucesso!"}), 200

    @app.route('/transacao/<int:id>', methods=['PATCH'])
    def atualizar_parcial_transacao(id):
        transacao = Transacao.query.get(id)
        if not transacao:
            return jsonify({"error": "Transação não encontrada."}), 404

        data = request.get_json()
        if 'valor' in data:
            transacao.valor = data['valor']
        if 'tipo' in data:
            transacao.tipo = data['tipo']
        if 'usuario_id' in data:
            transacao.usuario_id = data['usuario_id']
        
        db.session.commit()
        return jsonify({"message": "Transação atualizada parcialmente com sucesso!"}), 200

    @app.route('/transacao/<int:id>', methods=['DELETE'])
    def deletar_transacao(id):
        transacao = Transacao.query.get(id)
        if not transacao:
            return jsonify({"error": "Transação não encontrada."}), 404
        db.session.delete(transacao)
        db.session.commit()
        return jsonify({"message": "Transação deletada com sucesso!"}), 200





