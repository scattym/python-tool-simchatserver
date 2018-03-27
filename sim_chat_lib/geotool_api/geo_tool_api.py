#!/usr/bin/env python
"""
Library to manage proxy to geotool operations through the rest framework
"""
import datetime
import traceback

import requests
import logging
import json
import simplejson
import os
from sim_chat_lib.geotool_api import common, device_api

logger = logging.getLogger(__name__)


def set_api_host(host):
    common.set_api_host(host)


def host_to_token_header(host):
    return common.host_to_token_header(host)


def coord_dec_to_point_field(longitude, latitude):
    # "SRID=4326;POINT (151.200152783 -33.8158162333)"
    return "SRID=4326;POINT (%s %s)" % (longitude, latitude)


# DEC = (DEG + (MIN * 1/60) + (SEC * 1/60 * 1/60))
def dms_to_dec(dms):
    dms_str = str(dms)
    dot_location = dms_str.index('.')
    degrees = dms_str[0:dot_location - 2]
    minutes_seconds = dms_str[dot_location - 2:]
    decimal = float(degrees) + (float(minutes_seconds) / 60)
    print(degrees, minutes_seconds, decimal)
    return decimal


# 3348.948974, S, 15112.009167, E
def coord_nmea_to_point_field(longitude, long_dir, latitude, lat_dir):
    normal_long = dms_to_dec(longitude)
    normal_lat = dms_to_dec(latitude)
    if long_dir.lower() == "w":
        normal_long = 0 - normal_long
    if lat_dir.lower() == "s":
        normal_lat = 0 - normal_lat
    # "SRID=4326;POINT (151.200152783 -33.8158162333)"
    return "SRID=4326;POINT (%s %s)" % (normal_long, normal_lat)


def get_device_pk(imei):
    return device_api.get_device_pk(imei)


def create_device(imei, *args, **kwargs):
    return device_api.create_device(imei, *args, **kwargs)


def create_report(device_pk):
    report = {
        "device": device_pk
    }
    result = common.post_to_api(common.REPORT_API, report)
    if result and "id" in result:
        return result["id"]
    return None


def create_report_gps(report_pk):
    data = {
        "report": report_pk
    }
    result = common.post_to_api(common.REPORT_GPS_API, data)
    if result and "id" in result:
        return result["id"]
    return None


def create_report_gps_rmc(report_gps_pk, time, status, location,
                          speed_knots, track_angle, date, mag_var_angle, mag_var_dir):
    data = {
        "report_gps": report_gps_pk,
        "time": time,
        "status": status,
        "location": location,
        "speed_knots": speed_knots,
        "track_angle": track_angle,
        "date": date,
        "magnetic_variation_angle": mag_var_angle,
        "magnetic_variation_direction": mag_var_dir,
    }
    result = common.post_to_api(common.REPORT_GPS_RMC_API, data)
    if result and "id" in result:
        return result["id"]
    return None


def create_report_gps_vtg(report_gps_pk, true_track,
                          mag_track, ground_speed_knots, ground_speed_kms):
    data = {
        "report_gps": report_gps_pk,
        "true_track": true_track,
        "magnetic_track": mag_track,
        "ground_speed_knots": ground_speed_knots,
        "ground_speed_kms": ground_speed_kms,
    }
    result = common.post_to_api(common.REPORT_GPS_VTG_API, data)
    if result and "id" in result:
        return result["id"]
    return None

    # report_gps = models.ForeignKey(ReportGPS, on_delete=models.CASCADE)
    # time = models.TimeField(null=True, blank=True)
    # location = gis_model.PointField(null=True, blank=True)
    # fix_quality = models.CharField(max_length=1, null=True, blank=True)
    # satellite_number = models.IntegerField(null=True, blank=True)
    # horizontal_dilution = models.FloatField(null=True, blank=True)
    # altitude = models.FloatField(null=True, blank=True)


def create_report_gps_gga(report_gps_pk, time, location,
                          fix_quality, satellite_number, horizontal_dilution, altitude):
    data = {
        "report_gps": report_gps_pk,
        "time": str(time),
        "location": location,
        "fix_quality": fix_quality,
        "satellite_number": satellite_number,
        "horizontal_dilution": horizontal_dilution,
        "altitude": altitude,

    }
    result = common.post_to_api(common.REPORT_GPS_GGA_API, data)
    if result and "id" in result:
        return result["id"]
    return None


if __name__ == '__main__':
    log_level = 11 - 2

    logger = logging.getLogger('')
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s'
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    set_api_host("localhost:8000")

    print(get_device_pk("77070407942500"))
    print(create_device("77070407942501"))
    print(create_device("770704079425", name="Another API test"))
    # report_pk = create_report(10)
    # report_gps_pk = create_report_gps(report_pk)
    # 031924.0, A, 3348.948974, S, 15112.009167, E, 0.0, 0.0, 141017,, ,
    # 151.200 -33.816
    location = coord_dec_to_point_field(151.200, -33.816)
    location = coord_nmea_to_point_field(15112.009167, 'E', 3348.948974, 'S')
    # report_gps_rmc_pk = create_report_gps_rmc(
    #     report_gps_pk,
    #     "03:19:24.0",
    #     "A",
    #     location,
    #     0.0,
    #     0.0,
    #     "2017-10-14",
    #     None,
    #     None)
    # # $GPVTG, 85.8, T,, M, 0.0, N, 0.0, K, A * 38
    # report_gps_vtg_pk = create_report_gps_vtg(
    #     report_gps_pk, 85.8, None, 0.0, 0.0)
    # create_report_gps_gga(
    #     report_gps_pk,
    #     "03:19:24.0",
    #     location,
    #     '1',
    #     7,
    #     0.9,
    #     200)
    # obdii_pk = create_obdii(
    #     10,
    #     "2017-07-04 04:07:07Z",
    #     1600,
    #     110,
    #     90,
    #     97,
    #     1000,
    #     90,
    #     300,
    #     34)

