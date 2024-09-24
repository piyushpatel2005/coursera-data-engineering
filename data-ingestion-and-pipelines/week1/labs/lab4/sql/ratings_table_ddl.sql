DROP TABLE IF EXISTS ratings_training;

CREATE TABLE ratings_training (
  city varchar(50) NOT NULL,
  state varchar(50) DEFAULT NULL,
  postalCode varchar(15) DEFAULT NULL,
  country varchar(50) NOT NULL,
  creditLimit decimal(10,2) DEFAULT NULL,
  productCode varchar(15) NOT NULL,
  productLine varchar(50) NOT NULL,
  productScale varchar(10) NOT NULL,
  quantityInStock smallint NOT NULL,
  buyPrice decimal(10,2) NOT NULL,
  MSRP decimal(10,2) NOT NULL,
  productRating smallint NOT NULL,  
  customerNumber int NOT NULL,      
  PRIMARY KEY (customerNumber, productCode)
);
