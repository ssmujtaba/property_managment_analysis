CREATE TABLE IF NOT EXISTS `dim_date` (
  `date_id` INT NOT NULL,
  `date` DATE NOT NULL,
  `year` INT NOT NULL,
  `quarter` INT NOT NULL,
  `month` INT NOT NULL,
  `day` INT NOT NULL,
  `weekday` INT NOT NULL, -- 0 for Monday, 6 for Sunday
  PRIMARY KEY (`date_id`),
  UNIQUE INDEX `uq_date` (`date` ASC) VISIBLE
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `jnj_solutions_db`.`dim_owner`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `dim_owner` (
  `owner_id` INT NOT NULL,
  `owner_name` VARCHAR(255) NOT NULL,
  `owner_email` VARCHAR(255) NULL,
  `owner_phone` VARCHAR(50) NULL,
  `owner_category` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`owner_id`),
  UNIQUE INDEX `uq_owner_email` (`owner_email` ASC) VISIBLE
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `jnj_solutions_db`.`dim_platform`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `dim_platform` (
  `platform_id` INT NOT NULL,
  `platform_name` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`platform_id`),
  UNIQUE INDEX `uq_platform_name` (`platform_name` ASC) VISIBLE
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `jnj_solutions_db`.`dim_tenant`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `dim_tenant` (
  `tenant_id` INT NOT NULL,
  `tenant_name` VARCHAR(255) NOT NULL,
  `tenant_email` VARCHAR(255) NULL,
  `tenant_phone` VARCHAR(50) NULL,
  PRIMARY KEY (`tenant_id`),
  UNIQUE INDEX `uq_tenant_email` (`tenant_email` ASC) VISIBLE
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `jnj_solutions_db`.`dim_property`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `dim_property` (
  `property_id` INT NOT NULL,
  `owner_id` INT NOT NULL,
  `property_type` VARCHAR(100) NOT NULL,
  `country` VARCHAR(100) NOT NULL,
  `city` VARCHAR(100) NOT NULL,
  `distance_to_city_center` DECIMAL(5,2) NULL,
  `amenities` TEXT NULL, -- Storing as comma-separated string
  `base_price` DECIMAL(10,2) NOT NULL,
  PRIMARY KEY (`property_id`),
  INDEX `fk_property_owner_idx` (`owner_id` ASC) VISIBLE,
  CONSTRAINT `fk_property_owner`
    FOREIGN KEY (`owner_id`)
    REFERENCES `dim_owner` (`owner_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `jnj_solutions_db`.`fact_bookings`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `fact_bookings` (
  `booking_id` INT NOT NULL,
  `property_id` INT NOT NULL,
  `platform_id` INT NOT NULL,
  `tenant_id` INT NOT NULL,
  `check_in_date_id` INT NOT NULL, -- Foreign key to dim_date
  `check_out_date_id` INT NOT NULL, -- Foreign key to dim_date
  `check_in` DATE NOT NULL,
  `check_out` DATE NOT NULL,
  `nights` INT NOT NULL,
  `revenue` DECIMAL(12,2) NOT NULL,
  `purpose_of_stay` VARCHAR(255) NULL,
  `damage_flag` TINYINT NOT NULL, -- 0 for no damage, 1 for damage
  `damage_cost` DECIMAL(10,2) NULL,
  `turnover_flag` TINYINT NOT NULL, -- 0 for no turnover, 1 for turnover (cleaning needed)
  PRIMARY KEY (`booking_id`),
  INDEX `fk_bookings_property_idx` (`property_id` ASC) VISIBLE,
  INDEX `fk_bookings_platform_idx` (`platform_id` ASC) VISIBLE,
  INDEX `fk_bookings_tenant_idx` (`tenant_id` ASC) VISIBLE,
  INDEX `fk_bookings_check_in_date_idx` (`check_in_date_id` ASC) VISIBLE,
  INDEX `fk_bookings_check_out_date_idx` (`check_out_date_id` ASC) VISIBLE,
  CONSTRAINT `fk_bookings_property`
    FOREIGN KEY (`property_id`)
    REFERENCES `dim_property` (`property_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_bookings_platform`
    FOREIGN KEY (`platform_id`)
    REFERENCES `dim_platform` (`platform_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_bookings_tenant`
    FOREIGN KEY (`tenant_id`)
    REFERENCES `dim_tenant` (`tenant_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_bookings_check_in_date`
    FOREIGN KEY (`check_in_date_id`)
    REFERENCES `dim_date` (`date_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_bookings_check_out_date`
    FOREIGN KEY (`check_out_date_id`)
    REFERENCES `dim_date` (`date_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `jnj_solutions_db`.`fact_reviews`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `fact_reviews` (
  `review_id` INT NOT NULL,
  `booking_id` INT NULL, -- Can be NULL if review is not tied to a specific booking, but for this dataset, it will be linked
  `tenant_id` INT NOT NULL,
  `property_id` INT NOT NULL,
  `review_date_id` INT NOT NULL, -- Foreign key to dim_date
  `rating` INT NOT NULL, -- 1-5 star rating
  `review_text` TEXT NULL,
  `review_date` DATE NOT NULL,
  PRIMARY KEY (`review_id`),
  INDEX `fk_reviews_booking_idx` (`booking_id` ASC) VISIBLE,
  INDEX `fk_reviews_tenant_idx` (`tenant_id` ASC) VISIBLE,
  INDEX `fk_reviews_property_idx` (`property_id` ASC) VISIBLE,
  INDEX `fk_reviews_review_date_idx` (`review_date_id` ASC) VISIBLE,
  CONSTRAINT `fk_reviews_booking`
    FOREIGN KEY (`booking_id`)
    REFERENCES `fact_bookings` (`booking_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_reviews_tenant`
    FOREIGN KEY (`tenant_id`)
    REFERENCES `dim_tenant` (`tenant_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_reviews_property`
    FOREIGN KEY (`property_id`)
    REFERENCES `dim_property` (`property_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_reviews_review_date`
    FOREIGN KEY (`review_date_id`)
    REFERENCES `dim_date` (`date_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
) ENGINE = InnoDB;

-- Inserting Data

LOAD DATA INFILE 'C:\\Users\\Eier\\Desktop\\Portfolio of a data analyst\\SQL Databases\\dim_date.csv'
INTO TABLE dim_date
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA INFILE 'C:\\Users\\Eier\\Desktop\\Portfolio of a data analyst\\SQL Databases\\dim_owner.csv'
INTO TABLE dim_owner
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA INFILE 'C:\\Users\\Eier\\Desktop\\Portfolio of a data analyst\\SQL Databases\\dim_platform.csv'
INTO TABLE dim_platform
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA INFILE 'C:\\Users\\Eier\\Desktop\\Portfolio of a data analyst\\SQL Databases\\dim_tenant.csv'
INTO TABLE dim_tenant
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA INFILE 'C:\\Users\\Eier\\Desktop\\Portfolio of a data analyst\\SQL Databases\\dim_property.csv'
INTO TABLE dim_property
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA INFILE 'C:\\Users\\Eier\\Desktop\\Portfolio of a data analyst\\SQL Databases\\fact_bookings.csv'
INTO TABLE fact_bookings
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA INFILE 'C:\\Users\\Eier\\Desktop\\Portfolio of a data analyst\\SQL Databases\\fact_bookings.csv'
INTO TABLE fact_bookings
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA INFILE 'C:\\Users\\Eier\\Desktop\\Portfolio of a data analyst\\SQL Databases\\fact_reviews.csv'
INTO TABLE fact_reviews
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

select count(property_id) as 'Total Counts', property_type, owner_name
from
dim_property p
join dim_owner o on o.owner_id = p.owner_id
where property_id = 100
group by property_id, property_type, owner_name;

select count(property_type) as 'Total Resort Counts', country as 'Country'
from
dim_property
where property_type = 'Resort'
group by country;

select distinct owner_name, property_type, country
from
dim_owner o
join dim_property p on p.owner_id = o.owner_id
where property_type = 'Resort'
order by owner_name;

select property_type, city, country, owner_name
from
dim_property p
join dim_owner o on o.owner_id = p.owner_id
where property_type = 'Resort'
order by city;

-- revenue by property type, dim propert, fact bookings
select property_type, sum(revenue)
from
dim_property p
join fact_bookings f on f.property_id = p.property_id
where property_type = 'Resort'
group by property_type;

SELECT
    dp.property_type,
    SUM(fb.revenue) AS 'Total Resort Revenue', dp.country
FROM
    dim_property dp
JOIN
    fact_bookings fb ON dp.property_id = fb.property_id
JOIN
    dim_date dd ON fb.check_in_date_id = dd.date_id -- Join with dim_date using check_in_date_id
WHERE
    dp.property_type = 'Resort' AND dd.year = 2020 -- Add the year filter here
GROUP BY
    dp.property_type, dp.country;