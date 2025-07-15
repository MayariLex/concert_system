/*
SQLyog Community v13.3.0 (64 bit)
MySQL - 8.1.0 : Database - concert_db
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`concert_db` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `concert_db`;

/*Table structure for table `categories` */

DROP TABLE IF EXISTS `categories`;

CREATE TABLE `categories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `concert_id` int DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `price` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `categories` */

insert  into `categories`(`id`,`concert_id`,`name`,`price`) values 
(1,2,'VVIP',22000.00),
(2,2,'VIP Seated',20000.00),
(3,2,'Gold',15000.00),
(4,2,'Silver',10000.00),
(5,2,'Bronze',9500.00),
(6,3,'VVIP',100.00),
(7,3,'VIP Seated',100.00),
(8,3,'Gold',100.00),
(9,3,'Silver',100.00),
(10,3,'Bronze',100.00);

/*Table structure for table `concerts` */

DROP TABLE IF EXISTS `concerts`;

CREATE TABLE `concerts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `artist` varchar(255) DEFAULT NULL,
  `date` date DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `layout` int DEFAULT NULL,
  `poster` varchar(255) DEFAULT NULL,
  `created_by` int DEFAULT NULL,
  `status` enum('upcoming','done') DEFAULT 'upcoming',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `concerts` */

insert  into `concerts`(`id`,`name`,`artist`,`date`,`location`,`layout`,`poster`,`created_by`,`status`) values 
(3,'Sariling Mundo','TJ Monterde','2025-12-25','Bulacan',3,'TJD3EventPoster.jpg',NULL,'done');

/*Table structure for table `notifications` */

DROP TABLE IF EXISTS `notifications`;

CREATE TABLE `notifications` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `concert_id` int DEFAULT NULL,
  `order_id` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `notifications` */

insert  into `notifications`(`id`,`user_id`,`concert_id`,`order_id`,`created_at`) values 
(1,4,3,1,'2025-07-15 19:54:29'),
(2,4,3,2,'2025-07-15 19:58:38'),
(3,4,3,3,'2025-07-15 20:00:27'),
(4,4,3,4,'2025-07-15 20:01:07'),
(5,4,3,5,'2025-07-15 20:02:40'),
(6,4,3,6,'2025-07-15 20:04:24'),
(7,4,3,7,'2025-07-15 20:06:50'),
(8,4,3,8,'2025-07-15 21:30:46'),
(9,4,3,9,'2025-07-15 21:32:04'),
(10,4,3,10,'2025-07-15 21:33:21'),
(11,4,3,11,'2025-07-15 21:35:20'),
(12,4,3,12,'2025-07-15 21:40:18');

/*Table structure for table `order_items` */

DROP TABLE IF EXISTS `order_items`;

CREATE TABLE `order_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int DEFAULT NULL,
  `seat_id` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `order_items` */

insert  into `order_items`(`id`,`order_id`,`seat_id`) values 
(1,1,16),
(2,2,17),
(3,2,18),
(4,2,21),
(5,3,1),
(6,3,6),
(7,3,11),
(8,3,19),
(9,3,22),
(10,4,23),
(11,5,12),
(12,6,7),
(13,7,8),
(14,8,4),
(15,9,3),
(16,10,5),
(17,11,2),
(18,11,9),
(19,12,10),
(20,12,14);

/*Table structure for table `orders` */

DROP TABLE IF EXISTS `orders`;

CREATE TABLE `orders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `concert_id` int DEFAULT NULL,
  `total_price` decimal(10,2) DEFAULT NULL,
  `timestamp` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `orders` */

insert  into `orders`(`id`,`user_id`,`concert_id`,`total_price`,`timestamp`) values 
(1,4,3,10000.00,'2025-07-15 19:54:29'),
(2,4,3,29500.00,'2025-07-15 19:58:38'),
(3,4,3,79500.00,'2025-07-15 20:00:27'),
(4,4,3,9500.00,'2025-07-15 20:01:07'),
(5,4,3,15000.00,'2025-07-15 20:02:40'),
(6,4,3,20000.00,'2025-07-15 20:04:24'),
(7,4,3,20000.00,'2025-07-15 20:06:50'),
(8,4,3,30000.00,'2025-07-15 21:30:46'),
(9,4,3,30000.00,'2025-07-15 21:32:04'),
(10,4,3,30000.00,'2025-07-15 21:33:21'),
(11,4,3,50000.00,'2025-07-15 21:35:20'),
(12,4,3,35000.00,'2025-07-15 21:40:18');

/*Table structure for table `seats` */

DROP TABLE IF EXISTS `seats`;

CREATE TABLE `seats` (
  `id` int NOT NULL AUTO_INCREMENT,
  `label` varchar(50) DEFAULT NULL,
  `category_id` int DEFAULT NULL,
  `concert_id` int DEFAULT NULL,
  `status` enum('available','sold') DEFAULT 'available',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `seats` */

insert  into `seats`(`id`,`label`,`category_id`,`concert_id`,`status`) values 
(1,'V1',6,3,'sold'),
(2,'V2',6,3,'sold'),
(3,'V3',6,3,'sold'),
(4,'V4',6,3,'sold'),
(5,'V5',6,3,'sold'),
(6,'V1',7,3,'sold'),
(7,'V2',7,3,'sold'),
(8,'V3',7,3,'sold'),
(9,'V4',7,3,'sold'),
(10,'V5',7,3,'sold'),
(11,'G1',8,3,'sold'),
(12,'G2',8,3,'sold'),
(13,'G3',8,3,'available'),
(14,'G4',8,3,'sold'),
(15,'G5',8,3,'available'),
(16,'S1',9,3,'sold'),
(17,'S2',9,3,'sold'),
(18,'S3',9,3,'sold'),
(19,'S4',9,3,'sold'),
(20,'S5',9,3,'available'),
(21,'B1',10,3,'sold'),
(22,'B2',10,3,'sold'),
(23,'B3',10,3,'sold'),
(24,'B4',10,3,'available'),
(25,'B5',10,3,'available');

/*Table structure for table `users` */

DROP TABLE IF EXISTS `users`;

CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `role` enum('admin','user') DEFAULT 'user',
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `users` */

insert  into `users`(`id`,`username`,`email`,`password_hash`,`role`) values 
(3,'Admin','q5jg4mbtsw@qacmjeq.com','scrypt:32768:8:1$JMbIaJ1fbT68drlW$e1a9d71ff3fa4a046b6794b2865ee5c8646bbc194f01b1598bbb5cf2942174a1a91c150f1494d86c20d5a14c85a95e31e7df265dd20ca2a1a4f07942c5c3ab2c','admin'),
(4,'User','hello.mayari19@gmail.com','scrypt:32768:8:1$bdfwXO20ZrVyTZO7$2a2a88ffef3b06390ad3e8926ca9b787f528536da13e3c90b7ca706280a833073e0c830c34bc024fc564c08069e672df3e053334f0c1a4911da5eead3eab59a5','user');

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
