
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
INSERT INTO `NLIDB_FIELD_SYNONYMS` (`SYNONYM`, `FIELD`) VALUES
('production_of_gas', 'ANP.GAS_PRODUCTION'),
('oil_production', 'ANP.OIL_PRODUCTION'),
('production_of_oil', 'ANP.OIL_PRODUCTION'),
('petroleum_production', 'ANP.OIL_PRODUCTION'),
('production_of_petroleum', 'ANP.OIL_PRODUCTION'),
('production', 'ANP.OIL_PRODUCTION'),
('oil', 'ANP.OIL_PRODUCTION'),
('petroleum', 'ANP.OIL_PRODUCTION'),
('gas', 'ANP.GAS_PRODUCTION'),
('gas_production', 'ANP.GAS_PRODUCTION'),
('federated_state', 'ANP.STATE'),
('state_of_brazil', 'ANP.STATE'),
('state_of_federation', 'ANP.STATE'),
('state_of_federal_republic', 'ANP.STATE'),
('field', 'ANP.FIELD'),
('operator', 'ANP.OPERATOR'),
('state', 'ANP.STATE'),
('contract_number', 'ANP.CONTRACT_NUMBER'),
('basin', 'ANP.BASIN'),
('year', 'ANP.YEAR'),
('month', 'ANP.YEAR,ANP.MONTH'),
('ANP_MONTH', 'ANP.YEAR,ANP.MONTH');
--this last one is used by the NLIDB 
/*!40000 ALTER TABLE `NLIDB_FIELD_SYNONYMS` ENABLE KEYS */;
UNLOCK TABLES;
