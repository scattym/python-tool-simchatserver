import os

from celery import Celery
from kombu import Exchange, Queue
from kombu.common import Broadcast
from sim_chat_lib.master import send_take_photo_by_imei, send_photo_list_by_imei, send_firmware_update, \
    send_restart_device, send_restart_gps, send_toggle_debug, send_set_pin, send_set_snapshot_parameters
from sim_chat_lib.master import send_cancel_firmware_update, send_update_configuration

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'amqp://guest@localhost')
sim_chat_server_celery_app = Celery('sim_chat_server_tasks', broker=CELERY_BROKER_URL, )
sim_chat_server_celery_app.conf.broker_transport_options = {'region': 'ap-southeast-2'}

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


@sim_chat_server_celery_app.task(name='sim_chat_lib.celerytasks.sendcommand.update_configuration')
def update_configuration(imei):
    result = send_update_configuration(imei)
    return 'Issued configuration update for device {} with result {}'.format(imei, result)


@sim_chat_server_celery_app.task(name='sim_chat_lib.celerytasks.sendcommand.restart_device')
def restart_device(imei):
    result = send_restart_device(imei)
    return 'Issued device restart for device {} with result {}'.format(imei, result)


@sim_chat_server_celery_app.task(name='sim_chat_lib.celerytasks.sendcommand.restart_gps')
def restart_gps(imei):
    result = send_restart_gps(imei)
    return 'Issued gps restart for device {} with result {}'.format(imei, result)


@sim_chat_server_celery_app.task(name='sim_chat_lib.celerytasks.sendcommand.toggle_debug')
def toggle_debug(imei):
    result = send_toggle_debug(imei)
    return 'Issued debug toggle for device {} with result {}'.format(imei, result)


@sim_chat_server_celery_app.task(name='sim_chat_lib.celerytasks.sendcommand.set_pin')
def set_pin(imei, pin, state):
    result = send_set_pin(imei, pin, state)
    return 'Issued debug toggle for device {} with result {}'.format(imei, result)


@sim_chat_server_celery_app.task(name='sim_chat_lib.celerytasks.sendcommand.set_snapshot_parameters')
def set_snapshot_parameters(imei, event_code, interval, count, upload, delete):
    result = send_set_snapshot_parameters(imei, event_code, interval, count, upload, delete)
    return 'Issued debug toggle for device {} with result {}'.format(imei, result)


default_exchange = Exchange('sim_chat_lib.celerytasks.sendcommand.default', type='direct')
sim_chat_server_celery_app.conf.task_queues = (
    Broadcast('sim_chat_lib.celerytasks.sendcommand.broadcast_tasks', 'broadcast_queue'),
    Queue(
        'sim_chat_lib.celerytasks.sendcommand.default',
        default_exchange,
        routing_key='sim_chat_lib.celerytasks.sendcommand.default'
    )
)
sim_chat_server_celery_app.conf.task_routes = (route_for_simchatcelery,)
