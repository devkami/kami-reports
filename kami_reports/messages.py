import json
import logging
from dataclasses import dataclass
from datetime import datetime as dt
from os import getenv
from typing import List

from jinja2 import Environment, FileSystemLoader
from kami_logging import benchmark_with, logging_with
from kami_messenger.botconversa import Botconversa
from kami_messenger.email_messenger import EmailMessenger
from kami_messenger.messenger import Message

from filemanager import delete_old_files

messages_looger = logging.getLogger('messages_generator')
loader = FileSystemLoader('messages')
env = Environment(loader=loader)


@dataclass
class Contact:

    name: str
    email: str
    phone: str
    groups: List[str]


@logging_with(messages_looger)
@benchmark_with(messages_looger)
def get_contacts_from_json(json_file) -> List[Contact]:
    contacts = []
    with open(json_file) as contacts_file:
        contacts_dict = json.load(contacts_file)

    for contact_dict in contacts_dict:
        contact = Contact(**contact_dict)
        contacts.append(contact)

    return contacts


def filter_contact_by_group(contacts, group) -> List[Contact]:
    return [contact for contact in contacts if group in contact.groups]


@logging_with(messages_looger)
@benchmark_with(messages_looger)
def generate_messages(
    contacts, gdrive_folder_id, template_message
) -> List[Message]:
    messages = []
    account_message_template = env.get_template(template_message)
    for contact in contacts:
        message_data = account_message_template.render(
            contact_phone=contact.phone,
            contact_name=contact.name,
            contact_email=contact.email,
            report_id_folder=gdrive_folder_id,
        )
        messages.append(message_data)
    return messages


@logging_with(messages_looger)
@benchmark_with(messages_looger)
def generate_messages_by_group(gdrive_folder_id, group):
    all_contacts = get_contacts_from_json('messages/contacts.json')
    filtered_contacts = filter_contact_by_group(all_contacts, group)
    return generate_messages(
        filtered_contacts, gdrive_folder_id, f'{group}_message.json'
    )


def send_email(message):
    email_messenger_str = {
        'name': 'Email - kamico.com.br',
        'messages': [message],
        'credentials': {
            'login': str(getenv('EMAIL_USER')),
            'password': str(getenv('EMAIL_PASSWORD')),
        },
        'engine': '',
    }
    email_messenger = EmailMessenger(**email_messenger_str)
    email_messenger.sendMessage()


def send_whatsapp_message(message):
    botconversa_data = {
        'name': 'Botconversa',
        'messages': [message],
        'credentials': {'api-key': str(getenv('BOTCONVERSA_API_KEY'))},
        'engine': '',
    }
    botconversa = Botconversa(**botconversa_data)
    botconversa.sendMessage()


@logging_with(messages_looger)
@benchmark_with(messages_looger)
def send_email_messages_by_group(gdrive_folder_id, group):
    for message in generate_messages_by_group(gdrive_folder_id, group):
        mess = Message(**json.loads(message)['email'])
        send_email(mess)


@logging_with(messages_looger)
@benchmark_with(messages_looger)
def send_whatsapp_messages_by_group(gdrive_folder_id, group):
    for message in generate_messages_by_group(gdrive_folder_id, group):
        mess = Message(**json.loads(message)['whatsapp'])
        send_whatsapp_message(mess)


@logging_with(messages_looger)
@benchmark_with(messages_looger)
def send_messages_by_group(gdrive_folder_id, group):
    send_email_messages_by_group(gdrive_folder_id, group)
    send_whatsapp_messages_by_group(gdrive_folder_id, group)
