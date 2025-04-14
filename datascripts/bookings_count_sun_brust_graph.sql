DELIMITER //

DROP PROCEDURE IF EXISTS lacigal.GetBookingStatistics;

CREATE PROCEDURE GetBookingStatistics(IN days INT, IN start_time DATE, IN end_time DATE)

BEGIN
    IF days IS NOT NULL THEN
        SET start_time = DATE_SUB(NOW(), INTERVAL days DAY);
        SET end_time = NOW();
    END IF;
SELECT
    serviceName,
    COUNT(serviceName) AS NoOfBookingsInServices,
    catName,
    COUNT(catName) AS NoOfBookingsInCategories,
    subServiceName,
    COUNT(subServiceName) AS NoOfBookingsInSubServices,
    dealName,
    COUNT(dealName) AS NoOfBookingsInDeals
FROM (
    SELECT
        COALESCE(JSON_UNQUOTE(JSON_EXTRACT(services.value, '$.name')), '') AS serviceName,
        COALESCE(JSON_UNQUOTE(JSON_EXTRACT(categories.value, '$.name')), '') AS catName,
        COALESCE(JSON_UNQUOTE(JSON_EXTRACT(sub_services.value, '$.name')), '') AS subServiceName,
        '' AS dealName
    FROM
        booking_bookingmodel,
        JSON_TABLE(selected_items, '$.services[*]'
            COLUMNS (
                value JSON PATH '$'
            )
        ) AS services
        LEFT JOIN JSON_TABLE(services.value, '$.categories[*]'
            COLUMNS (
                value JSON PATH '$'
            )
        ) AS categories ON TRUE
        LEFT JOIN JSON_TABLE(categories.value, '$.sub_services[*]'
            COLUMNS (
                value JSON PATH '$'
            )
        ) AS sub_services ON TRUE
    WHERE DATE(booking_bookingmodel.created_at) BETWEEN start_time AND end_time
    UNION ALL
    SELECT
        '' AS serviceName,
        '' AS catName,
        '' AS subServiceName,
        COALESCE(JSON_UNQUOTE(JSON_EXTRACT(deals.value, '$.name')), '') AS dealName
    FROM
        booking_bookingmodel,
        JSON_TABLE(selected_items, '$.deals[*]'
            COLUMNS (
                value JSON PATH '$'
            )
        ) AS deals
        WHERE DATE(booking_bookingmodel.created_at) BETWEEN start_time AND end_time
) AS combined
GROUP BY serviceName, catName, subServiceName, dealName
HAVING
    serviceName IS NOT NULL AND TRIM(serviceName) <> ''
    OR catName IS NOT NULL AND TRIM(catName) <> ''
    OR subServiceName IS NOT NULL AND TRIM(subServiceName) <> ''
    OR dealName IS NOT NULL AND TRIM(dealName) <> ''
ORDER BY serviceName;

END //

DELIMITER ;