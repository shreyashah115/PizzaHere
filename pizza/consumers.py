# pizza/consumers.py
from channels.generic.websocket import WebsocketConsumer
import json
from .models import User, Order
from .bot_messages import BOT_MESSAGES
import random
from datetime import datetime


order_statuses = {1: "being prepared", 2: "being packed", 3: "out for delivery", 4: "delivered"}

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.bot_message = "Hi, welcome to Pizzociety, please share your 10 digit mobile number."
        self.send(text_data=json.dumps({
            'bot_message': self.bot_message
        }))

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        if self.bot_message in [BOT_MESSAGES.get("mobile"), BOT_MESSAGES.get("incorrect_mobile"), BOT_MESSAGES.get("ask_mobile")]:
            if message.isdigit() and len(message) == 10:
                self.mobile = int(message)
                try:
                    user_exists = User.objects.get(phone=int(message))
                    user_details = user_exists.__dict__
                    self.bot_message = "Welcome back, {}.\n".format(user_details.get("name"))
                    self.bot_message += BOT_MESSAGES.get("first_question")
                except Exception:
                    self.bot_message = BOT_MESSAGES.get("name")
            else:
                if self.talk_to_bot(message):
                    self.bot_message = BOT_MESSAGES.get("incorrect_mobile")

        elif self.bot_message == BOT_MESSAGES.get("name"):
            self.name = message
            self.bot_message = BOT_MESSAGES.get("address")

        elif self.bot_message == BOT_MESSAGES.get("address"):
            self.address = message
            push_user_details = User(name=self.name, phone=self.mobile, address=self.address)
            push_user_details.save()
            self.bot_message = BOT_MESSAGES.get("first_question")

        elif BOT_MESSAGES.get("first_question") in self.bot_message:
            if message.lower() in ["1", "order a pizza", "order"]:
                self.bot_message = BOT_MESSAGES.get("pizza_choices")
            elif message.lower() in ["2", "track my order", "track"]:
                self.bot_message = BOT_MESSAGES.get("order_id")
            else:
                self.bot_message = BOT_MESSAGES.get("first_question")

        elif self.bot_message == BOT_MESSAGES.get("pizza_choices"):
            if message.lower() in ["1", "2", "3", "4", "mexican delight", "tofu supreme", "margherrita", "farmhouse"]:
                self.bot_message = BOT_MESSAGES.get("base_options")
            else:
                self.bot_message = BOT_MESSAGES.get("first_question")

        elif self.bot_message == BOT_MESSAGES.get("base_options"):
            if message.lower() in ["1", "2", "3", "wheat", "multigrain", "normal"]:
                self.bot_message = BOT_MESSAGES.get("size_options")
            else:
                self.bot_message = BOT_MESSAGES.get("base_options")

        elif self.bot_message == BOT_MESSAGES.get("size_options"):
            if message.lower() in ["1", "2", "3", "regular", "medium", "large"]:
                random_order_id = self.create_order()
                self.bot_message = "Your order has been placed. Here's your order ID: {}.\n".format(random_order_id)
                self.bot_message += BOT_MESSAGES.get("thanks-bye")

        elif self.bot_message == BOT_MESSAGES.get("order_id"):
            if message.isdigit():
                try:
                    order_status = self.fetch_order_status(message)
                    self.bot_message = "Your order is {}.\n".format(order_status)
                    self.bot_message += BOT_MESSAGES.get("thanks-bye")
                except Exception:
                    self.bot_message = BOT_MESSAGES.get("invalid_order")

        else:
            if self.talk_to_bot(message):
                self.bot_message = BOT_MESSAGES.get("ask_mobile")

        self.send(text_data=json.dumps({
            'bot_message': self.bot_message,
            'user_message': message
        }))

    def talk_to_bot(self, message):
        if message.lower() in BOT_MESSAGES.get("user-hello"):
            self.bot_message = random.choice(BOT_MESSAGES.get("bot-hello"))
        elif message.lower() in BOT_MESSAGES.get("user-whatsup"):
            self.bot_message = random.choice(BOT_MESSAGES.get("bot-whatsup"))
        elif message.lower() in BOT_MESSAGES.get("user-greeting"):
            self.bot_message = random.choice(BOT_MESSAGES.get("bot-greeting"))
        else:
            return True

    def create_order(self):
        random_order_id = random.randint(10**(6-1),10**6-1)
        user_model_object = User.objects.get(phone=self.mobile)
        user_details = user_model_object.__dict__
        fetched_user_id = user_details.get("id")
        order_object = Order(order_id=random_order_id, user_id=fetched_user_id, order_status=1)
        order_object.save()
        return random_order_id
    
    def fetch_order_status(self, message):
        order_exists = Order.objects.get(order_id=int(message))
        order_details = order_exists.__dict__
        order_status = order_details.get("order_status")
        creation_date = order_details.get("created_on")
        creation_date = creation_date.replace(tzinfo=None)
        time_passed = datetime.now() - creation_date
        time_passed_in_minutes = int(time_passed.seconds/60)
        if time_passed_in_minutes < 2:
            order_status = order_statuses.get(1)
        elif 2 <= time_passed_in_minutes < 4:
            order_status = order_statuses.get(2)
        elif 4 <= time_passed_in_minutes < 5:
            order_status = order_statuses.get(3)
        else:
            order_status = order_statuses.get(4)
        return order_status

