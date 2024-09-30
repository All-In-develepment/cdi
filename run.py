from app import create_app
from flask import Flask, jsonify
from flask_cors import CORS
# from flask_jwt_extended import JWTManager
# Cria a aplicação Flask usando a função create_app
app = create_app()
CORS(app)

if __name__ == "__main__":
    # Inicia o servidor Flask
    app.run(host="0.0.0.0", port=5000, debug=True)


