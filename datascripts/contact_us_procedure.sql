DELIMITER //

DROP PROCEDURE IF EXISTS lacigal.GetSortedContactUs;

CREATE PROCEDURE GetSortedContactUs(IN days INT, IN start_time DATE, IN end_time DATE)
BEGIN
    IF days IS NOT NULL THEN
        SET start_time = DATE_SUB(NOW(), INTERVAL days DAY);
        SET end_time = NOW();
    END IF;
    SELECT cu.id,
           cu.name,
           cu.email,
           cu.message,
           CONCAT(CAST(ROUND(TIMESTAMPDIFF(SECOND, cu.created_at, NOW()) / 3600, 2) AS DECIMAL(10, 2)),
                  ' hours')                                                                    AS TAT,
           IF(EXISTS (SELECT 1 FROM services_reply r WHERE r.contact_id = cu.id), TRUE, FALSE) AS is_replied
    FROM services_contactus cu
    WHERE DATE(cu.created_at) BETWEEN start_time AND end_time

    ORDER BY is_replied, TAT DESC;
END //

DELIMITER ;
