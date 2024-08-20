-- MySQL dump 10.13  Distrib 8.0.39, for Linux (x86_64)
--
-- Host: localhost    Database: Discord
-- ------------------------------------------------------
-- Server version	8.0.39-0ubuntu0.20.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `comment_points`
--

DROP TABLE IF EXISTS `comment_points`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `comment_points` (
  `seq` int NOT NULL AUTO_INCREMENT,
  `uid` bigint NOT NULL,
  `times` int NOT NULL DEFAULT '2',
  `next_reward` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`seq`),
  KEY `uid` (`uid`),
  CONSTRAINT `comment_points_ibfk_1` FOREIGN KEY (`uid`) REFERENCES `user` (`uid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=137 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ctf_data`
--

DROP TABLE IF EXISTS `ctf_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ctf_data` (
  `id` bigint NOT NULL,
  `flags` varchar(255) DEFAULT NULL,
  `score` int DEFAULT NULL,
  `restrictions` varchar(255) DEFAULT NULL,
  `message_id` bigint DEFAULT NULL,
  `case_status` tinyint(1) DEFAULT NULL,
  `start_time` datetime DEFAULT NULL,
  `end_time` varchar(255) DEFAULT NULL,
  `title` varchar(255) DEFAULT NULL,
  `tried` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ctf_history`
--

DROP TABLE IF EXISTS `ctf_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ctf_history` (
  `data_id` bigint DEFAULT NULL,
  `uid` bigint DEFAULT NULL,
  `count` int DEFAULT NULL,
  `solved` tinyint(1) NOT NULL DEFAULT '0',
  KEY `data_id` (`data_id`),
  CONSTRAINT `history_ibfk_1` FOREIGN KEY (`data_id`) REFERENCES `ctf_data` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `game`
--

DROP TABLE IF EXISTS `game`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `game` (
  `seq` bigint NOT NULL DEFAULT '0',
  `lastID` bigint DEFAULT '0',
  `niceColor` varchar(3) NOT NULL DEFAULT 'FFF',
  `nicecolorround` int DEFAULT NULL,
  `niceColorCount` bigint DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gift`
--

DROP TABLE IF EXISTS `gift`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gift` (
  `btnID` bigint NOT NULL,
  `type` enum('電電點','抽獎券') DEFAULT NULL,
  `count` int DEFAULT NULL,
  `recipient` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`btnID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `DCname` varchar(32) DEFAULT NULL,
  `uid` bigint NOT NULL,
  `DCMail` varchar(320) DEFAULT NULL,
  `githubName` varchar(39) DEFAULT NULL,
  `githubMail` varchar(320) DEFAULT NULL,
  `loveuwu` tinyint(1) NOT NULL DEFAULT '0',
  `point` int NOT NULL DEFAULT '0',
  `ticket` int NOT NULL DEFAULT '1',
  `charge_combo` int NOT NULL DEFAULT '0',
  `next_lottery` int NOT NULL DEFAULT '0',
  `last_charge` datetime NOT NULL DEFAULT '1970-01-01 00:00:00',
  `last_comment` date NOT NULL DEFAULT '1970-01-01',
  `today_comments` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-08-20 10:22:41
