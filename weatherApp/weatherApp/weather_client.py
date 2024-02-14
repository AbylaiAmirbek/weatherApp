import socket

def request_weather(city):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        server_address = ('localhost', 12345)
        client_socket.connect(server_address)

        # отправка города в сервер
        client_socket.sendall(city.encode('utf-8'))

        # получение ответа с сервера и принт
        response = client_socket.recv(1024).decode('utf-8')
        print(response)

        # вопрос
        save_to_file = input("Do you want to save the weather data to a file? (yes/no): ")
        client_socket.sendall(save_to_file.encode('utf-8'))

if __name__ == "__main__":
    user_input = input("Enter city: ")
    request_weather(user_input)
