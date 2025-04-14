DELIMITER //

DROP PROCEDURE IF EXISTS lacigal.GetSortedBookings;

CREATE PROCEDURE GetSortedBookings(IN days INT, IN start_time DATE, IN end_time DATE)
BEGIN
    IF days IS NOT NULL THEN
        SET start_time = DATE_SUB(NOW(), INTERVAL days DAY);
        SET end_time = NOW();
    END IF;

        SELECT
            bo.id,
            c.name AS `Client_Name`,
            DATE_FORMAT(bo.booking_date, '%Y-%m-%d %H:%i:%s') AS `Booking_Date`,
            CONCAT('Rs ', FORMAT(bo.total_price, 2)) AS `Total_Price`,
            CONCAT(CAST(ROUND(TIMESTAMPDIFF(SECOND, bo.booking_date, NOW()) / 3600, 2) AS DECIMAL(10,2)), ' hours') AS `TAT`
        FROM
            booking_bookingmodel bo
        JOIN
            booking_clientmodel c ON bo.client_id = c.id
        WHERE
            DATE(bo.booking_date) BETWEEN start_time AND end_time
            AND bo.booking_date < NOW()
            AND bo.arrival_time IS NULL
        ORDER BY
            Total_Price, `TAT` DESC;
END //

DELIMITER ;