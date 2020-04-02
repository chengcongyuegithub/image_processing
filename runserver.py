from app import app, socketio

if __name__ == '__main__':
    app.run(debug=True)
    socketio.run(app, port=8080, debug=True)
