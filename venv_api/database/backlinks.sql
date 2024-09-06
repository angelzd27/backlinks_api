-- phpMyAdmin SQL Dump
-- version 4.9.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Sep 06, 2024 at 05:14 PM
-- Server version: 8.0.17
-- PHP Version: 7.3.10

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `backlinks`
--

DELIMITER $$
--
-- Procedures
--
CREATE DEFINER=`root`@`localhost` PROCEDURE `email_config` (IN `_id_config` INT, IN `_email` VARCHAR(255), IN `_password` VARCHAR(255))  NO SQL
BEGIN
	DECLARE emailId INT DEFAULT 0;
	DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
    	SELECT True AS error, "Unexpected error" AS msg;
    	ROLLBACK;
	END;
    
    START TRANSACTION;
    
    INSERT INTO `emails`(`email`, `password`) VALUES (_email, _password);
    SET emailId = LAST_INSERT_ID();
    
    INSERT INTO `config_emails`(`id_config`, `id_emails`) VALUES (_id_config, emailId);
    
    SELECT False AS error, "Operation executed" AS msg;
    
    COMMIT;
END$$

CREATE DEFINER=`root`@`localhost` PROCEDURE `user_register` (IN `_name` VARCHAR(100), IN `_last_name` VARCHAR(100), IN `_email` VARCHAR(255), IN `_password` VARCHAR(255), IN `_id_profile` INT)  NO SQL
BEGIN
	DECLARE configId INT DEFAULT 0;
	DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
    	SELECT True AS error, "Unexpected error" AS msg;
    	ROLLBACK;
	END;
    
    START TRANSACTION;
    
    INSERT INTO `config`(`pages_number`, `contact_number`, `author`, `email`, `url`, `comment`, `subject`, `message`) VALUES (10, 10, 'No author assigned', 'No email assigned', 'No url assigned', 'No comment assigned', 'No subject assigned', 'No message assigned');
    
    SET configId = LAST_INSERT_ID();
    
    INSERT INTO `users`(`name`, `last_name`, `email`, `password`, `id_profile`, `id_config`) VALUES (_name, _last_name, _email, _password, _id_profile, configId);
    
    SELECT False AS error, "Operation executed" AS msg;
    
    COMMIT;
END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `config`
--

