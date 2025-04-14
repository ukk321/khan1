import datetime
import json

from django import template
from django.db import connection

register = template.Library()


def get_sorted_contact_us(days=None, start_time=None, end_time=None):
    with connection.cursor() as cursor:
        if days:
            cursor.callproc('GetSortedContactUs', [days, None, None])
        else:
            cursor.callproc('GetSortedContactUs', [None, start_time, end_time])
        results = cursor.fetchall()

        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns, row)) for row in results]

    return data


@register.inclusion_tag('admin/contact_queries_table.html')
def dashboard_graph_contact_us_tag(days=None, start_time=None, end_time=None):
    if days:
        days = int(days)
        extract_data = get_sorted_contact_us(days=days)
    else:
        start_date_time = datetime.datetime.fromisoformat(start_time)
        end_date_time = datetime.datetime.fromisoformat(end_time)
        extract_data = get_sorted_contact_us(start_time=start_date_time, end_time=end_date_time)
    return {'contact_us_data': extract_data}


def get_sorted_booking_data(days=None, start_time=None, end_time=None):
    with connection.cursor() as cursor:
        if days:
            cursor.callproc('GetSortedBookings', [days, None, None])
        else:
            cursor.callproc('GetSortedBookings', [None, start_time, end_time])
        results = cursor.fetchall()

        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns, row)) for row in results]

    return data


@register.inclusion_tag('admin/booking_table.html')
def dashboard_graph_booking_tag(days=None, start_time=None, end_time=None):
    if days:
        days = int(days)
        extract_data = get_sorted_booking_data(days=days)
    else:
        start_date_time = datetime.datetime.fromisoformat(start_time)
        end_date_time = datetime.datetime.fromisoformat(end_time)
        extract_data = get_sorted_booking_data(start_time=start_date_time, end_time=end_date_time)
    return {'booking_data': extract_data}


def get_booking_stats(days=None, start_time=None, end_time=None):
    with connection.cursor() as cursor:
        if days:
            cursor.callproc('GetBookingStats', [days, None, None])
        else:
            cursor.callproc('GetBookingStats', [None, start_time, end_time])
        results = cursor.fetchall()

        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns, row)) for row in results]

    return data


@register.inclusion_tag('admin/pie_chart.html')
def dashboard_graph_booking_stats_tag(days=None, start_time=None, end_time=None):
    start_date_time = datetime.datetime.fromisoformat(start_time) if start_time else None
    end_date_time = datetime.datetime.fromisoformat(end_time) if end_time else None

    extract_data = get_booking_stats(days=days, start_time=start_date_time, end_time=end_date_time)
    return {'booking_stats_data': extract_data}


def get_monthly_booking_counts(days=None, start_time=None, end_time=None):
    with connection.cursor() as cursor:
        if days:
            cursor.callproc('GetMonthlyBookingCounts', [days, None, None])
        else:
            cursor.callproc('GetMonthlyBookingCounts', [None, start_time, end_time])
        results = cursor.fetchall()
        monthly_counts = {month: 0 for month in range(1, 13)}
        for row in results:
            monthly_counts[row[0]] = row[1]

    return [monthly_counts[month] for month in range(1, 13)]


@register.inclusion_tag('admin/bar_chart.html')
def dashboard_graph_monthly_bookings_tag(days=None, start_time=None, end_time=None):
    if days:
        days = int(days)
        booking_counts = get_monthly_booking_counts(days)
    else:
        start_date_time = datetime.datetime.fromisoformat(start_time)
        end_date_time = datetime.datetime.fromisoformat(end_time)
        booking_counts = get_monthly_booking_counts(start_time=start_date_time, end_time=end_date_time)
    return {'monthly_booking_counts': booking_counts}


def get_sub_service_hierarchy_data(days=None, start_time=None, end_time=None):
    with connection.cursor() as cursor:
        if days:
            cursor.callproc('GetBookingStatistics', [days, None, None])
        else:
            cursor.callproc('GetBookingStatistics', [None, start_time, end_time])
        results = cursor.fetchall()

        columns = [col[0] for col in cursor.description]
        data = [dict(zip(columns, row)) for row in results]

        hierarchy_data = create_sunburst_chart_data(data)

        return hierarchy_data


def create_sunburst_chart_data(flat_data):
    root = {"name": "Booking Frequency", "children": []}

    if not flat_data:
        return root

    deals = {}
    services = {}

    for entry in flat_data:
        deal_name = entry.get("dealName", "")
        service_name = entry.get("serviceName", "")
        cat_name = entry.get("catName", "")
        sub_service_name = entry.get("subServiceName", "")

        if deal_name:
            if deal_name not in deals:
                deals[deal_name] = 0
            deals[deal_name] += int(entry.get("NoOfBookingsInDeals", 0))

        if service_name:
            if service_name not in services:
                services[service_name] = {
                    "total": 0,
                    "categories": {}
                }
            services[service_name]["total"] += int(entry.get("NoOfBookingsInServices", 0))

            if cat_name:
                if cat_name not in services[service_name]["categories"]:
                    services[service_name]["categories"][cat_name] = {
                        "total": 0,
                        "sub_services": {}
                    }
                services[service_name]["categories"][cat_name]["total"] += int(entry.get("NoOfBookingsInCategories", 0))

                if sub_service_name:
                    if sub_service_name not in services[service_name]["categories"][cat_name]["sub_services"]:
                        services[service_name]["categories"][cat_name]["sub_services"][sub_service_name] = 0
                    services[service_name]["categories"][cat_name]["sub_services"][sub_service_name] += int(entry.get("NoOfBookingsInSubServices", 0))

    deals_node = {"name": "Deals", "value": sum(deals.values()), "children": []}
    for deal_name, count in deals.items():
        deals_node["children"].append({"name": deal_name, "value": count})
    root["children"].append(deals_node)

    services_node = {"name": "Services", "value": sum(service["total"] for service in services.values()), "children": []}
    for service_name, service_data in services.items():
        service_node = {"name": service_name, "value": service_data["total"], "children": []}
        for cat_name, cat_data in service_data["categories"].items():
            cat_node = {"name": cat_name, "value": cat_data["total"], "children": []}
            for sub_service_name, sub_service_count in cat_data["sub_services"].items():
                cat_node["children"].append({"name": sub_service_name, "value": sub_service_count})
            service_node["children"].append(cat_node)
        services_node["children"].append(service_node)

    root["children"].append(services_node)

    return root


@register.inclusion_tag('admin/sunburst.html')
def dashboard_graph_sub_service_tag(days=None, start_time=None, end_time=None):
    if days:
        days = int(days)
        extract_data = get_sub_service_hierarchy_data(days)
    else:
        start_date_time = datetime.datetime.fromisoformat(start_time)
        end_date_time = datetime.datetime.fromisoformat(end_time)
        extract_data = get_sub_service_hierarchy_data(start_time=start_date_time, end_time=end_date_time)
    return {'data': json.dumps(extract_data)}
