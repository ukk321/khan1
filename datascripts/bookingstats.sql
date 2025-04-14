DELIMITER //

DROP PROCEDURE IF EXISTS lacigal.GetBookingStats;

CREATE PROCEDURE GetBookingStats(IN days INT, IN start_date DATE, IN end_date DATE)
BEGIN
    -- Declare variables
    DECLARE total_amount DECIMAL(10, 2);
    DECLARE total_advance_payments DECIMAL(10, 2);
    DECLARE total_pending_amount DECIMAL(10, 2);

    -- If 'days' is provided, override start_date and end_date
    IF days IS NOT NULL THEN
        SET start_date = DATE_SUB(NOW(), INTERVAL days DAY);
        SET end_date = NOW();
    END IF;

    -- Calculate total amount from bookings
    SELECT SUM(total_price) INTO total_amount
    FROM booking_bookingmodel
    WHERE DATE(booking_date) BETWEEN start_date AND end_date;

    -- Calculate total advance payments
    SELECT SUM(payment_amount) INTO total_advance_payments
    FROM booking_paymentmodel
    WHERE payment_status = 'ADVANCE PAID'
    AND booking_id IN (SELECT id FROM booking_bookingmodel WHERE DATE(booking_date) BETWEEN start_date AND end_date);

    -- Calculate total pending amount
    SET total_pending_amount = total_amount - total_advance_payments;

    -- Return results
    SELECT total_amount AS Total_Booking_Amount,
           total_advance_payments AS Total_Advance_Payments,
           total_pending_amount AS Total_Pending_Amount;
END //

DELIMITER ;