CREATE TABLE `config` (
  `id` int(11) NOT NULL,
  `pages_number` int(11) NOT NULL,
  `contact_number` int(11) NOT NULL,
  `author` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `email` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `url` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `comment` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `subject` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `message` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `config`
--

INSERT INTO `config` (`id`, `pages_number`, `contact_number`, `author`, `email`, `url`, `comment`, `subject`, `message`) VALUES
(1, 20, 100, 'Okip', 'comunicacion@okip.com.mx', 'okip.com.mx', 'Holi Crayoli', 'Email subject', 'Message email'),
(2, 10, 10, 'No author assigned', 'No email assigned', 'No url assigned', 'No comment assigned', 'No subject assigned', 'No message assigned');

-- --------------------------------------------------------

--
-- Table structure for table `config_emails`
--

CREATE TABLE `config_emails` (
  `id_config` int(11) NOT NULL,
  `id_emails` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `config_emails`
--

INSERT INTO `config_emails` (`id_config`, `id_emails`) VALUES
(1, 1),
(1, 2);

-- --------------------------------------------------------

--
-- Table structure for table `contacts`
--

CREATE TABLE `contacts` (
  `id` int(11) NOT NULL,
  `url` varchar(500) COLLATE utf8mb4_general_ci NOT NULL,
  `emails` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `phones` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `company_name` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `emails`
--

CREATE TABLE `emails` (
  `id` int(11) NOT NULL,
  `email` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `password` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `status` tinyint(4) NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `emails`
--

INSERT INTO `emails` (`id`, `email`, `password`, `status`) VALUES
(1, 'l.zada010425@itses.edu.mx', 'Sistemas2022$', 1),
(2, 'angeltj27@gmail.com', 'Angel123!', 0);

-- --------------------------------------------------------

--
-- Table structure for table `profile`
--

CREATE TABLE `profile` (
  `id` int(11) NOT NULL,
  `profile` varchar(100) COLLATE utf8mb4_general_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `profile`
--

INSERT INTO `profile` (`id`, `profile`) VALUES
(1, 'admin'),
(2, 'user');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `name` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `last_name` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `email` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `password` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `id_profile` int(11) NOT NULL,
  `id_config` int(11) NOT NULL,
  `status` tinyint(4) NOT NULL DEFAULT '1',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `name`, `last_name`, `email`, `password`, `id_profile`, `id_config`, `status`, `created_at`) VALUES
(1, 'Angel Antonio', 'Zapatero Diaz', 'azapatero@okip.com.mx', 'pbkdf2:sha256:600000$SSC2cnMc1LYVsKdAIuQKfu4GRpCGzR$a1f4f2327f1d153fc9424cb59c997868f3503556785bd9f485786ef0a47f0c47', 1, 1, 1, '2024-07-25 09:48:40'),
(2, 'José Luis', 'Cruz Reyes', 'jlcruz@okip.com.mx', 'pbkdf2:sha256:600000$2u9vaKWqi2J2UlYmdTPThlZLhRJL45$a9a60aa4948591cc7e3afbf70da56e04495d591f57b43f883ec5544d14052e9a', 2, 2, 1, '2024-07-26 10:41:35');

-- --------------------------------------------------------

--
-- Table structure for table `website`
--

CREATE TABLE `website` (
  `id` int(11) NOT NULL,
  `url` varchar(500) COLLATE utf8mb4_general_ci NOT NULL,
  `status` tinyint(4) NOT NULL DEFAULT '0',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `website`
--

INSERT INTO `website` (`id`, `url`, `status`, `created_at`) VALUES
(1, 'https://kinsta.com/es/blog/comentarios-del-sitio-estatico/', 1, '2024-08-02 08:56:12'),
(2, 'https://elemprendesario.club/satisfaccion-del-cliente-al-alcance-de-un-escaneo-codigos-qr-en-accion/#respond', 1, '2024-08-02 09:01:33'),
(3, 'https://elemprendesario.club/buen-fin-y-las-compras-planificadas/#respond', 1, '2024-08-02 09:01:37'),
(4, 'https://elemprendesario.club/satisfaccion-del-cliente-al-alcance-de-un-escaneo-codigos-qr-en-accion/#respond', 1, '2024-08-02 09:02:02'),
(5, 'https://elemprendesario.club/buen-fin-y-las-compras-planificadas/#respond', 1, '2024-08-02 09:02:06'),
(6, 'https://elemprendesario.club/como-ser-una-empresa-customer-centric/', 1, '2024-08-02 09:02:18'),
(7, 'https://elemprendesario.club/que-es-una-encuesta-de-satisfaccion-de-cliente/#respond', 1, '2024-08-02 09:03:08'),
(8, 'https://elemprendesario.club/decalogodelservicioalcliente/', 1, '2024-08-02 09:03:19'),
(9, 'https://elemprendesario.club/panini-y-los-mundiales-de-futbol/', 1, '2024-08-02 09:03:25'),
(10, 'https://revistaseguridad360.com/', 1, '2024-08-02 09:03:54'),
(11, 'https://wordpress.com/es/blog/2024/06/26/recien-salidos-del-horno-nuevos-temas-para-wordpress-com-junio-2024/#comments', 1, '2024-08-02 09:21:20'),
(12, 'https://es-mx.wordpress.org/2024/07/18/wordpress-6-6-dorsey/#respond', 0, '2024-08-02 09:21:45'),
(13, 'https://es-mx.wordpress.org/2024/06/25/wordpress-6-5-5/#respond', 0, '2024-08-02 09:21:48'),
(14, 'https://www.hostinger.mx/tutoriales/que-es-wordpress', 1, '2024-08-02 09:22:36');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `config`
--
ALTER TABLE `config`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `config_emails`
--
ALTER TABLE `config_emails`
  ADD KEY `fk_config_email` (`id_config`),
  ADD KEY `fk_email_config` (`id_emails`);

--
-- Indexes for table `contacts`
--
ALTER TABLE `contacts`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `emails`
--
ALTER TABLE `emails`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `profile`
--
ALTER TABLE `profile`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD KEY `fk_profile_type_user` (`id_profile`),
  ADD KEY `fk_config_type_user` (`id_config`);

--
-- Indexes for table `website`
--
ALTER TABLE `website`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `config`
--
ALTER TABLE `config`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `contacts`
--
ALTER TABLE `contacts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `emails`
--
ALTER TABLE `emails`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `profile`
--
ALTER TABLE `profile`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `website`
--
ALTER TABLE `website`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `config_emails`
--
ALTER TABLE `config_emails`
  ADD CONSTRAINT `fk_config_email` FOREIGN KEY (`id_config`) REFERENCES `config` (`id`),
  ADD CONSTRAINT `fk_email_config` FOREIGN KEY (`id_emails`) REFERENCES `emails` (`id`);

--
-- Constraints for table `users`
--
ALTER TABLE `users`
  ADD CONSTRAINT `fk_config_type_user` FOREIGN KEY (`id_config`) REFERENCES `config` (`id`),
  ADD CONSTRAINT `fk_profile_type_user` FOREIGN KEY (`id_profile`) REFERENCES `profile` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
