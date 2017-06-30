CREATE DATABASE  IF NOT EXISTS `HyperFlexTopologyProduction` /*!40100 DEFAULT CHARACTER SET latin1 */;
USE `HyperFlexTopologyProduction`;
-- MySQL dump 10.13  Distrib 5.5.44, for debian-linux-gnu (x86_64)
--
-- Host: 127.0.0.1    Database: HyperFlexTopologyProduction
-- ------------------------------------------------------
-- Server version	5.5.44-0ubuntu0.14.04.1

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
-- Table structure for table `Controller`
--

DROP TABLE IF EXISTS `Controller`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Controller` (
  `location` varchar(45) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ip_port` int(11) unsigned NOT NULL,
  `network_node_id` int(11) NOT NULL,
  PRIMARY KEY (`network_node_id`),
  UNIQUE KEY `network_node_id_UNIQUE` (`network_node_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Controller`
--

LOCK TABLES `Controller` WRITE;
/*!40000 ALTER TABLE `Controller` DISABLE KEYS */;
/*!40000 ALTER TABLE `Controller` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `FlowVisorFlowMatch`
--

DROP TABLE IF EXISTS `FlowVisorFlowMatch`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `FlowVisorFlowMatch` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `in_port` int(11) DEFAULT NULL,
  `dl_vlan` varchar(45) DEFAULT NULL,
  `dl_src` varchar(45) DEFAULT NULL,
  `dl_dst` varchar(45) DEFAULT NULL,
  `dl_type` varchar(45) DEFAULT NULL,
  `nw_src` varchar(45) DEFAULT NULL,
  `nw_dst` varchar(45) DEFAULT NULL,
  `nw_proto` varchar(45) DEFAULT NULL,
  `nw_tos` varchar(45) DEFAULT NULL,
  `tp_src` int(11) DEFAULT NULL,
  `tp_dst` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=115 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `FlowVisorFlowMatch`
--

LOCK TABLES `FlowVisorFlowMatch` WRITE;
/*!40000 ALTER TABLE `FlowVisorFlowMatch` DISABLE KEYS */;
/*!40000 ALTER TABLE `FlowVisorFlowMatch` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `FlowVisorFlowSpace`
--

DROP TABLE IF EXISTS `FlowVisorFlowSpace`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `FlowVisorFlowSpace` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `dpid` varchar(45) NOT NULL,
  `flowmatch_id` int(11) NOT NULL,
  `priority` int(11) DEFAULT '100',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=115 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `FlowVisorFlowSpace`
--

LOCK TABLES `FlowVisorFlowSpace` WRITE;
/*!40000 ALTER TABLE `FlowVisorFlowSpace` DISABLE KEYS */;
/*!40000 ALTER TABLE `FlowVisorFlowSpace` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Host`
--

DROP TABLE IF EXISTS `Host`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Host` (
  `vsdn_id` int(11) NOT NULL,
  `network_node_id` int(11) NOT NULL,
  PRIMARY KEY (`network_node_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Host`
--

LOCK TABLES `Host` WRITE;
/*!40000 ALTER TABLE `Host` DISABLE KEYS */;
INSERT INTO `Host` VALUES (1,8),(1,9);
/*!40000 ALTER TABLE `Host` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Hypervisor`
--

DROP TABLE IF EXISTS `Hypervisor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Hypervisor` (
  `network_node_id` int(11) NOT NULL DEFAULT '0',
  `status` int(11) DEFAULT NULL,
  `user` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `password` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `port` int(11) DEFAULT NULL,
  PRIMARY KEY (`network_node_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Hypervisor`
--

LOCK TABLES `Hypervisor` WRITE;
/*!40000 ALTER TABLE `Hypervisor` DISABLE KEYS */;
INSERT INTO `Hypervisor` VALUES (10,1,'fvadmin','',8081);
/*!40000 ALTER TABLE `Hypervisor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `LogicalEdge`
--

DROP TABLE IF EXISTS `LogicalEdge`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `LogicalEdge` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `node_one_id` int(11) NOT NULL,
  `node_two_id` int(11) NOT NULL,
  `vsdn_id` int(11) NOT NULL,
  `datarate` int(255) DEFAULT NULL,
  `cplane` tinyint(1) DEFAULT NULL,
  `msgrate` int(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=83 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `LogicalEdge`
--

LOCK TABLES `LogicalEdge` WRITE;
/*!40000 ALTER TABLE `LogicalEdge` DISABLE KEYS */;
/*!40000 ALTER TABLE `LogicalEdge` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `LogicalEdgeEmbedding`
--

DROP TABLE IF EXISTS `LogicalEdgeEmbedding`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `LogicalEdgeEmbedding` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `logical_edge_id` int(10) unsigned NOT NULL,
  `physical_edge_id` int(10) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=98 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `LogicalEdgeEmbedding`
--

LOCK TABLES `LogicalEdgeEmbedding` WRITE;
/*!40000 ALTER TABLE `LogicalEdgeEmbedding` DISABLE KEYS */;
/*!40000 ALTER TABLE `LogicalEdgeEmbedding` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `NetworkNode`
--

DROP TABLE IF EXISTS `NetworkNode`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `NetworkNode` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `ip` varchar(45) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(45) COLLATE utf8mb4_unicode_ci NOT NULL,
  `info_type` int(11) NOT NULL,
  `x` int(255) DEFAULT NULL,
  `y` int(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=73 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `NetworkNode`
--

LOCK TABLES `NetworkNode` WRITE;
/*!40000 ALTER TABLE `NetworkNode` DISABLE KEYS */;
INSERT INTO `NetworkNode` VALUES (1,'192.168.1.3','Berlin',2,253,-198),(2,'192.168.1.4','Hamburg',2,-137,-266),(3,'192.168.0.5','Cologne',2,-257,25),(4,'192.168.0.6','Frankfurt',2,-151,140),(5,'192.168.0.7','Dresden',2,311,43),(6,'192.168.0.8','Stuttgart',2,-89,328),(8,'192.168.1.8','Munich',2,103,441),(10,'192.168.56.150','Hypervisor',4,-100,0),(22,'127.0.0.1','ctrl1',2,0,0),(67,'17.0.0.1','ctrl2',2,400,400),(68,'17.0.0.2','ctrl3',2,400,375),(69,'17.0.0.3','ctrl4',2,400,350);
/*!40000 ALTER TABLE `NetworkNode` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `PhysicalEdge`
--

DROP TABLE IF EXISTS `PhysicalEdge`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `PhysicalEdge` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `node_one_id` int(11) NOT NULL,
  `node_two_id` int(11) NOT NULL,
  `port_one_id` int(10) unsigned DEFAULT NULL,
  `port_two_id` int(10) unsigned DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `PhysicalEdge`
--

LOCK TABLES `PhysicalEdge` WRITE;
/*!40000 ALTER TABLE `PhysicalEdge` DISABLE KEYS */;
INSERT INTO `PhysicalEdge` VALUES (1,4,1,211,181),(2,4,2,212,191),(3,4,3,213,201),(5,4,5,214,221),(6,4,6,215,231),(9,4,8,216,241),(10,1,2,182,192),(11,6,8,232,242),(12,10,4,NULL,NULL),(31,22,67,266,267),(32,68,67,288,268),(33,69,67,278,269),(36,22,10,298,NULL);
/*!40000 ALTER TABLE `PhysicalEdge` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `PhysicalPort`
--

DROP TABLE IF EXISTS `PhysicalPort`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `PhysicalPort` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `switch_id` int(11) NOT NULL,
  `number` int(11) NOT NULL,
  `speed` double DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=299 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `PhysicalPort`
--

LOCK TABLES `PhysicalPort` WRITE;
/*!40000 ALTER TABLE `PhysicalPort` DISABLE KEYS */;
INSERT INTO `PhysicalPort` VALUES (1,10,1,1000),(181,1,1,1000),(182,1,2,1000),(183,1,3,1000),(184,1,4,1000),(185,1,5,1000),(186,1,6,1000),(187,1,7,1000),(188,1,8,1000),(189,1,9,1000),(190,1,10,1000),(191,2,1,100),(192,2,2,100),(193,2,3,100),(194,2,4,100),(195,2,5,100),(196,2,6,100),(197,2,7,100),(198,2,8,100),(199,2,9,100),(200,2,10,100),(201,3,1,1000),(202,3,2,1000),(203,3,3,1000),(204,3,4,1000),(205,3,5,1000),(206,3,6,1000),(207,3,7,1000),(208,3,8,1000),(209,3,9,1000),(210,3,10,1000),(211,4,1,1000),(212,4,2,1000),(213,4,3,1000),(214,4,4,1000),(215,4,5,1000),(216,4,6,1000),(217,4,7,1000),(218,4,8,1000),(219,4,9,1000),(220,4,10,1000),(221,5,1,1000),(222,5,2,1000),(223,5,3,1000),(224,5,4,1000),(225,5,5,1000),(226,5,6,1000),(227,5,7,1000),(228,5,8,1000),(229,5,9,1000),(230,5,10,1000),(231,6,1,1000),(232,6,2,1000),(233,6,3,1000),(234,6,4,1000),(235,6,5,1000),(236,6,6,1000),(237,6,7,1000),(238,6,8,1000),(239,6,9,1000),(240,6,10,1000),(241,8,1,1000),(242,8,2,1000),(243,8,3,1000),(244,8,4,1000),(245,8,5,1000),(246,8,6,1000),(247,8,7,1000),(248,8,8,1000),(249,8,9,1000),(250,8,10,1000),(251,8,11,1000),(252,8,12,1000),(253,8,13,1000),(254,8,14,1000),(255,8,15,1000),(256,8,16,1000),(257,8,17,1000),(258,8,18,1000),(259,8,19,1000),(261,22,1,1000),(266,22,2,1000),(267,67,1,1000),(268,67,2,1000),(269,67,3,1000),(270,67,4,1000),(271,67,5,1000),(272,67,6,1000),(273,67,7,1000),(274,67,8,1000),(275,67,9,1000),(276,67,10,1000),(277,67,1,1000),(278,69,1,1000),(279,69,2,1000),(280,69,3,1000),(281,69,4,1000),(282,69,5,1000),(283,69,6,1000),(284,69,7,1000),(285,69,8,1000),(286,69,9,1000),(287,69,10,1000),(288,68,1,1000),(289,68,2,1000),(290,68,3,1000),(291,68,4,1000),(292,68,5,1000),(293,68,6,1000),(294,68,7,1000),(295,68,8,1000),(296,68,9,1000),(297,68,10,1000),(298,22,3,1000);
/*!40000 ALTER TABLE `PhysicalPort` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `PhysicalSwitch`
--

DROP TABLE IF EXISTS `PhysicalSwitch`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `PhysicalSwitch` (
  `dpid` varchar(45) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ip_port` int(11) DEFAULT NULL,
  `num_ports` int(11) DEFAULT NULL,
  `cplane` int(1) NOT NULL,
  `network_node_id` int(11) NOT NULL,
  PRIMARY KEY (`network_node_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `PhysicalSwitch`
--

LOCK TABLES `PhysicalSwitch` WRITE;
/*!40000 ALTER TABLE `PhysicalSwitch` DISABLE KEYS */;
INSERT INTO `PhysicalSwitch` VALUES ('00:00:00:00:00:00:00:01',9100,10,0,1),('00:00:00:00:00:00:00:02',9100,10,0,2),('00:00:00:00:00:00:00:03',9100,10,0,3),('00:00:00:00:00:00:00:04',9100,10,0,4),('00:00:00:00:00:00:00:05',9100,10,0,5),('00:00:00:00:00:00:00:06',9100,10,0,6),('00:00:00:00:00:00:00:08',9100,20,0,8),('00:00:00:00:00:00:00:01',7854,3,1,22),('00:00:00:00:00:00:00:67',5555,10,1,67),('00:00:00:00:00:00:00:68',5555,10,1,68),('00:00:00:00:00:00:00:69',5555,10,1,69);
/*!40000 ALTER TABLE `PhysicalSwitch` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `SlicePermission`
--

DROP TABLE IF EXISTS `SlicePermission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `SlicePermission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `flow_visor_flow_space_id` int(11) NOT NULL,
  `vsdn_id` int(11) NOT NULL,
  `permission` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=115 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `SlicePermission`
--

LOCK TABLES `SlicePermission` WRITE;
/*!40000 ALTER TABLE `SlicePermission` DISABLE KEYS */;
/*!40000 ALTER TABLE `SlicePermission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `SwitchToVsdn`
--

DROP TABLE IF EXISTS `SwitchToVsdn`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `SwitchToVsdn` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `vsdn_id` int(11) DEFAULT NULL,
  `switch_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=95 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `SwitchToVsdn`
--

LOCK TABLES `SwitchToVsdn` WRITE;
/*!40000 ALTER TABLE `SwitchToVsdn` DISABLE KEYS */;
/*!40000 ALTER TABLE `SwitchToVsdn` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Tenant`
--

DROP TABLE IF EXISTS `Tenant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Tenant` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(45) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Tenant`
--

LOCK TABLES `Tenant` WRITE;
/*!40000 ALTER TABLE `Tenant` DISABLE KEYS */;
INSERT INTO `Tenant` VALUES (1,'tenant1');
/*!40000 ALTER TABLE `Tenant` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Vsdn`
--

DROP TABLE IF EXISTS `Vsdn`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `Vsdn` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tenant_id` int(11) NOT NULL,
  `color` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `name` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `subnet` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `controller_id` int(11) DEFAULT NULL,
  `hypervisor_id` int(11) DEFAULT NULL,
  `message_rate` int(11) DEFAULT NULL,
  `isolation` int(11) DEFAULT NULL,
  `password` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=48 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Vsdn`
--

LOCK TABLES `Vsdn` WRITE;
/*!40000 ALTER TABLE `Vsdn` DISABLE KEYS */;
/*!40000 ALTER TABLE `Vsdn` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-10-29 16:56:55
