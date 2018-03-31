from sim_chat_lib.geotool_api import common
import logging
import traceback
import io

logger = logging.getLogger(__name__)


def add_camera_image(device_pk, camera_number, camera_time, image_data_jpg):
    try:
        data = {
            "pk": device_pk,
            "camera_number": camera_number,
            "camera_time": str(camera_time),
        }
        camera_time_geotool_format = camera_time.strftime("%Y%m%d%H%M%S")
        files = [
            (
                'device', (None, str(device_pk)),
            ),
            (
                'camera_number', (None, str(camera_number)),
            ),
            (
                'camera_time', (None, str(camera_time)),
            ),
            (
                'image',
                (
                    'camera{}-{}.jpg'.format(camera_number, camera_time_geotool_format),
                    io.BytesIO(image_data_jpg),
                    'image/jpg'
                )
            )
        ]
        result = common.post_to_api(common.CAMERA_API, None, files=files)
        logger.debug("Add camera result was: ", result)
        if result:
            return result
    except Exception as err:
        logger.error("Exception in add camera image: %s", err)
        logger.error(
            "Payload: device pk: %s camera_number: %s camera_time: %s files: %s ",
            device_pk,
            camera_number,
            camera_time,
            image_data_jpg,
        )
        logger.error(traceback.format_exc())
    return None


if __name__ == "__main__":
    import base64
    import datetime
    log_level = 11 - 11

    logger = logging.getLogger('')
    logger.setLevel(log_level)
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    common.set_api_host("localhost:8000")

    file_base64 = (
        """/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0a"""
        """HBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/wAALCAACAAIBAREA/8QAHwAAAQUBAQEB"""
        """AQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1Fh"""
        """ByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZ"""
        """WmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXG"""
        """x8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/9oACAEBAAA/ACv/2Q=="""
    )

    file_data = base64.b64decode(file_base64)
    print(add_camera_image(24, 0, datetime.datetime.utcnow(), file_data))
