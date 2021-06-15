from threading import Thread
import uvicorn

import server
import config

class MyThread(Thread):
    
    def __init__(self, name):
        """Инициализация потока"""
        Thread.__init__(self)
        self.name = name
    
    def run(self):
        """Запуск потока с сервером"""
        uvicorn.run(server.app, host=config.host, port=config.port, use_colors=False) #uvicorn server:app --host 127.0.0.1 --port 1234
    
def create_thread():
    my_thread = MyThread("server")
    my_thread.setDaemon("True")
    my_thread.start()


if __name__ == "__main__":
    pass