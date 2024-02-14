import requests
import json
import logging
import socket
class Weather:
    def __init__(self, api_key):
        self.api_key = api_key
        self.logger = self.setup_logger()

    def setup_logger(self):
        logger = logging.getLogger("weather_logger")
        logger.setLevel(logging.DEBUG)

        # создание консоля handler и set level для DEBUG
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # создание форматировщика
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # добавление форматировщика в handler
        ch.setFormatter(formatter)

        # добавление handler в logger
        logger.addHandler(ch)

        return logger

    def get_weather_data(self, city):

        try:
            response = requests.get(
                f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&APPID={self.api_key}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as errh:
            self.logger.error(f"HTTP Error: {errh}")
        except requests.exceptions.ConnectionError as errc:
            self.logger.error(f"Error Connecting: {errc}")
        except requests.exceptions.Timeout as errt:
            self.logger.error(f"Timeout Error: {errt}")
        except requests.exceptions.RequestException as err:
            self.logger.error(f"An unexpected error occurred: {err}")
        return None

    def display_weather(self, city, weather_data):
        if weather_data and weather_data.get('cod') == '404':
            self.logger.warning("No City Found")
        elif weather_data:
            weather = weather_data['weather'][0]['main']
            temp_celsius = round(weather_data['main']['temp'])

            return f"\nThe weather in {city} is: {weather}\nThe temperature in {city} is: {temp_celsius}°C\n"

    def save_to_file(self, city, weather_data, filename="weather_data.json"):
        try:
            with open(filename, 'w') as file:
                json.dump({'city': city, 'data': weather_data}, file)
            self.logger.info(f"Weather data saved to {filename}")
        except Exception as e:
            self.logger.error(f"An error occurred while saving to file: {e}")


def start_server(api_key):
    # создание TCP/IP сокета
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # связка сокета к адресу и порту
    server_address = ('localhost', 12345)
    server_socket.bind(server_address)

    # прослушивание входящих подключений
    server_socket.listen(1)

    print(f"Server listening on {server_address}")

    while True:
        # установления соединения
        print("Waiting for a connection...")
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")

        try:
            weather_obj = Weather(api_key)

            # получение города
            city = client_socket.recv(1024).decode('utf-8')
            print(f"Received request for weather data for {city}")

            # получение информацию о погоде
            data = weather_obj.get_weather_data(city)

            if data:
                # отображение информацию о погоде
                response = weather_obj.display_weather(city, data)

                # Send the response back to the client
                client_socket.sendall(response.encode('utf-8'))
                print("Response sent to the client")

                # сохранение в файл
                save_to_file = client_socket.recv(1024).decode('utf-8')
                if save_to_file.lower() == 'yes':
                    weather_obj.save_to_file(city, data)
                    print("Weather data saved successfully.")

        finally:
            # очистка соединение
            client_socket.close()


if __name__ == "__main__":
    api_key = '30d4741c779ba94c470ca1f63045390a'

    # запуск сервера
    start_server(api_key)
