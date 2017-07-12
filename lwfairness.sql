-- MySQL dump 10.13  Distrib 5.7.18, for macos10.12 (x86_64)
--
-- Host: localhost    Database: proj1
-- ------------------------------------------------------
-- Server version	5.7.18

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `average`
--

DROP TABLE IF EXISTS `average`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `average` (
  `resource_id` int(11) DEFAULT NULL,
  `q_id` int(11) DEFAULT NULL,
  `avg` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `average`
--

LOCK TABLES `average` WRITE;
/*!40000 ALTER TABLE `average` DISABLE KEYS */;
INSERT INTO `average` VALUES (2,1,0.333333333333),(2,2,0),(2,3,0),(2,4,0.333333333333),(2,5,0.333333333333),(2,6,-0.333333333333),(2,7,0.333333333333),(2,8,0.333333333333),(2,9,0.333333333333),(2,10,0.333333333333),(2,11,-0.333333333333),(2,12,0.333333333333),(2,13,0.333333333333),(2,14,0),(2,15,0.333333333333),(2,16,0.333333333333),(4,1,1),(4,2,1),(4,3,-1),(4,4,1),(4,5,1),(4,6,1),(4,7,1),(4,8,1),(4,9,0),(4,10,1),(4,11,1),(4,12,1),(4,13,1),(4,14,-1),(4,15,-1),(4,16,-1),(5,1,0.4),(5,2,0),(5,3,0.8),(5,4,0),(5,5,-0.4),(5,6,0.6),(5,7,0.4),(5,8,0.2),(5,9,0.6),(5,10,0.6),(5,11,-0.2),(5,12,-0.4),(5,13,-0.2),(5,14,-0.2),(5,15,-0.8),(5,16,-0.6),(6,1,-1),(6,2,0),(6,3,1),(6,4,-1),(6,5,0),(6,6,1),(6,7,0),(6,8,0),(6,9,0),(6,10,1),(6,11,0),(6,12,1),(6,13,1),(6,14,1),(6,15,1),(6,16,0),(7,1,0.5),(7,2,0.5),(7,3,-0.5),(7,4,-0.5),(7,5,-0.5),(7,6,-0.5),(7,7,-0.5),(7,8,-0.5),(7,9,0.5),(7,10,0),(7,11,0),(7,12,0.5),(7,13,0.5),(7,14,0.5),(7,15,0),(7,16,0.5),(8,1,0.5),(8,2,-0.5),(8,3,-0.5),(8,4,0.5),(8,5,0.5),(8,6,0.5),(8,7,-0.5),(8,8,-0.5),(8,9,0.5),(8,10,0.5),(8,11,0.5),(8,12,0.5),(8,13,-0.5),(8,14,0.5),(8,15,0.5),(8,16,0.5),(1,1,1),(1,2,0),(1,3,1),(1,4,1),(1,5,1),(1,6,0),(1,7,1),(1,8,1),(1,9,1),(1,10,0),(1,11,1),(1,12,1),(1,13,1),(1,14,1),(1,15,0),(1,16,1),(3,1,0),(3,2,-0.25),(3,3,0.25),(3,4,-0.25),(3,5,0.25),(3,6,-0.25),(3,7,-0.25),(3,8,0.25),(3,9,-0.5),(3,10,0.5),(3,11,0.25),(3,12,-0.25),(3,13,0.25),(3,14,0.25),(3,15,0.25),(3,16,0.25);
/*!40000 ALTER TABLE `average` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `evaluation`
--

DROP TABLE IF EXISTS `evaluation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `evaluation` (
  `user_id` int(11) DEFAULT NULL,
  `resource_id` int(11) DEFAULT NULL,
  `q_id` int(11) DEFAULT NULL,
  `answer` text,
  `comment` text
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `evaluation`
--

LOCK TABLES `evaluation` WRITE;
/*!40000 ALTER TABLE `evaluation` DISABLE KEYS */;
INSERT INTO `evaluation` VALUES (8,5,1,'no',NULL),(8,5,2,'no',NULL),(8,5,3,'yes',NULL),(8,5,4,'no',NULL),(8,5,5,'no',NULL),(8,5,6,'yes',NULL),(8,5,7,'no',NULL),(8,5,8,'no',NULL),(8,5,9,'yes',NULL),(8,5,10,'no',NULL),(8,5,11,'no',NULL),(8,5,12,'yes',NULL),(8,5,13,'no',NULL),(8,5,14,'yes',NULL),(8,5,15,'no',NULL),(8,5,16,'no',NULL),(10,5,1,'yesbut','o'),(10,5,2,'yesbut','k'),(10,5,3,'yes',NULL),(10,5,4,'yesbut','h'),(10,5,5,'yesbut','g'),(10,5,6,'yesbut','f'),(10,5,7,'yesbut','d'),(10,5,8,'yes',NULL),(10,5,9,'yes',NULL),(10,5,10,'yes',NULL),(10,5,11,'yes',NULL),(10,5,12,'no',NULL),(10,5,13,'yes',NULL),(10,5,14,'no',NULL),(10,5,15,'no',NULL),(10,5,16,'no',NULL),(17,5,1,'yes',NULL),(17,5,2,'yes',NULL),(17,5,3,'yes',NULL),(17,5,4,'yes',NULL),(17,5,5,'yes',NULL),(17,5,6,'yes',NULL),(17,5,7,'yes',NULL),(17,5,8,'yes',NULL),(17,5,9,'yes',NULL),(17,5,10,'yes',NULL),(17,5,11,'yes',NULL),(17,5,12,'no',NULL),(17,5,13,'no',NULL),(17,5,14,'no',NULL),(17,5,15,'no',NULL),(17,5,16,'no',NULL),(21,1,1,'yes',NULL),(21,1,2,'yes',NULL),(21,1,3,'yes',NULL),(21,1,4,'yes',NULL),(21,1,5,'yes',NULL),(21,1,6,'yes',NULL),(21,1,7,'yes',NULL),(21,1,8,'yes',NULL),(21,1,9,'yes',NULL),(21,1,10,'yes',NULL),(21,1,11,'yes',NULL),(21,1,12,'yes',NULL),(21,1,13,'yes',NULL),(21,1,14,'yes',NULL),(21,1,15,'yes',NULL),(21,1,16,'yes',NULL),(21,2,1,'no',NULL),(21,2,2,'no',NULL),(21,2,3,'no',NULL),(21,2,4,'no',NULL),(21,2,5,'no',NULL),(21,2,6,'no',NULL),(21,2,7,'no',NULL),(21,2,8,'no',NULL),(21,2,9,'no',NULL),(21,2,10,'no',NULL),(21,2,11,'no',NULL),(21,2,12,'no',NULL),(21,2,13,'no',NULL),(21,2,14,'no',NULL),(21,2,15,'no',NULL),(21,2,16,'no',NULL),(21,3,1,'yesbut','2'),(21,3,2,'yesbut','2'),(21,3,3,'yesbut','2'),(21,3,4,'yesbut','2'),(21,3,5,'yesbut','2'),(21,3,6,'yesbut','2'),(21,3,7,'yesbut','2'),(21,3,8,'yesbut','2'),(21,3,9,'yesbut','2'),(21,3,10,'yesbut','2'),(21,3,11,'yesbut','2'),(21,3,12,'yesbut','2'),(21,3,13,'yesbut','2'),(21,3,14,'yesbut','2'),(21,3,15,'yesbut','2'),(21,3,16,'yesbut','2'),(21,4,1,'yes',NULL),(21,4,2,'yes',NULL),(21,4,3,'no',NULL),(21,4,4,'yes',NULL),(21,4,5,'yes',NULL),(21,4,6,'yes',NULL),(21,4,7,'yes',NULL),(21,4,8,'yes',NULL),(21,4,9,'yesbut','sldf'),(21,4,10,'yes',NULL),(21,4,11,'yes',NULL),(21,4,12,'yes',NULL),(21,4,13,'yes',NULL),(21,4,14,'no',NULL),(21,4,15,'no',NULL),(21,4,16,'no',NULL),(21,5,1,'yes',NULL),(21,5,2,'no',NULL),(21,5,3,'yesbut','a'),(21,5,4,'yes',NULL),(21,5,5,'no',NULL),(21,5,6,'yesbut','e'),(21,5,7,'yes',NULL),(21,5,8,'no',NULL),(21,5,9,'yesbut','i'),(21,5,10,'yes',NULL),(21,5,11,'no',NULL),(21,5,12,'yesbut','o'),(21,5,13,'yes',NULL),(21,5,14,'no',NULL),(21,5,15,'yesbut','u'),(21,5,16,'yes',NULL),(21,6,1,'no',NULL),(21,6,2,'yesbut','e'),(21,6,3,'yes',NULL),(21,6,4,'no',NULL),(21,6,5,'yesbut','o'),(21,6,6,'yes',NULL),(21,6,7,'yesbut','owe'),(21,6,8,'yesbut','a'),(21,6,9,'yesbut','q'),(21,6,10,'yes',NULL),(21,6,11,'yesbut','sd'),(21,6,12,'yes',NULL),(21,6,13,'yes',NULL),(21,6,14,'yes',NULL),(21,6,15,'yes',NULL),(21,6,16,'yesbut','pdf'),(21,7,1,'yesbut','a1'),(21,7,2,'yesbut','a1'),(21,7,3,'yesbut','a1'),(21,7,4,'yesbut','a1'),(21,7,5,'yesbut','a1'),(21,7,6,'yesbut','a1'),(21,7,7,'yesbut','a1'),(21,7,8,'yesbut','a1'),(21,7,9,'yesbut','v'),(21,7,10,'yesbut','a1'),(21,7,11,'yesbut','a1'),(21,7,12,'yesbut','a1'),(21,7,13,'yesbut','a1'),(21,7,14,'yesbut','v'),(21,7,15,'yesbut','a1'),(21,7,16,'yesbut','a1'),(21,8,1,'yesbut','a'),(21,8,2,'yesbut','a'),(21,8,3,'yesbut','a'),(21,8,4,'yesbut','a'),(21,8,5,'yesbut','a'),(21,8,6,'yesbut','a'),(21,8,7,'yesbut','a'),(21,8,8,'yesbut','a'),(21,8,9,'yesbut','a'),(21,8,10,'yesbut','a'),(21,8,11,'yesbut','a'),(21,8,12,'yesbut','a'),(21,8,13,'yesbut','a'),(21,8,14,'yesbut','a'),(21,8,15,'yesbut','a'),(21,8,16,'yesbut','a'),(22,3,1,'no',NULL),(22,3,2,'no',NULL),(22,3,3,'yes',NULL),(22,3,4,'no',NULL),(22,3,5,'yes',NULL),(22,3,6,'no',NULL),(22,3,7,'no',NULL),(22,3,8,'yes',NULL),(22,3,9,'no',NULL),(22,3,10,'yesbut','whoo'),(22,3,11,'yes',NULL),(22,3,12,'no',NULL),(22,3,13,'yes',NULL),(22,3,14,'yes',NULL),(22,3,15,'yes',NULL),(22,3,16,'yes',NULL),(22,2,1,'yes',NULL),(22,2,2,'yes',NULL),(22,2,3,'yes',NULL),(22,2,4,'yes',NULL),(22,2,5,'yes',NULL),(22,2,6,'no',NULL),(22,2,7,'yes',NULL),(22,2,8,'yes',NULL),(22,2,9,'yes',NULL),(22,2,10,'yes',NULL),(22,2,11,'no',NULL),(22,2,12,'yes',NULL),(22,2,13,'yes',NULL),(22,2,14,'yes',NULL),(22,2,15,'yes',NULL),(22,2,16,'yes',NULL),(22,8,1,'yes',NULL),(22,8,2,'no',NULL),(22,8,3,'no',NULL),(22,8,4,'yes',NULL),(22,8,5,'yes',NULL),(22,8,6,'yes',NULL),(22,8,7,'no',NULL),(22,8,8,'no',NULL),(22,8,9,'yes',NULL),(22,8,10,'yes',NULL),(22,8,11,'yes',NULL),(22,8,12,'yes',NULL),(22,8,13,'no',NULL),(22,8,14,'yes',NULL),(22,8,15,'yes',NULL),(22,8,16,'yes',NULL),(22,7,1,'yes',NULL),(22,7,2,'yes',NULL),(22,7,3,'no',NULL),(22,7,4,'no',NULL),(22,7,5,'no',NULL),(22,7,6,'no',NULL),(22,7,7,'no',NULL),(22,7,8,'no',NULL),(22,7,9,'yes',NULL),(22,7,10,'yesbut','bye'),(22,7,11,'yesbut','sd'),(22,7,12,'yes',NULL),(22,7,13,'yes',NULL),(22,7,14,'yes',NULL),(22,7,15,'yesbut','but'),(22,7,16,'yes',NULL),(22,5,1,'yes',NULL),(22,5,2,'yes',NULL),(22,5,3,'yes',NULL),(22,5,4,'no',NULL),(22,5,5,'no',NULL),(22,5,6,'yes',NULL),(22,5,7,'yes',NULL),(22,5,8,'yes',NULL),(22,5,9,'yesbut','okokokok'),(22,5,10,'yes',NULL),(22,5,11,'no',NULL),(22,5,12,'no',NULL),(22,5,13,'no',NULL),(22,5,14,'yes',NULL),(22,5,15,'no',NULL),(22,5,16,'no',NULL),(9,2,1,'yes',NULL),(9,2,2,'yesbut','hit'),(9,2,3,'yesbut','hello'),(9,2,4,'yes',NULL),(9,2,5,'yes',NULL),(9,2,6,'yes',NULL),(9,2,7,'yes',NULL),(9,2,8,'yes',NULL),(9,2,9,'yes',NULL),(9,2,10,'yes',NULL),(9,2,11,'yes',NULL),(9,2,12,'yes',NULL),(9,2,13,'yes',NULL),(9,2,14,'yesbut','hi'),(9,2,15,'yes',NULL),(9,2,16,'yes',NULL),(9,1,1,'yes',NULL),(9,1,2,'no',NULL),(9,1,3,'yes',NULL),(9,1,4,'yes',NULL),(9,1,5,'yes',NULL),(9,1,6,'no',NULL),(9,1,7,'yes',NULL),(9,1,8,'yes',NULL),(9,1,9,'yes',NULL),(9,1,10,'no',NULL),(9,1,11,'yes',NULL),(9,1,12,'yes',NULL),(9,1,13,'yes',NULL),(9,1,14,'yes',NULL),(9,1,15,'no',NULL),(9,1,16,'yes',NULL),(9,3,1,'yes',NULL),(9,3,2,'yes',NULL),(9,3,3,'yes',NULL),(9,3,4,'yes',NULL),(9,3,5,'yes',NULL),(9,3,6,'yes',NULL),(9,3,7,'yes',NULL),(9,3,8,'yes',NULL),(9,3,9,'yesbut','heeds'),(9,3,10,'yes',NULL),(9,3,11,'yes',NULL),(9,3,12,'yes',NULL),(9,3,13,'yes',NULL),(9,3,14,'yes',NULL),(9,3,15,'yes',NULL),(9,3,16,'yes',NULL),(23,3,1,'yesbut','oo'),(23,3,2,'no',NULL),(23,3,3,'no',NULL),(23,3,4,'no',NULL),(23,3,5,'no',NULL),(23,3,6,'no',NULL),(23,3,7,'no',NULL),(23,3,8,'no',NULL),(23,3,9,'no',NULL),(23,3,10,'yes',NULL),(23,3,11,'no',NULL),(23,3,12,'no',NULL),(23,3,13,'no',NULL),(23,3,14,'no',NULL),(23,3,15,'no',NULL),(23,3,16,'no',NULL);
/*!40000 ALTER TABLE `evaluation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `question`
--

DROP TABLE IF EXISTS `question`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `question` (
  `q_id` int(11) NOT NULL AUTO_INCREMENT,
  `num` int(11) DEFAULT NULL,
  `version` int(11) DEFAULT '1',
  `content` text,
  `short_content` text,
  `F` text,
  `A` text,
  `I` text,
  `R` text,
  `res_type` text,
  PRIMARY KEY (`q_id`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `question`
--

LOCK TABLES `question` WRITE;
/*!40000 ALTER TABLE `question` DISABLE KEYS */;
INSERT INTO `question` VALUES (1,1,1,'The tool is hosted in one or more well-used repositories, if relevant repositories exist',NULL,'F','A',NULL,NULL,'Tool'),(2,2,1,'Source code is shared on a public repository',NULL,NULL,'A',NULL,NULL,'Tool'),(3,3,1,'Code is written in an open-source, free programming language',NULL,NULL,'A',NULL,NULL,'Tool'),(4,4,1,'The tool inputs standard data format(s) consistent with community practice',NULL,NULL,'A','I','R','Tool'),(5,5,1,'All previous versions of the tool are made available',NULL,NULL,'A','I','R','Tool'),(6,6,1,'Web-based version is available (in addition to desktop version)',NULL,NULL,'A',NULL,'R','Tool'),(7,7,1,'Source code is documented',NULL,NULL,NULL,NULL,'R','Tool'),(8,8,1,'Pipelines that use the tool have been standardized and provide detailed usage guidelines',NULL,NULL,NULL,NULL,'R','Tool'),(9,9,1,'A tutorial page is provided for the tool',NULL,NULL,NULL,NULL,'R','Tool'),(10,10,1,'Example datasets are provided',NULL,NULL,NULL,NULL,'R','Tool'),(11,11,1,'Licensing information is provided on the tool’s landing page',NULL,NULL,NULL,NULL,'R','Tool'),(12,12,1,'Information is provided describing how to cite the tool',NULL,NULL,NULL,NULL,'R','Tool'),(13,13,1,'Version information is provided for the tool',NULL,NULL,NULL,NULL,'R','Tool'),(14,14,1,'A paper about the tool has been published',NULL,NULL,NULL,NULL,'R','Tool'),(15,15,1,'Video tutorials for the tool are available',NULL,NULL,NULL,NULL,'R','Tool'),(16,16,1,'Contact information is provided for the originator(s) of the tool',NULL,NULL,NULL,NULL,'R','Tool'),(17,1,1,'Standardized IDs are used to identify dataset',NULL,'F',NULL,NULL,NULL,'Dataset'),(18,2,1,'The dataset can be located on the host platform via free-text search and menu-driven decision tree search',NULL,'F',NULL,NULL,NULL,'Dataset'),(19,3,1,'The dataset is hosted in one or more well-used repositories, if relevant repositories exist',NULL,'F','A',NULL,NULL,'Dataset'),(20,4,1,'(Meta)data are assigned a globally unique and eternally persistent identifier',NULL,'F',NULL,NULL,'R','Dataset'),(21,5,1,'The dataset is retrievable by a standardized protocol',NULL,NULL,'A',NULL,NULL,'Dataset'),(22,6,1,'The dataset is available in a human-readable format',NULL,NULL,'A',NULL,NULL,'Dataset'),(23,7,1,'The dataset is available in a standard machine-accessible format (that is interoperable with popular analysis tools)',NULL,NULL,'A',NULL,NULL,'Dataset'),(24,8,1,'The meta(data) are sufficiently complete to permit effective reuse',NULL,NULL,NULL,NULL,'R','Dataset'),(25,9,1,'Metadata are linked to other relevant datasets, vocabularies and ontologies',NULL,NULL,NULL,'I',NULL,'Dataset'),(26,10,1,'A tutorial page is provided for the dataset to describe the format of the dataset',NULL,NULL,NULL,NULL,'R','Dataset'),(27,11,1,'Information is provided describing how to cite the dataset',NULL,NULL,NULL,NULL,'R','Dataset'),(28,12,1,'A description of the methods used to acquire the data is provided',NULL,NULL,NULL,NULL,'R','Dataset'),(29,13,1,'Licensing information is provided on the dataset’s landing page',NULL,NULL,NULL,NULL,'R','Dataset'),(30,14,1,'Version information is provided on the dataset’s landing page',NULL,NULL,NULL,NULL,'R','Dataset'),(31,15,1,'Tools that can be used to analyze the dataset are listed on the dataset’s landing page',NULL,NULL,NULL,NULL,'R','Dataset'),(32,16,1,'Contact information is provided for the originator(s) of the dataset',NULL,NULL,NULL,NULL,'R','Dataset');
/*!40000 ALTER TABLE `question` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `resource`
--

DROP TABLE IF EXISTS `resource`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `resource` (
  `resource_id` int(11) NOT NULL AUTO_INCREMENT,
  `resource_name` text,
  `url` text,
  `resource_type` text,
  `description` text,
  `average1` double DEFAULT NULL,
  `average2` double DEFAULT NULL,
  `average3` double DEFAULT NULL,
  `average4` double DEFAULT NULL,
  `average5` double DEFAULT NULL,
  `average6` double DEFAULT NULL,
  `average7` double DEFAULT NULL,
  `average8` double DEFAULT NULL,
  `average9` double DEFAULT NULL,
  `average10` double DEFAULT NULL,
  `average11` double DEFAULT NULL,
  `average12` double DEFAULT NULL,
  `average13` double DEFAULT NULL,
  `average14` double DEFAULT NULL,
  `average15` double DEFAULT NULL,
  `average16` double DEFAULT NULL,
  PRIMARY KEY (`resource_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `resource`
--

LOCK TABLES `resource` WRITE;
/*!40000 ALTER TABLE `resource` DISABLE KEYS */;
INSERT INTO `resource` VALUES (1,'L1000CDS2','http://amp.pharm.mssm.edu/L1000CDS2','Tool','An ultra-fast LINCS L1000 Characteristic Direction signature search engine',-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1),(2,'iLINCS','http://www.ilincs.org/','Tool','An integrative web platform for analysis of LINCS data and signatures',0.333333333333,0,0,0.333333333333,0.333333333333,-0.333333333333,0.333333333333,0.333333333333,0.333333333333,0.333333333333,-0.333333333333,0.333333333333,0.333333333333,0,0.333333333333,0.333333333333),(3,'Query App','http://clue.io/query','Tool','Connections to user-defined signatures',-0.5,-0.5,0.5,-0.5,0.5,-0.5,-0.5,0.5,-0.5,0,0.5,-0.5,0.5,0.5,0.5,0.5),(4,'Drug-Pathway Browser','http://lincs.hms.harvard.edu/explore/pathway/','Tool','Interactive map of key signal transduction pathways and drug-target data',1,1,-1,1,1,1,1,1,0,1,1,1,1,-1,-1,-1),(5,'Drug/Cell-line Browser','http://www.maayanlab.net/LINCS/DCB/','Tool','DCB provides interactive visualization of cancer cell-line viability data',0.4,0,0.8,0,-0.4,0.6,0.4,0.2,0.6,0.6,-0.2,-0.4,-0.2,-0.2,-0.8,-0.6),(6,'Harmonizome','http://amp.pharm.mssm.edu/Harmonizome/','Tool','Web portal with a collection of 114 datasets abstracted into gene function tables',-1,0,1,-1,0,1,0,0,0,1,0,1,1,1,1,0),(7,'GEO2Enrichr','http://amp.pharm.mssm.edu/g2e','Tool','A web app and browser extension to extract and analyze signatures from GEO',0.5,0.5,-0.5,-0.5,-0.5,-0.5,-0.5,-0.5,0.5,0,0,0.5,0.5,0.5,0,0.5),(8,'Enrichr','http://amp.pharm.mssm.edu/Enrichr','Tool','An intuitive web-based gene list enrichment analysis tool with 90 libraries',0.5,-0.5,-0.5,0.5,0.5,0.5,-0.5,-0.5,0.5,0.5,0.5,0.5,-0.5,0.5,0.5,0.5);
/*!40000 ALTER TABLE `resource` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `table1`
--

DROP TABLE IF EXISTS `table1`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `table1` (
  `user_id` int(11) DEFAULT NULL,
  `resource_id` int(11) DEFAULT NULL,
  `q_id` int(11) DEFAULT NULL,
  `answer` text,
  `comment` text
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `table1`
--

LOCK TABLES `table1` WRITE;
/*!40000 ALTER TABLE `table1` DISABLE KEYS */;
INSERT INTO `table1` VALUES (10,1,33,'no',NULL),(10,1,34,'no',NULL),(10,1,35,'no',NULL),(10,1,36,'no',NULL),(10,1,37,'no',NULL),(10,1,38,'no',NULL),(10,1,39,'no',NULL),(10,1,40,'no',NULL),(10,1,41,'no',NULL),(10,1,42,'no',NULL),(10,1,43,'no',NULL),(10,1,44,'no',NULL),(10,1,45,'no',NULL),(10,1,46,'no',NULL),(10,1,47,'no',NULL),(10,1,48,'no',NULL),(9,1,33,'yes',NULL),(9,1,34,'no',NULL),(9,1,35,'yes',NULL),(9,1,36,'yes',NULL),(9,1,37,'yes',NULL),(9,1,38,'no',NULL),(9,1,39,'yes',NULL),(9,1,40,'yes',NULL),(9,1,41,'yes',NULL),(9,1,42,'no',NULL),(9,1,43,'yes',NULL),(9,1,44,'yes',NULL),(9,1,45,'yes',NULL),(9,1,46,'yes',NULL),(9,1,47,'no',NULL),(9,1,48,'yes',NULL);
/*!40000 ALTER TABLE `table1` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `username` text,
  `password` text,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'thisuser','thispass'),(2,'thisuser@gmail.com','newpass'),(3,'thisuser@gmail.com','passpass'),(4,'thisuser@gmail.com','whew'),(5,'hi','hi'),(8,'hi@gmail.com','um'),(9,'new@g.com','okoko'),(10,'okr@gmail.com','whew'),(11,'gor@gmail.com','w'),(12,'go@gmail.com','ok'),(13,'go@gmail.com','go'),(14,'go@gmail.com','gogogogogo'),(15,'ok@gmail.com','new'),(16,'userplaceholder@g.com','nnpass'),(17,'th@gmail.com','the'),(18,'tih@gmail.com','th'),(19,'hhh@gmail.com','new'),(20,'okok','okok'),(21,'ex@gmail.com','ok'),(22,'ne@gmail.com','ne'),(23,'newu@gmail.com','new'),(24,'g@g.com','g');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-07-12 11:52:27
