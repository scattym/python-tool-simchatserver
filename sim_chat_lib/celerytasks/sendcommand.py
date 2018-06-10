import os

from celery import Celery
from kombu import Exchange, Queue
from kombu.common import Broadcast
from sim_chat_lib.master import send_take_photo_by_imei, send_photo_list_by_imei, send_firmware_update
from sim_chat_lib.master import send_cancel_firmware_update

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'amqp://guest@localhost')
sim_chat_server_celery_app = Celery('sim_chat_server_tasks', broker=CELERY_BROKER_URL)

#     {
#     'sim_chat_lib.celerytasks.sendcommand.take_photo': {
#         'queue': 'broadcast_tasks',
#         'exchange': 'broadcast_tasks',
#     },
#     '*': 'default',
# }


def route_for_simchatcelery(name, args, kwargs, options, task=None, **kw):
    if name == 'NOSUCHCOMMANDNAMEsim_chat_lib.celerytasks.sendcommand.take_photo':
        return {
            'exchange': 'sim_chat_lib.celerytasks.sendcommand.default',
            'queue': 'sim_chat_lib.celerytasks.sendcommand.default',
        }
    else:
        return {
            'exchange': 'sim_chat_lib.celerytasks.sendcommand.broadcast_tasks',
            'queue': 'sim_chat_lib.celerytasks.sendcommand.broadcast_tasks',
        }



@sim_chat_server_celery_app.task(name='sim_chat_lib.celerytasks.sendcommand.take_photo')
def take_photo(identifier, *args, **kwrgs):
    result = send_take_photo_by_imei(identifier)
    return 'Issued take photo command for device {} with result {}'.format(identifier, result)


@sim_chat_server_celery_app.task(name='sim_chat_lib.celerytasks.sendcommand.get_file')
def get_file_list(identifier):
    result = send_photo_list_by_imei(identifier)
    return 'Issued photo list command for device {} with result {}'.format(identifier, result)


@sim_chat_server_celery_app.task(name='sim_chat_lib.celerytasks.sendcommand.firmware_update')
def firmware_update(imei):
    result = send_firmware_update(imei)
    return 'Issued firmware update command for device {} with result {}'.format(imei, result)


@sim_chat_server_celery_app.task(name='sim_chat_lib.celerytasks.sendcommand.cancel_firmware_update')
def cancel_firmware_update(imei):
    result = send_cancel_firmware_update(imei)
    return 'Issued cancel firmware update command for device {} with result {}'.format(imei, result)


default_exchange = Exchange('sim_chat_lib.celerytasks.sendcommand.default', type='direct')
sim_chat_server_celery_app.conf.task_queues = (
    Broadcast('sim_chat_lib.celerytasks.sendcommand.broadcast_tasks'),
    Queue(
        'sim_chat_lib.celerytasks.sendcommand.default',
        default_exchange,
        routing_key='sim_chat_lib.celerytasks.sendcommand.default'
    )
)
sim_chat_server_celery_app.conf.task_routes = (route_for_simchatcelery,)
