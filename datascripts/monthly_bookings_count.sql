DELIMITER //

DROP PROCEDURE IF EXISTS lacigal.GetMonthlyBookingCounts;

CREATE PROCEDURE GetMonthlyBookingCounts(IN days INT, IN start_date DATE, IN end_date DATE)
BEGIN

    IF days IS NOT NULL THEN
        SET start_date = DATE_SUB(NOW(), INTERVAL days DAY);
        SET end_date = NOW();
    END IF;

    SELECT
        MONTH(booking_date) AS month,
        COUNT(*) AS booking_count
    FROM
        booking_bookingmodel
    WHERE
        DATE(booking_date) BETWEEN DATE(start_date) AND DATE(end_date)
    GROUP BY
        month
    ORDER BY
        month;
END //

DELIMITER ;