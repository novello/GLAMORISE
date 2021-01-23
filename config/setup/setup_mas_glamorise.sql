-- MySQL dump 10.16  Distrib 10.1.26-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: db
-- ------------------------------------------------------
-- Server version	10.1.26-MariaDB-0+deb9u1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `NLIDB_FIELD_SYNONYMS`
--

DROP TABLE IF EXISTS `NLIDB_FIELD_SYNONYMS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `NLIDB_FIELD_SYNONYMS` (
  `SYNONYM` varchar(200) DEFAULT NULL,
  `FIELD` varchar(200) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `NLIDB_FIELD_SYNONYMS`
--

LOCK TABLES `NLIDB_FIELD_SYNONYMS` WRITE;
/*!40000 ALTER TABLE `NLIDB_FIELD_SYNONYMS` DISABLE KEYS */;
INSERT INTO `NLIDB_FIELD_SYNONYMS` VALUES ('author','author.name'),
('author', 'author.name'),
('author_name', 'author.name'),
('name_of_author', 'author.name'),
('researcher', 'author.name'),
('researcher_name', 'author.name'),
('name_of_researcher', 'author.name'),
('conference', 'conference.name'),
('conference_name', 'conference.name'),
('name_of_conference', 'conference.name'),
('citation', 'publication.citation_num'),
('publication_citation', 'publication.citation_num'),
('citation_of_publication', 'publication.citation_num'),
('paper', 'publication.title'),
('paper_title', 'publication.title'),
('title_of_paper', 'publication.title'),
('publication', 'publication.title'),
('publication_title', 'publication.title'),
('title_of_publication', 'publication.title'),
('journal', 'journal.name'),
('journal_name', 'journal.name'),
('name_of_journal', 'journal.name'),
('keyword', 'keyword.keyword'),
('year', 'publication.year'),
('publication_year', 'publication.year'),
('year_of_publication', 'publication.year'),
('organization', 'organization.name'),
('organization_name', 'organization.name'),
('name_of_organization', 'organization.name'),
('reference', 'publication.reference_num'),
('publication_reference', 'publication.reference_num'),
('reference_of_publication', 'publication.reference_num');
/*!40000 ALTER TABLE `NLIDB_FIELD_SYNONYMS` ENABLE KEYS */;
UNLOCK TABLES;
