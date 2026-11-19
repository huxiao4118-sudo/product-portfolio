-- MySQL 8.0.16+; schema only, 19 original/helper + 2 application tables.
-- Use a fresh database; this file contains no source rows or predictions.
CREATE DATABASE IF NOT EXISTS `olist_delivery_mysql` CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
USE `olist_delivery_mysql`;

CREATE TABLE `geolocation_raw` (
  `source_row_id` INT NOT NULL,
  `geolocation_zip_code_prefix` VARCHAR(5) NULL,
  `geolocation_lat` DOUBLE NULL,
  `geolocation_lng` DOUBLE NULL,
  `geolocation_city` VARCHAR(255) NULL,
  `geolocation_state` CHAR(2) NULL,
  CONSTRAINT `geolocation_raw_pkey` PRIMARY KEY (`source_row_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE `category_translation` (
  `product_category_name` VARCHAR(255) NOT NULL,
  `product_category_name_english` VARCHAR(255) NULL,
  CONSTRAINT `category_translation_pkey` PRIMARY KEY (`product_category_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE `mql_leads` (
  `mql_id` VARCHAR(32) NOT NULL,
  `first_contact_date` DATETIME(6) NULL,
  `landing_page_id` VARCHAR(32) NULL,
  `origin` VARCHAR(255) NULL,
  CONSTRAINT `mql_leads_pkey` PRIMARY KEY (`mql_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE `ibge_states` (
  `ibge_state_id` INT NOT NULL,
  `state_code` CHAR(2) NOT NULL,
  `state_name` VARCHAR(255) NOT NULL,
  `region_id` INT NOT NULL,
  `region_name` VARCHAR(255) NOT NULL,
  CONSTRAINT `ibge_states_pkey` PRIMARY KEY (`ibge_state_id`),
  CONSTRAINT `ibge_states_state_code_key` UNIQUE (`state_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE `seller_registry` (
  `seller_id` VARCHAR(32) NOT NULL,
  CONSTRAINT `seller_registry_pkey` PRIMARY KEY (`seller_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE `categories` (
  `product_category_name` VARCHAR(255) NOT NULL,
  CONSTRAINT `categories_pkey` PRIMARY KEY (`product_category_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE `zip_locations` (
  `zip_prefix` VARCHAR(5) NOT NULL,
  `lat` DOUBLE NULL,
  `lng` DOUBLE NULL,
  CONSTRAINT `zip_locations_pkey` PRIMARY KEY (`zip_prefix`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE `calendar_dates` (
  `calendar_date` DATE NOT NULL,
  `weekday` INT NULL,
  CONSTRAINT `calendar_dates_pkey` PRIMARY KEY (`calendar_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE `customers` (
  `customer_id` VARCHAR(32) NOT NULL,
  `customer_unique_id` VARCHAR(32) NULL,
  `customer_zip_code_prefix` VARCHAR(5) NULL,
  `customer_city` VARCHAR(255) NULL,
  `customer_state` CHAR(2) NOT NULL,
  CONSTRAINT `customers_pkey` PRIMARY KEY (`customer_id`),
  CONSTRAINT `fk_customers_ibge_state` FOREIGN KEY (`customer_state`) REFERENCES `ibge_states`(`state_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE `products` (
  `product_id` VARCHAR(32) NOT NULL,
  `product_category_name` VARCHAR(255) NULL,
  `product_name_lenght` DOUBLE NULL,
  `product_description_lenght` DOUBLE NULL,
  `product_photos_qty` DOUBLE NULL,
  `product_weight_g` DOUBLE NULL,
  `product_length_cm` DOUBLE NULL,
  `product_height_cm` DOUBLE NULL,
  `product_width_cm` DOUBLE NULL,
  CONSTRAINT `products_pkey` PRIMARY KEY (`product_id`),
  CONSTRAINT `products_product_category_name_fkey` FOREIGN KEY (`product_category_name`) REFERENCES `categories`(`product_category_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE `sellers` (
  `seller_id` VARCHAR(32) NOT NULL,
  `seller_zip_code_prefix` VARCHAR(5) NULL,
  `seller_city` VARCHAR(255) NULL,
  `seller_state` CHAR(2) NOT NULL,
  CONSTRAINT `sellers_pkey` PRIMARY KEY (`seller_id`),
  CONSTRAINT `fk_sellers_ibge_state` FOREIGN KEY (`seller_state`) REFERENCES `ibge_states`(`state_code`),
  CONSTRAINT `sellers_seller_id_fkey` FOREIGN KEY (`seller_id`) REFERENCES `seller_registry`(`seller_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE `closed_deals` (
  `mql_id` VARCHAR(32) NOT NULL,
  `seller_id` VARCHAR(32) NOT NULL,
  `sdr_id` VARCHAR(32) NULL,
  `sr_id` VARCHAR(32) NULL,
  `won_date` DATETIME(6) NULL,
  `business_segment` VARCHAR(255) NULL,
  `lead_type` VARCHAR(255) NULL,
  `lead_behaviour_profile` VARCHAR(255) NULL,
  `has_company` VARCHAR(255) NULL,
  `has_gtin` VARCHAR(255) NULL,
  `average_stock` VARCHAR(255) NULL,
  `business_type` VARCHAR(255) NULL,
  `declared_product_catalog_size` DOUBLE NULL,
  `declared_monthly_revenue` DOUBLE NULL,
  CONSTRAINT `closed_deals_pkey` PRIMARY KEY (`mql_id`),
  CONSTRAINT `uq_closed_deals_seller` UNIQUE (`seller_id`),
  CONSTRAINT `closed_deals_mql_id_fkey` FOREIGN KEY (`mql_id`) REFERENCES `mql_leads`(`mql_id`),
  CONSTRAINT `closed_deals_seller_id_fkey` FOREIGN KEY (`seller_id`) REFERENCES `seller_registry`(`seller_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE `holiday_events` (
  `calendar_date` DATE NOT NULL,
  `name` VARCHAR(255) NULL,
  `source` VARCHAR(255) NULL,
  `holiday_id` BIGINT NOT NULL AUTO_INCREMENT,
  CONSTRAINT `holiday_events_pkey` PRIMARY KEY (`holiday_id`),
  CONSTRAINT `holiday_events_calendar_date_fkey` FOREIGN KEY (`calendar_date`) REFERENCES `calendar_dates`(`calendar_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE `ibge_state_statistics` (
  `state_code` CHAR(2) NOT NULL,
  `reference_year` INT NOT NULL,
  `population_estimated` BIGINT NOT NULL,
  `gdp_thousand_brl` DOUBLE NOT NULL,
  `gdp_brl` DOUBLE NOT NULL,
  `gdp_per_resident_brl_derived` DOUBLE NOT NULL,
  `context_only` BOOLEAN NOT NULL DEFAULT 1,
  `retrieved_at_utc` DATETIME(6) NOT NULL,
  CONSTRAINT `ibge_state_statistics_pkey` PRIMARY KEY (`state_code`, `reference_year`),
  CONSTRAINT `ibge_state_statistics_state_code_fkey` FOREIGN KEY (`state_code`) REFERENCES `ibge_states`(`state_code`),
  CHECK (`population_estimated` > 0),
  CHECK (`gdp_thousand_brl` > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE `orders` (
  `order_id` VARCHAR(32) NOT NULL,
  `customer_id` VARCHAR(32) NOT NULL,
  `order_status` VARCHAR(255) NULL,
  `order_purchase_timestamp` DATETIME(6) NULL,
  `order_approved_at` DATETIME(6) NULL,
  `order_delivered_carrier_date` DATETIME(6) NULL,
  `order_delivered_customer_date` DATETIME(6) NULL,
  `order_estimated_delivery_date` DATETIME(6) NULL,
  CONSTRAINT `orders_pkey` PRIMARY KEY (`order_id`),
  CONSTRAINT `orders_customer_id_fkey` FOREIGN KEY (`customer_id`) REFERENCES `customers`(`customer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE `order_items` (
  `order_id` VARCHAR(32) NOT NULL,
  `order_item_id` INT NOT NULL,
  `product_id` VARCHAR(32) NOT NULL,
  `seller_id` VARCHAR(32) NOT NULL,
  `shipping_limit_date` DATETIME(6) NULL,
  `price` DOUBLE NULL,
  `freight_value` DOUBLE NULL,
  CONSTRAINT `order_items_pkey` PRIMARY KEY (`order_id`, `order_item_id`),
  CONSTRAINT `order_items_order_id_fkey` FOREIGN KEY (`order_id`) REFERENCES `orders`(`order_id`),
  CONSTRAINT `order_items_product_id_fkey` FOREIGN KEY (`product_id`) REFERENCES `products`(`product_id`),
  CONSTRAINT `order_items_seller_id_fkey` FOREIGN KEY (`seller_id`) REFERENCES `sellers`(`seller_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE `payments` (
  `order_id` VARCHAR(32) NOT NULL,
  `payment_sequential` INT NOT NULL,
  `payment_type` VARCHAR(255) NULL,
  `payment_installments` INT NULL,
  `payment_value` DOUBLE NULL,
  CONSTRAINT `payments_pkey` PRIMARY KEY (`order_id`, `payment_sequential`),
  CONSTRAINT `payments_order_id_fkey` FOREIGN KEY (`order_id`) REFERENCES `orders`(`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE `reviews` (
  `source_row_id` INT NOT NULL,
  `review_id` VARCHAR(32) NULL,
  `order_id` VARCHAR(32) NOT NULL,
  `review_score` INT NULL,
  `review_comment_title` TEXT NULL,
  `review_comment_message` TEXT NULL,
  `review_creation_date` DATETIME(6) NULL,
  `review_answer_timestamp` DATETIME(6) NULL,
  CONSTRAINT `reviews_pkey` PRIMARY KEY (`source_row_id`),
  CONSTRAINT `reviews_order_id_fkey` FOREIGN KEY (`order_id`) REFERENCES `orders`(`order_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE `order_calendar_anchor` (
  `order_id` VARCHAR(32) NOT NULL,
  `approved_date` DATE NULL,
  `promised_date` DATE NULL,
  CONSTRAINT `order_calendar_anchor_pkey` PRIMARY KEY (`order_id`),
  CONSTRAINT `order_calendar_anchor_approved_date_fkey` FOREIGN KEY (`approved_date`) REFERENCES `calendar_dates`(`calendar_date`),
  CONSTRAINT `order_calendar_anchor_order_id_fkey` FOREIGN KEY (`order_id`) REFERENCES `orders`(`order_id`),
  CONSTRAINT `order_calendar_anchor_promised_date_fkey` FOREIGN KEY (`promised_date`) REFERENCES `calendar_dates`(`calendar_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE IF NOT EXISTS predictions (
 order_id VARCHAR(32) NOT NULL,
 risk_probability DOUBLE NOT NULL,
 predicted_at DATETIME(6) NOT NULL,
 PRIMARY KEY (order_id),
 CONSTRAINT fk_predictions_order FOREIGN KEY (order_id) REFERENCES orders(order_id),
 CHECK (risk_probability BETWEEN 0 AND 1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE IF NOT EXISTS case_events (
 event_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
 order_id VARCHAR(32) NOT NULL,
 action_status VARCHAR(20) NOT NULL,
 note TEXT NOT NULL,
 recorded_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
 PRIMARY KEY (event_id),
 CONSTRAINT fk_case_events_order FOREIGN KEY (order_id) REFERENCES orders(order_id),
 CHECK (action_status IN ('Open','Investigating','Contacted','Resolved')),
 INDEX idx_case_events_order (order_id,event_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
