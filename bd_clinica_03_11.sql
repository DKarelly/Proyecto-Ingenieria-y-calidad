CREATE DATABASE  IF NOT EXISTS `CLINICA` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `CLINICA`;
-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: trolley.proxy.rlwy.net    Database: CLINICA
-- ------------------------------------------------------
-- Server version	9.4.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `ASIGNAR_EMPLEADO_INCIDENCIA`
--

DROP TABLE IF EXISTS `ASIGNAR_EMPLEADO_INCIDENCIA`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ASIGNAR_EMPLEADO_INCIDENCIA` (
  `id_historial` int NOT NULL AUTO_INCREMENT,
  `observaciones` varchar(200) DEFAULT NULL,
  `estado_historial` varchar(20) DEFAULT NULL,
  `fecha_resolucion` date DEFAULT NULL,
  `id_empleado` int DEFAULT NULL,
  `id_incidencia` int DEFAULT NULL,
  PRIMARY KEY (`id_historial`),
  KEY `id_empleado` (`id_empleado`),
  KEY `id_incidencia` (`id_incidencia`),
  CONSTRAINT `ASIGNAR_EMPLEADO_INCIDENCIA_ibfk_1` FOREIGN KEY (`id_empleado`) REFERENCES `EMPLEADO` (`id_empleado`),
  CONSTRAINT `ASIGNAR_EMPLEADO_INCIDENCIA_ibfk_2` FOREIGN KEY (`id_incidencia`) REFERENCES `INCIDENCIA` (`id_incidencia`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ASIGNAR_EMPLEADO_INCIDENCIA`
--

LOCK TABLES `ASIGNAR_EMPLEADO_INCIDENCIA` WRITE;
/*!40000 ALTER TABLE `ASIGNAR_EMPLEADO_INCIDENCIA` DISABLE KEYS */;
INSERT INTO `ASIGNAR_EMPLEADO_INCIDENCIA` VALUES (9,'','Resuelta','2025-10-30',5,9),(10,'Reparación programada por plomería mañana.','En proceso',NULL,7,10),(11,'Equipo informático enviado a soporte técnico.','Resuelta','2025-10-27',3,11),(12,'Insumos repuestos por personal de almacén.','Resuelta','2025-10-27',2,12),(13,'Ascensor reportado al proveedor externo.','Abierta',NULL,6,13),(14,'Electricista notificó posible corto circuito, revisión mañana.','En proceso',NULL,1,14),(15,'Soporte de red realizó revisión parcial del router.','En proceso',NULL,4,15),(16,'Puerta ajustada, requiere reemplazo de bisagra.','Resuelta','2025-10-30',5,16),(17,'Incidencia marcada como resuelta','Resuelta','2025-10-31',6,21),(18,'Incidencia marcada como resuelta','Resuelta','2025-10-31',2,22),(19,'Incidencia marcada como resuelta','Resuelta','2025-10-31',2,23),(20,'','En proceso',NULL,7,24),(21,'Incidencia marcada como resuelta','En proceso','2025-10-31',5,25),(22,NULL,'En proceso',NULL,2,26),(23,NULL,'En proceso',NULL,2,27),(24,NULL,'Abierta',NULL,7,28),(25,'','En proceso',NULL,17,33),(26,'','En proceso',NULL,5,32),(27,'','En proceso',NULL,7,31),(28,'','En proceso',NULL,6,30),(29,'','En proceso',NULL,7,29),(30,'','En proceso',NULL,5,20),(31,'','En proceso',NULL,6,19),(32,'','En proceso',NULL,7,18),(33,'','En proceso',NULL,1,17),(34,'','En proceso',NULL,5,34),(35,'Incidencia resuelta','Resuelta','2025-11-02',7,36),(36,'','En proceso',NULL,6,35),(37,'','Resuelta','2025-11-02',1,38);
/*!40000 ALTER TABLE `ASIGNAR_EMPLEADO_INCIDENCIA` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `AUDITORIA`
--

DROP TABLE IF EXISTS `AUDITORIA`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `AUDITORIA` (
  `id_auditoria` int NOT NULL AUTO_INCREMENT,
  `id_usuario` int DEFAULT NULL,
  `id_empleado` int DEFAULT NULL,
  `accion` varchar(100) NOT NULL,
  `modulo` varchar(50) NOT NULL,
  `tipo_evento` varchar(50) NOT NULL,
  `descripcion` text,
  `ip_address` varchar(45) DEFAULT NULL,
  `fecha_registro` datetime DEFAULT CURRENT_TIMESTAMP,
  `detalles_json` text,
  PRIMARY KEY (`id_auditoria`),
  KEY `id_usuario` (`id_usuario`),
  KEY `id_empleado` (`id_empleado`),
  KEY `idx_fecha` (`fecha_registro`),
  KEY `idx_modulo` (`modulo`),
  KEY `idx_tipo_evento` (`tipo_evento`),
  CONSTRAINT `AUDITORIA_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `USUARIO` (`id_usuario`),
  CONSTRAINT `AUDITORIA_ibfk_2` FOREIGN KEY (`id_empleado`) REFERENCES `EMPLEADO` (`id_empleado`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `AUDITORIA`
--

LOCK TABLES `AUDITORIA` WRITE;
/*!40000 ALTER TABLE `AUDITORIA` DISABLE KEYS */;
/*!40000 ALTER TABLE `AUDITORIA` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `AUDITORIA_ARCHIVO`
--

DROP TABLE IF EXISTS `AUDITORIA_ARCHIVO`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `AUDITORIA_ARCHIVO` (
  `id_archivo` int NOT NULL AUTO_INCREMENT,
  `id_auditoria` int NOT NULL,
  `nombre_archivo` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ruta_archivo` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `tipo_archivo` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `tamano_bytes` bigint DEFAULT NULL,
  `fecha_subida` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_archivo`),
  KEY `idx_auditoria` (`id_auditoria`),
  KEY `idx_fecha` (`fecha_subida`),
  CONSTRAINT `AUDITORIA_ARCHIVO_ibfk_1` FOREIGN KEY (`id_auditoria`) REFERENCES `AUDITORIA` (`id_auditoria`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `AUDITORIA_ARCHIVO`
--

LOCK TABLES `AUDITORIA_ARCHIVO` WRITE;
/*!40000 ALTER TABLE `AUDITORIA_ARCHIVO` DISABLE KEYS */;
/*!40000 ALTER TABLE `AUDITORIA_ARCHIVO` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `BLOQUEO_PROGRAMACION`
--

DROP TABLE IF EXISTS `BLOQUEO_PROGRAMACION`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `BLOQUEO_PROGRAMACION` (
  `id_bloqueo` int NOT NULL AUTO_INCREMENT,
  `fecha` date DEFAULT NULL,
  `hora_inicio` time DEFAULT NULL,
  `hora_fin` time DEFAULT NULL,
  `motivo` text,
  `estado` varchar(20) DEFAULT NULL,
  `id_programacion` int DEFAULT NULL,
  PRIMARY KEY (`id_bloqueo`),
  KEY `id_programacion` (`id_programacion`),
  CONSTRAINT `BLOQUEO_PROGRAMACION_ibfk_1` FOREIGN KEY (`id_programacion`) REFERENCES `PROGRAMACION` (`id_programacion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `BLOQUEO_PROGRAMACION`
--

LOCK TABLES `BLOQUEO_PROGRAMACION` WRITE;
/*!40000 ALTER TABLE `BLOQUEO_PROGRAMACION` DISABLE KEYS */;
/*!40000 ALTER TABLE `BLOQUEO_PROGRAMACION` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `CATEGORIA`
--

DROP TABLE IF EXISTS `CATEGORIA`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `CATEGORIA` (
  `id_categoria` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) DEFAULT NULL,
  `descripcion` text,
  `estado` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id_categoria`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `CATEGORIA`
--

LOCK TABLES `CATEGORIA` WRITE;
/*!40000 ALTER TABLE `CATEGORIA` DISABLE KEYS */;
INSERT INTO `CATEGORIA` VALUES (1,'Citas','Reportes relacionados con citas y agendamiento médico','Activo'),(2,'Usuarios','Reportes de gestión y administración de usuarios del sistema','Activo'),(3,'Servicios','Reportes sobre servicios médicos ofrecidos por la clínica','Activo'),(4,'Recursos','Reportes de ocupación y disponibilidad de recursos físicos','Activo'),(5,'Pacientes','Reportes de datos demográficos y históricos de pacientes','Activo'),(6,'Personal','Reportes de empleados, horarios y especialidades','Activo'),(7,'Incidencias','Reportes de problemas, quejas y eventos reportados','Activo'),(8,'Auditoría','Reportes de actividades del sistema y logs de acceso','Activo');
/*!40000 ALTER TABLE `CATEGORIA` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `CITA`
--

DROP TABLE IF EXISTS `CITA`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `CITA` (
  `id_cita` int NOT NULL AUTO_INCREMENT,
  `fecha_cita` date DEFAULT NULL,
  `hora_inicio` time DEFAULT NULL,
  `hora_fin` time DEFAULT NULL,
  `diagnostico` text,
  `observaciones` text,
  `estado` varchar(20) DEFAULT NULL,
  `id_reserva` int DEFAULT NULL,
  PRIMARY KEY (`id_cita`),
  KEY `id_reserva` (`id_reserva`),
  CONSTRAINT `CITA_ibfk_1` FOREIGN KEY (`id_reserva`) REFERENCES `RESERVA` (`id_reserva`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `CITA`
--

LOCK TABLES `CITA` WRITE;
/*!40000 ALTER TABLE `CITA` DISABLE KEYS */;
/*!40000 ALTER TABLE `CITA` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `DEPARTAMENTO`
--

DROP TABLE IF EXISTS `DEPARTAMENTO`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `DEPARTAMENTO` (
  `id_departamento` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  PRIMARY KEY (`id_departamento`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `DEPARTAMENTO`
--

LOCK TABLES `DEPARTAMENTO` WRITE;
/*!40000 ALTER TABLE `DEPARTAMENTO` DISABLE KEYS */;
INSERT INTO `DEPARTAMENTO` VALUES (1,'Amazonas'),(2,'Áncash'),(3,'Apurímac'),(4,'Arequipa'),(5,'Ayacucho'),(6,'Cajamarca'),(7,'Callao'),(8,'Cusco'),(9,'Huancavelica'),(10,'Huánuco'),(11,'Ica'),(12,'Junín'),(13,'La Libertad'),(14,'Lambayeque'),(15,'Lima'),(16,'Loreto'),(17,'Madre de Dios'),(18,'Moquegua'),(19,'Pasco'),(20,'Piura'),(21,'Puno'),(22,'San Martín'),(23,'Tacna'),(24,'Tumbes'),(25,'Ucayali');
/*!40000 ALTER TABLE `DEPARTAMENTO` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `DISTRITO`
--

DROP TABLE IF EXISTS `DISTRITO`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `DISTRITO` (
  `id_distrito` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `id_provincia` int DEFAULT NULL,
  PRIMARY KEY (`id_distrito`),
  KEY `id_provincia` (`id_provincia`),
  CONSTRAINT `DISTRITO_ibfk_1` FOREIGN KEY (`id_provincia`) REFERENCES `PROVINCIA` (`id_provincia`)
) ENGINE=InnoDB AUTO_INCREMENT=250402 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `DISTRITO`
--

LOCK TABLES `DISTRITO` WRITE;
/*!40000 ALTER TABLE `DISTRITO` DISABLE KEYS */;
INSERT INTO `DISTRITO` VALUES (10101,'Chachapoyas',101),(10102,'Asunción',101),(10103,'Balsas',101),(10104,'Cheto',101),(10105,'Chiliquin',101),(10106,'Chuquibamba',101),(10107,'Granada',101),(10108,'Huancas',101),(10109,'La Jalca',101),(10110,'Leimebamba',101),(10111,'Levanto',101),(10112,'Magdalena',101),(10113,'Mariscal Castilla',101),(10114,'Molinopampa',101),(10115,'Montevideo',101),(10116,'Olleros',101),(10117,'Quinjalca',101),(10118,'San Francisco de Daguas',101),(10119,'San Isidro de Maino',101),(10120,'Soloco',101),(10121,'Sonche',101),(10201,'Bagua',102),(10202,'Aramango',102),(10203,'Copallin',102),(10204,'El Parco',102),(10205,'Imaza',102),(10206,'La Peca',102),(10301,'Jumbilla',103),(10302,'Chisquilla',103),(10303,'Churuja',103),(10304,'Corosha',103),(10305,'Cuispes',103),(10306,'Florida',103),(10307,'Jazan',103),(10308,'Recta',103),(10309,'San Carlos',103),(10310,'Shipasbamba',103),(10311,'Valera',103),(10312,'Yambrasbamba',103),(10401,'Nieva',104),(10402,'El Cenepa',104),(10403,'Río Santiago',104),(10501,'Lamud',105),(10502,'Camporredondo',105),(10503,'Cocabamba',105),(10504,'Colcamar',105),(10505,'Conila',105),(10506,'Inguilpata',105),(10507,'Longuita',105),(10508,'Lonya Chico',105),(10509,'Luya',105),(10510,'Luya Viejo',105),(10511,'María',105),(10512,'Ocalli',105),(10513,'Ocumal',105),(10514,'Pisuquia',105),(10515,'Providencia',105),(10516,'San Cristóbal',105),(10517,'San Francisco de Yeso',105),(10518,'San Jerónimo',105),(10519,'San Juan de Lopecancha',105),(10520,'Santa Catalina',105),(10521,'Santo Tomas',105),(10522,'Tingo',105),(10523,'Trita',105),(10601,'San Nicolás',106),(10602,'Chirimoto',106),(10603,'Cochamal',106),(10604,'Huambo',106),(10605,'Limabamba',106),(10606,'Longar',106),(10607,'Mariscal Benavides',106),(10608,'Milpuc',106),(10609,'Omia',106),(10610,'Santa Rosa',106),(10611,'Totora',106),(10612,'Vista Alegre',106),(10701,'Bagua Grande',107),(10702,'Cajaruro',107),(10703,'Cumba',107),(10704,'El Milagro',107),(10705,'Jamalca',107),(10706,'Lonya Grande',107),(10707,'Yamon',107),(20101,'Huaraz',201),(20102,'Cochabamba',201),(20103,'Colcabamba',201),(20104,'Huanchay',201),(20105,'Independencia',201),(20106,'Jangas',201),(20107,'La Libertad',201),(20108,'Olleros',201),(20109,'Pampas Grande',201),(20110,'Pariacoto',201),(20111,'Pira',201),(20112,'Tarica',201),(20201,'Aija',202),(20202,'Coris',202),(20203,'Huacllan',202),(20204,'La Merced',202),(20205,'Succha',202),(20301,'Llamellin',203),(20302,'Aczo',203),(20303,'Chaccho',203),(20304,'Chingas',203),(20305,'Mirgas',203),(20306,'San Juan de Rontoy',203),(20401,'Chacas',204),(20402,'Acochaca',204),(20501,'Chiquian',205),(20502,'Abelardo Pardo Lezameta',205),(20503,'Antonio Raymondi',205),(20504,'Aquia',205),(20505,'Cajacay',205),(20506,'Canis',205),(20507,'Colquioc',205),(20508,'Huallanca',205),(20509,'Huasta',205),(20510,'Huayllacayan',205),(20511,'La Primavera',205),(20512,'Mangas',205),(20513,'Pacllon',205),(20514,'San Miguel de Corpanqui',205),(20515,'Ticllos',205),(20601,'Carhuaz',206),(20602,'Acopampa',206),(20603,'Amashca',206),(20604,'Anta',206),(20605,'Ataquero',206),(20606,'Marcara',206),(20607,'Pariahuanca',206),(20608,'San Miguel de Aco',206),(20609,'Shilla',206),(20610,'Tinco',206),(20611,'Yungar',206),(20701,'San Luis',207),(20702,'San Nicolás',207),(20703,'Yauya',207),(20801,'Casma',208),(20802,'Buena Vista Alta',208),(20803,'Comandante Noel',208),(20804,'Yautan',208),(20901,'Corongo',209),(20902,'Aco',209),(20903,'Bambas',209),(20904,'Cusca',209),(20905,'La Pampa',209),(20906,'Yanac',209),(20907,'Yupan',209),(21001,'Huari',210),(21002,'Anra',210),(21003,'Cajay',210),(21004,'Chavin de Huantar',210),(21005,'Huacachi',210),(21006,'Huacchis',210),(21007,'Huachis',210),(21008,'Huantar',210),(21009,'Masin',210),(21010,'Paucas',210),(21011,'Ponto',210),(21012,'Rahuapampa',210),(21013,'Rapayan',210),(21014,'San Marcos',210),(21015,'San Pedro de Chana',210),(21016,'Uco',210),(21101,'Huarmey',211),(21102,'Cochapeti',211),(21103,'Culebras',211),(21104,'Huayan',211),(21105,'Malvas',211),(21201,'Caraz',212),(21202,'Huallanca',212),(21203,'Huata',212),(21204,'Huaylas',212),(21205,'Mato',212),(21206,'Pamparomas',212),(21207,'Pueblo Libre',212),(21208,'Santa Cruz',212),(21209,'Santo Toribio',212),(21210,'Yuracmarca',212),(21301,'Piscobamba',213),(21302,'Casca',213),(21303,'Eleazar Guzmán Barron',213),(21304,'Fidel Olivas Escudero',213),(21305,'Llama',213),(21306,'Llumpa',213),(21307,'Lucma',213),(21308,'Musga',213),(21401,'Ocros',214),(21402,'Acas',214),(21403,'Cajamarquilla',214),(21404,'Carhuapampa',214),(21405,'Cochas',214),(21406,'Congas',214),(21407,'Llipa',214),(21408,'San Cristóbal de Rajan',214),(21409,'San Pedro',214),(21410,'Santiago de Chilcas',214),(21501,'Cabana',215),(21502,'Bolognesi',215),(21503,'Conchucos',215),(21504,'Huacaschuque',215),(21505,'Huandoval',215),(21506,'Lacabamba',215),(21507,'Llapo',215),(21508,'Pallasca',215),(21509,'Pampas',215),(21510,'Santa Rosa',215),(21511,'Tauca',215),(21601,'Pomabamba',216),(21602,'Huayllan',216),(21603,'Parobamba',216),(21604,'Quinuabamba',216),(21701,'Recuay',217),(21702,'Catac',217),(21703,'Cotaparaco',217),(21704,'Huayllapampa',217),(21705,'Llacllin',217),(21706,'Marca',217),(21707,'Pampas Chico',217),(21708,'Pararin',217),(21709,'Tapacocha',217),(21710,'Ticapampa',217),(21801,'Chimbote',218),(21802,'Cáceres del Perú',218),(21803,'Coishco',218),(21804,'Macate',218),(21805,'Moro',218),(21806,'Nepeña',218),(21807,'Samanco',218),(21808,'Santa',218),(21809,'Nuevo Chimbote',218),(21901,'Sihuas',219),(21902,'Acobamba',219),(21903,'Alfonso Ugarte',219),(21904,'Cashapampa',219),(21905,'Chingalpo',219),(21906,'Huayllabamba',219),(21907,'Quiches',219),(21908,'Ragash',219),(21909,'San Juan',219),(21910,'Sicsibamba',219),(22001,'Yungay',220),(22002,'Cascapara',220),(22003,'Mancos',220),(22004,'Matacoto',220),(22005,'Quillo',220),(22006,'Ranrahirca',220),(22007,'Shupluy',220),(22008,'Yanama',220),(30101,'Abancay',301),(30102,'Chacoche',301),(30103,'Circa',301),(30104,'Curahuasi',301),(30105,'Huanipaca',301),(30106,'Lambrama',301),(30107,'Pichirhua',301),(30108,'San Pedro de Cachora',301),(30109,'Tamburco',301),(30201,'Andahuaylas',302),(30202,'Andarapa',302),(30203,'Chiara',302),(30204,'Huancarama',302),(30205,'Huancaray',302),(30206,'Huayana',302),(30207,'Kishuara',302),(30208,'Pacobamba',302),(30209,'Pacucha',302),(30210,'Pampachiri',302),(30211,'Pomacocha',302),(30212,'San Antonio de Cachi',302),(30213,'San Jerónimo',302),(30214,'San Miguel de Chaccrampa',302),(30215,'Santa María de Chicmo',302),(30216,'Talavera',302),(30217,'Tumay Huaraca',302),(30218,'Turpo',302),(30219,'Kaquiabamba',302),(30220,'José María Arguedas',302),(30301,'Antabamba',303),(30302,'El Oro',303),(30303,'Huaquirca',303),(30304,'Juan Espinoza Medrano',303),(30305,'Oropesa',303),(30306,'Pachaconas',303),(30307,'Sabaino',303),(30401,'Chalhuanca',304),(30402,'Capaya',304),(30403,'Caraybamba',304),(30404,'Chapimarca',304),(30405,'Colcabamba',304),(30406,'Cotaruse',304),(30407,'Ihuayllo',304),(30408,'Justo Apu Sahuaraura',304),(30409,'Lucre',304),(30410,'Pocohuanca',304),(30411,'San Juan de Chacña',304),(30412,'Sañayca',304),(30413,'Soraya',304),(30414,'Tapairihua',304),(30415,'Tintay',304),(30416,'Toraya',304),(30417,'Yanaca',304),(30501,'Tambobamba',305),(30502,'Cotabambas',305),(30503,'Coyllurqui',305),(30504,'Haquira',305),(30505,'Mara',305),(30506,'Challhuahuacho',305),(30601,'Chincheros',306),(30602,'Anco_Huallo',306),(30603,'Cocharcas',306),(30604,'Huaccana',306),(30605,'Ocobamba',306),(30606,'Ongoy',306),(30607,'Uranmarca',306),(30608,'Ranracancha',306),(30609,'Rocchacc',306),(30610,'El Porvenir',306),(30611,'Los Chankas',306),(30701,'Chuquibambilla',307),(30702,'Curpahuasi',307),(30703,'Gamarra',307),(30704,'Huayllati',307),(30705,'Mamara',307),(30706,'Micaela Bastidas',307),(30707,'Pataypampa',307),(30708,'Progreso',307),(30709,'San Antonio',307),(30710,'Santa Rosa',307),(30711,'Turpay',307),(30712,'Vilcabamba',307),(30713,'Virundo',307),(30714,'Curasco',307),(40101,'Arequipa',401),(40102,'Alto Selva Alegre',401),(40103,'Cayma',401),(40104,'Cerro Colorado',401),(40105,'Characato',401),(40106,'Chiguata',401),(40107,'Jacobo Hunter',401),(40108,'La Joya',401),(40109,'Mariano Melgar',401),(40110,'Miraflores',401),(40111,'Mollebaya',401),(40112,'Paucarpata',401),(40113,'Pocsi',401),(40114,'Polobaya',401),(40115,'Quequeña',401),(40116,'Sabandia',401),(40117,'Sachaca',401),(40118,'San Juan de Siguas',401),(40119,'San Juan de Tarucani',401),(40120,'Santa Isabel de Siguas',401),(40121,'Santa Rita de Siguas',401),(40122,'Socabaya',401),(40123,'Tiabaya',401),(40124,'Uchumayo',401),(40125,'Vitor',401),(40126,'Yanahuara',401),(40127,'Yarabamba',401),(40128,'Yura',401),(40129,'José Luis Bustamante Y Rivero',401),(40201,'Camaná',402),(40202,'José María Quimper',402),(40203,'Mariano Nicolás Valcárcel',402),(40204,'Mariscal Cáceres',402),(40205,'Nicolás de Pierola',402),(40206,'Ocoña',402),(40207,'Quilca',402),(40208,'Samuel Pastor',402),(40301,'Caravelí',403),(40302,'Acarí',403),(40303,'Atico',403),(40304,'Atiquipa',403),(40305,'Bella Unión',403),(40306,'Cahuacho',403),(40307,'Chala',403),(40308,'Chaparra',403),(40309,'Huanuhuanu',403),(40310,'Jaqui',403),(40311,'Lomas',403),(40312,'Quicacha',403),(40313,'Yauca',403),(40401,'Aplao',404),(40402,'Andagua',404),(40403,'Ayo',404),(40404,'Chachas',404),(40405,'Chilcaymarca',404),(40406,'Choco',404),(40407,'Huancarqui',404),(40408,'Machaguay',404),(40409,'Orcopampa',404),(40410,'Pampacolca',404),(40411,'Tipan',404),(40412,'Uñon',404),(40413,'Uraca',404),(40414,'Viraco',404),(40501,'Chivay',405),(40502,'Achoma',405),(40503,'Cabanaconde',405),(40504,'Callalli',405),(40505,'Caylloma',405),(40506,'Coporaque',405),(40507,'Huambo',405),(40508,'Huanca',405),(40509,'Ichupampa',405),(40510,'Lari',405),(40511,'Lluta',405),(40512,'Maca',405),(40513,'Madrigal',405),(40514,'San Antonio de Chuca',405),(40515,'Sibayo',405),(40516,'Tapay',405),(40517,'Tisco',405),(40518,'Tuti',405),(40519,'Yanque',405),(40520,'Majes',405),(40601,'Chuquibamba',406),(40602,'Andaray',406),(40603,'Cayarani',406),(40604,'Chichas',406),(40605,'Iray',406),(40606,'Río Grande',406),(40607,'Salamanca',406),(40608,'Yanaquihua',406),(40701,'Mollendo',407),(40702,'Cocachacra',407),(40703,'Dean Valdivia',407),(40704,'Islay',407),(40705,'Mejia',407),(40706,'Punta de Bombón',407),(40801,'Cotahuasi',408),(40802,'Alca',408),(40803,'Charcana',408),(40804,'Huaynacotas',408),(40805,'Pampamarca',408),(40806,'Puyca',408),(40807,'Quechualla',408),(40808,'Sayla',408),(40809,'Tauria',408),(40810,'Tomepampa',408),(40811,'Toro',408),(50101,'Ayacucho',501),(50102,'Acocro',501),(50103,'Acos Vinchos',501),(50104,'Carmen Alto',501),(50105,'Chiara',501),(50106,'Ocros',501),(50107,'Pacaycasa',501),(50108,'Quinua',501),(50109,'San José de Ticllas',501),(50110,'San Juan Bautista',501),(50111,'Santiago de Pischa',501),(50112,'Socos',501),(50113,'Tambillo',501),(50114,'Vinchos',501),(50115,'Jesús Nazareno',501),(50116,'Andrés Avelino Cáceres Dorregaray',501),(50201,'Cangallo',502),(50202,'Chuschi',502),(50203,'Los Morochucos',502),(50204,'María Parado de Bellido',502),(50205,'Paras',502),(50206,'Totos',502),(50301,'Sancos',503),(50302,'Carapo',503),(50303,'Sacsamarca',503),(50304,'Santiago de Lucanamarca',503),(50401,'Huanta',504),(50402,'Ayahuanco',504),(50403,'Huamanguilla',504),(50404,'Iguain',504),(50405,'Luricocha',504),(50406,'Santillana',504),(50407,'Sivia',504),(50408,'Llochegua',504),(50409,'Canayre',504),(50410,'Uchuraccay',504),(50411,'Pucacolpa',504),(50412,'Chaca',504),(50501,'San Miguel',505),(50502,'Anco',505),(50503,'Ayna',505),(50504,'Chilcas',505),(50505,'Chungui',505),(50506,'Luis Carranza',505),(50507,'Santa Rosa',505),(50508,'Tambo',505),(50509,'Samugari',505),(50510,'Anchihuay',505),(50511,'Oronccoy',505),(50601,'Puquio',506),(50602,'Aucara',506),(50603,'Cabana',506),(50604,'Carmen Salcedo',506),(50605,'Chaviña',506),(50606,'Chipao',506),(50607,'Huac-Huas',506),(50608,'Laramate',506),(50609,'Leoncio Prado',506),(50610,'Llauta',506),(50611,'Lucanas',506),(50612,'Ocaña',506),(50613,'Otoca',506),(50614,'Saisa',506),(50615,'San Cristóbal',506),(50616,'San Juan',506),(50617,'San Pedro',506),(50618,'San Pedro de Palco',506),(50619,'Sancos',506),(50620,'Santa Ana de Huaycahuacho',506),(50621,'Santa Lucia',506),(50701,'Coracora',507),(50702,'Chumpi',507),(50703,'Coronel Castañeda',507),(50704,'Pacapausa',507),(50705,'Pullo',507),(50706,'Puyusca',507),(50707,'San Francisco de Ravacayco',507),(50708,'Upahuacho',507),(50801,'Pausa',508),(50802,'Colta',508),(50803,'Corculla',508),(50804,'Lampa',508),(50805,'Marcabamba',508),(50806,'Oyolo',508),(50807,'Pararca',508),(50808,'San Javier de Alpabamba',508),(50809,'San José de Ushua',508),(50810,'Sara Sara',508),(50901,'Querobamba',509),(50902,'Belén',509),(50903,'Chalcos',509),(50904,'Chilcayoc',509),(50905,'Huacaña',509),(50906,'Morcolla',509),(50907,'Paico',509),(50908,'San Pedro de Larcay',509),(50909,'San Salvador de Quije',509),(50910,'Santiago de Paucaray',509),(50911,'Soras',509),(51001,'Huancapi',510),(51002,'Alcamenca',510),(51003,'Apongo',510),(51004,'Asquipata',510),(51005,'Canaria',510),(51006,'Cayara',510),(51007,'Colca',510),(51008,'Huamanquiquia',510),(51009,'Huancaraylla',510),(51010,'Hualla',510),(51011,'Sarhua',510),(51012,'Vilcanchos',510),(51101,'Vilcas Huaman',511),(51102,'Accomarca',511),(51103,'Carhuanca',511),(51104,'Concepción',511),(51105,'Huambalpa',511),(51106,'Independencia',511),(51107,'Saurama',511),(51108,'Vischongo',511),(60101,'Cajamarca',601),(60102,'Asunción',601),(60103,'Chetilla',601),(60104,'Cospan',601),(60105,'Encañada',601),(60106,'Jesús',601),(60107,'Llacanora',601),(60108,'Los Baños del Inca',601),(60109,'Magdalena',601),(60110,'Matara',601),(60111,'Namora',601),(60112,'San Juan',601),(60201,'Cajabamba',602),(60202,'Cachachi',602),(60203,'Condebamba',602),(60204,'Sitacocha',602),(60301,'Celendín',603),(60302,'Chumuch',603),(60303,'Cortegana',603),(60304,'Huasmin',603),(60305,'Jorge Chávez',603),(60306,'José Gálvez',603),(60307,'Miguel Iglesias',603),(60308,'Oxamarca',603),(60309,'Sorochuco',603),(60310,'Sucre',603),(60311,'Utco',603),(60312,'La Libertad de Pallan',603),(60401,'Chota',604),(60402,'Anguia',604),(60403,'Chadin',604),(60404,'Chiguirip',604),(60405,'Chimban',604),(60406,'Choropampa',604),(60407,'Cochabamba',604),(60408,'Conchan',604),(60409,'Huambos',604),(60410,'Lajas',604),(60411,'Llama',604),(60412,'Miracosta',604),(60413,'Paccha',604),(60414,'Pion',604),(60415,'Querocoto',604),(60416,'San Juan de Licupis',604),(60417,'Tacabamba',604),(60418,'Tocmoche',604),(60419,'Chalamarca',604),(60501,'Contumaza',605),(60502,'Chilete',605),(60503,'Cupisnique',605),(60504,'Guzmango',605),(60505,'San Benito',605),(60506,'Santa Cruz de Toledo',605),(60507,'Tantarica',605),(60508,'Yonan',605),(60601,'Cutervo',606),(60602,'Callayuc',606),(60603,'Choros',606),(60604,'Cujillo',606),(60605,'La Ramada',606),(60606,'Pimpingos',606),(60607,'Querocotillo',606),(60608,'San Andrés de Cutervo',606),(60609,'San Juan de Cutervo',606),(60610,'San Luis de Lucma',606),(60611,'Santa Cruz',606),(60612,'Santo Domingo de la Capilla',606),(60613,'Santo Tomas',606),(60614,'Socota',606),(60615,'Toribio Casanova',606),(60701,'Bambamarca',607),(60702,'Chugur',607),(60703,'Hualgayoc',607),(60801,'Jaén',608),(60802,'Bellavista',608),(60803,'Chontali',608),(60804,'Colasay',608),(60805,'Huabal',608),(60806,'Las Pirias',608),(60807,'Pomahuaca',608),(60808,'Pucara',608),(60809,'Sallique',608),(60810,'San Felipe',608),(60811,'San José del Alto',608),(60812,'Santa Rosa',608),(60901,'San Ignacio',609),(60902,'Chirinos',609),(60903,'Huarango',609),(60904,'La Coipa',609),(60905,'Namballe',609),(60906,'San José de Lourdes',609),(60907,'Tabaconas',609),(61001,'Pedro Gálvez',610),(61002,'Chancay',610),(61003,'Eduardo Villanueva',610),(61004,'Gregorio Pita',610),(61005,'Ichocan',610),(61006,'José Manuel Quiroz',610),(61007,'José Sabogal',610),(61101,'San Miguel',611),(61102,'Bolívar',611),(61103,'Calquis',611),(61104,'Catilluc',611),(61105,'El Prado',611),(61106,'La Florida',611),(61107,'Llapa',611),(61108,'Nanchoc',611),(61109,'Niepos',611),(61110,'San Gregorio',611),(61111,'San Silvestre de Cochan',611),(61112,'Tongod',611),(61113,'Unión Agua Blanca',611),(61201,'San Pablo',612),(61202,'San Bernardino',612),(61203,'San Luis',612),(61204,'Tumbaden',612),(61301,'Santa Cruz',613),(61302,'Andabamba',613),(61303,'Catache',613),(61304,'Chancaybaños',613),(61305,'La Esperanza',613),(61306,'Ninabamba',613),(61307,'Pulan',613),(61308,'Saucepampa',613),(61309,'Sexi',613),(61310,'Uticyacu',613),(61311,'Yauyucan',613),(70101,'Callao',701),(70102,'Bellavista',701),(70103,'Carmen de la Legua Reynoso',701),(70104,'La Perla',701),(70105,'La Punta',701),(70106,'Ventanilla',701),(70107,'Mi Perú',701),(80101,'Cusco',801),(80102,'Ccorca',801),(80103,'Poroy',801),(80104,'San Jerónimo',801),(80105,'San Sebastian',801),(80106,'Santiago',801),(80107,'Saylla',801),(80108,'Wanchaq',801),(80201,'Acomayo',802),(80202,'Acopia',802),(80203,'Acos',802),(80204,'Mosoc Llacta',802),(80205,'Pomacanchi',802),(80206,'Rondocan',802),(80207,'Sangarara',802),(80301,'Anta',803),(80302,'Ancahuasi',803),(80303,'Cachimayo',803),(80304,'Chinchaypujio',803),(80305,'Huarocondo',803),(80306,'Limatambo',803),(80307,'Mollepata',803),(80308,'Pucyura',803),(80309,'Zurite',803),(80401,'Calca',804),(80402,'Coya',804),(80403,'Lamay',804),(80404,'Lares',804),(80405,'Pisac',804),(80406,'San Salvador',804),(80407,'Taray',804),(80408,'Yanatile',804),(80501,'Yanaoca',805),(80502,'Checca',805),(80503,'Kunturkanki',805),(80504,'Langui',805),(80505,'Layo',805),(80506,'Pampamarca',805),(80507,'Quehue',805),(80508,'Tupac Amaru',805),(80601,'Sicuani',806),(80602,'Checacupe',806),(80603,'Combapata',806),(80604,'Marangani',806),(80605,'Pitumarca',806),(80606,'San Pablo',806),(80607,'San Pedro',806),(80608,'Tinta',806),(80701,'Santo Tomas',807),(80702,'Capacmarca',807),(80703,'Chamaca',807),(80704,'Colquemarca',807),(80705,'Livitaca',807),(80706,'Llusco',807),(80707,'Quiñota',807),(80708,'Velille',807),(80801,'Espinar',808),(80802,'Condoroma',808),(80803,'Coporaque',808),(80804,'Ocoruro',808),(80805,'Pallpata',808),(80806,'Pichigua',808),(80807,'Suyckutambo',808),(80808,'Alto Pichigua',808),(80901,'Santa Ana',809),(80902,'Echarate',809),(80903,'Huayopata',809),(80904,'Maranura',809),(80905,'Ocobamba',809),(80906,'Quellouno',809),(80907,'Kimbiri',809),(80908,'Santa Teresa',809),(80909,'Vilcabamba',809),(80910,'Pichari',809),(80911,'Inkawasi',809),(80912,'Villa Virgen',809),(80913,'Villa Kintiarina',809),(80914,'Megantoni',809),(81001,'Paruro',810),(81002,'Accha',810),(81003,'Ccapi',810),(81004,'Colcha',810),(81005,'Huanoquite',810),(81006,'Omachaç',810),(81007,'Paccaritambo',810),(81008,'Pillpinto',810),(81009,'Yaurisque',810),(81101,'Paucartambo',811),(81102,'Caicay',811),(81103,'Challabamba',811),(81104,'Colquepata',811),(81105,'Huancarani',811),(81106,'Kosñipata',811),(81201,'Urcos',812),(81202,'Andahuaylillas',812),(81203,'Camanti',812),(81204,'Ccarhuayo',812),(81205,'Ccatca',812),(81206,'Cusipata',812),(81207,'Huaro',812),(81208,'Lucre',812),(81209,'Marcapata',812),(81210,'Ocongate',812),(81211,'Oropesa',812),(81212,'Quiquijana',812),(81301,'Urubamba',813),(81302,'Chinchero',813),(81303,'Huayllabamba',813),(81304,'Machupicchu',813),(81305,'Maras',813),(81306,'Ollantaytambo',813),(81307,'Yucay',813),(90101,'Huancavelica',901),(90102,'Acobambilla',901),(90103,'Acoria',901),(90104,'Conayca',901),(90105,'Cuenca',901),(90106,'Huachocolpa',901),(90107,'Huayllahuara',901),(90108,'Izcuchaca',901),(90109,'Laria',901),(90110,'Manta',901),(90111,'Mariscal Cáceres',901),(90112,'Moya',901),(90113,'Nuevo Occoro',901),(90114,'Palca',901),(90115,'Pilchaca',901),(90116,'Vilca',901),(90117,'Yauli',901),(90118,'Ascensión',901),(90119,'Huando',901),(90201,'Acobamba',902),(90202,'Andabamba',902),(90203,'Anta',902),(90204,'Caja',902),(90205,'Marcas',902),(90206,'Paucara',902),(90207,'Pomacocha',902),(90208,'Rosario',902),(90301,'Lircay',903),(90302,'Anchonga',903),(90303,'Callanmarca',903),(90304,'Ccochaccasa',903),(90305,'Chincho',903),(90306,'Congalla',903),(90307,'Huanca-Huanca',903),(90308,'Huayllay Grande',903),(90309,'Julcamarca',903),(90310,'San Antonio de Antaparco',903),(90311,'Santo Tomas de Pata',903),(90312,'Secclla',903),(90401,'Castrovirreyna',904),(90402,'Arma',904),(90403,'Aurahua',904),(90404,'Capillas',904),(90405,'Chupamarca',904),(90406,'Cocas',904),(90407,'Huachos',904),(90408,'Huamatambo',904),(90409,'Mollepampa',904),(90410,'San Juan',904),(90411,'Santa Ana',904),(90412,'Tantara',904),(90413,'Ticrapo',904),(90501,'Churcampa',905),(90502,'Anco',905),(90503,'Chinchihuasi',905),(90504,'El Carmen',905),(90505,'La Merced',905),(90506,'Locroja',905),(90507,'Paucarbamba',905),(90508,'San Miguel de Mayocc',905),(90509,'San Pedro de Coris',905),(90510,'Pachamarca',905),(90511,'Cosme',905),(90601,'Huaytara',906),(90602,'Ayavi',906),(90603,'Córdova',906),(90604,'Huayacundo Arma',906),(90605,'Laramarca',906),(90606,'Ocoyo',906),(90607,'Pilpichaca',906),(90608,'Querco',906),(90609,'Quito-Arma',906),(90610,'San Antonio de Cusicancha',906),(90611,'San Francisco de Sangayaico',906),(90612,'San Isidro',906),(90613,'Santiago de Chocorvos',906),(90614,'Santiago de Quirahuara',906),(90615,'Santo Domingo de Capillas',906),(90616,'Tambo',906),(90701,'Pampas',907),(90702,'Acostambo',907),(90703,'Acraquia',907),(90704,'Ahuaycha',907),(90705,'Colcabamba',907),(90706,'Daniel Hernández',907),(90707,'Huachocolpa',907),(90709,'Huaribamba',907),(90710,'Ñahuimpuquio',907),(90711,'Pazos',907),(90713,'Quishuar',907),(90714,'Salcabamba',907),(90715,'Salcahuasi',907),(90716,'San Marcos de Rocchac',907),(90717,'Surcubamba',907),(90718,'Tintay Puncu',907),(90719,'Quichuas',907),(90720,'Andaymarca',907),(90721,'Roble',907),(90722,'Pichos',907),(90723,'Santiago de Tucuma',907),(100101,'Huanuco',1001),(100102,'Amarilis',1001),(100103,'Chinchao',1001),(100104,'Churubamba',1001),(100105,'Margos',1001),(100106,'Quisqui (Kichki)',1001),(100107,'San Francisco de Cayran',1001),(100108,'San Pedro de Chaulan',1001),(100109,'Santa María del Valle',1001),(100110,'Yarumayo',1001),(100111,'Pillco Marca',1001),(100112,'Yacus',1001),(100113,'San Pablo de Pillao',1001),(100201,'Ambo',1002),(100202,'Cayna',1002),(100203,'Colpas',1002),(100204,'Conchamarca',1002),(100205,'Huacar',1002),(100206,'San Francisco',1002),(100207,'San Rafael',1002),(100208,'Tomay Kichwa',1002),(100301,'La Unión',1003),(100307,'Chuquis',1003),(100311,'Marías',1003),(100313,'Pachas',1003),(100316,'Quivilla',1003),(100317,'Ripan',1003),(100321,'Shunqui',1003),(100322,'Sillapata',1003),(100323,'Yanas',1003),(100401,'Huacaybamba',1004),(100402,'Canchabamba',1004),(100403,'Cochabamba',1004),(100404,'Pinra',1004),(100501,'Llata',1005),(100502,'Arancay',1005),(100503,'Chavín de Pariarca',1005),(100504,'Jacas Grande',1005),(100505,'Jircan',1005),(100506,'Miraflores',1005),(100507,'Monzón',1005),(100508,'Punchao',1005),(100509,'Puños',1005),(100510,'Singa',1005),(100511,'Tantamayo',1005),(100601,'Rupa-Rupa',1006),(100602,'Daniel Alomía Robles',1006),(100603,'Hermílio Valdizan',1006),(100604,'José Crespo y Castillo',1006),(100605,'Luyando',1006),(100606,'Mariano Damaso Beraun',1006),(100607,'Pucayacu',1006),(100608,'Castillo Grande',1006),(100609,'Pueblo Nuevo',1006),(100610,'Santo Domingo de Anda',1006),(100701,'Huacrachuco',1007),(100702,'Cholon',1007),(100703,'San Buenaventura',1007),(100704,'La Morada',1007),(100705,'Santa Rosa de Alto Yanajanca',1007),(100801,'Panao',1008),(100802,'Chaglla',1008),(100803,'Molino',1008),(100804,'Umari',1008),(100901,'Puerto Inca',1009),(100902,'Codo del Pozuzo',1009),(100903,'Honoria',1009),(100904,'Tournavista',1009),(100905,'Yuyapichis',1009),(101001,'Jesús',1010),(101002,'Baños',1010),(101003,'Jivia',1010),(101004,'Queropalca',1010),(101005,'Rondos',1010),(101006,'San Francisco de Asís',1010),(101007,'San Miguel de Cauri',1010),(101101,'Chavinillo',1011),(101102,'Cahuac',1011),(101103,'Chacabamba',1011),(101104,'Aparicio Pomares',1011),(101105,'Jacas Chico',1011),(101106,'Obas',1011),(101107,'Pampamarca',1011),(101108,'Choras',1011),(110101,'Ica',1101),(110102,'La Tinguiña',1101),(110103,'Los Aquijes',1101),(110104,'Ocucaje',1101),(110105,'Pachacutec',1101),(110106,'Parcona',1101),(110107,'Pueblo Nuevo',1101),(110108,'Salas',1101),(110109,'San José de Los Molinos',1101),(110110,'San Juan Bautista',1101),(110111,'Santiago',1101),(110112,'Subtanjalla',1101),(110113,'Tate',1101),(110114,'Yauca del Rosario',1101),(110201,'Chincha Alta',1102),(110202,'Alto Laran',1102),(110203,'Chavin',1102),(110204,'Chincha Baja',1102),(110205,'El Carmen',1102),(110206,'Grocio Prado',1102),(110207,'Pueblo Nuevo',1102),(110208,'San Juan de Yanac',1102),(110209,'San Pedro de Huacarpana',1102),(110210,'Sunampe',1102),(110211,'Tambo de Mora',1102),(110301,'Nasca',1103),(110302,'Changuillo',1103),(110303,'El Ingenio',1103),(110304,'Marcona',1103),(110305,'Vista Alegre',1103),(110401,'Palpa',1104),(110402,'Llipata',1104),(110403,'Río Grande',1104),(110404,'Santa Cruz',1104),(110405,'Tibillo',1104),(110501,'Pisco',1105),(110502,'Huancano',1105),(110503,'Humay',1105),(110504,'Independencia',1105),(110505,'Paracas',1105),(110506,'San Andrés',1105),(110507,'San Clemente',1105),(110508,'Tupac Amaru Inca',1105),(120101,'Huancayo',1201),(120104,'Carhuacallanga',1201),(120105,'Chacapampa',1201),(120106,'Chicche',1201),(120107,'Chilca',1201),(120108,'Chongos Alto',1201),(120111,'Chupuro',1201),(120112,'Colca',1201),(120113,'Cullhuas',1201),(120114,'El Tambo',1201),(120116,'Huacrapuquio',1201),(120117,'Hualhuas',1201),(120119,'Huancan',1201),(120120,'Huasicancha',1201),(120121,'Huayucachi',1201),(120122,'Ingenio',1201),(120124,'Pariahuanca',1201),(120125,'Pilcomayo',1201),(120126,'Pucara',1201),(120127,'Quichuay',1201),(120128,'Quilcas',1201),(120129,'San Agustín',1201),(120130,'San Jerónimo de Tunan',1201),(120132,'Saño',1201),(120133,'Sapallanga',1201),(120134,'Sicaya',1201),(120135,'Santo Domingo de Acobamba',1201),(120136,'Viques',1201),(120201,'Concepción',1202),(120202,'Aco',1202),(120203,'Andamarca',1202),(120204,'Chambara',1202),(120205,'Cochas',1202),(120206,'Comas',1202),(120207,'Heroínas Toledo',1202),(120208,'Manzanares',1202),(120209,'Mariscal Castilla',1202),(120210,'Matahuasi',1202),(120211,'Mito',1202),(120212,'Nueve de Julio',1202),(120213,'Orcotuna',1202),(120214,'San José de Quero',1202),(120215,'Santa Rosa de Ocopa',1202),(120301,'Chanchamayo',1203),(120302,'Perene',1203),(120303,'Pichanaqui',1203),(120304,'San Luis de Shuaro',1203),(120305,'San Ramón',1203),(120306,'Vitoc',1203),(120401,'Jauja',1204),(120402,'Acolla',1204),(120403,'Apata',1204),(120404,'Ataura',1204),(120405,'Canchayllo',1204),(120406,'Curicaca',1204),(120407,'El Mantaro',1204),(120408,'Huamali',1204),(120409,'Huaripampa',1204),(120410,'Huertas',1204),(120411,'Janjaillo',1204),(120412,'Julcán',1204),(120413,'Leonor Ordóñez',1204),(120414,'Llocllapampa',1204),(120415,'Marco',1204),(120416,'Masma',1204),(120417,'Masma Chicche',1204),(120418,'Molinos',1204),(120419,'Monobamba',1204),(120420,'Muqui',1204),(120421,'Muquiyauyo',1204),(120422,'Paca',1204),(120423,'Paccha',1204),(120424,'Pancan',1204),(120425,'Parco',1204),(120426,'Pomacancha',1204),(120427,'Ricran',1204),(120428,'San Lorenzo',1204),(120429,'San Pedro de Chunan',1204),(120430,'Sausa',1204),(120431,'Sincos',1204),(120432,'Tunan Marca',1204),(120433,'Yauli',1204),(120434,'Yauyos',1204),(120501,'Junin',1205),(120502,'Carhuamayo',1205),(120503,'Ondores',1205),(120504,'Ulcumayo',1205),(120601,'Satipo',1206),(120602,'Coviriali',1206),(120603,'Llaylla',1206),(120604,'Mazamari',1206),(120605,'Pampa Hermosa',1206),(120606,'Pangoa',1206),(120607,'Río Negro',1206),(120608,'Río Tambo',1206),(120609,'Vizcatan del Ene',1206),(120701,'Tarma',1207),(120702,'Acobamba',1207),(120703,'Huaricolca',1207),(120704,'Huasahuasi',1207),(120705,'La Unión',1207),(120706,'Palca',1207),(120707,'Palcamayo',1207),(120708,'San Pedro de Cajas',1207),(120709,'Tapo',1207),(120801,'La Oroya',1208),(120802,'Chacapalpa',1208),(120803,'Huay-Huay',1208),(120804,'Marcapomacocha',1208),(120805,'Morococha',1208),(120806,'Paccha',1208),(120807,'Santa Bárbara de Carhuacayan',1208),(120808,'Santa Rosa de Sacco',1208),(120809,'Suitucancha',1208),(120810,'Yauli',1208),(120901,'Chupaca',1209),(120902,'Ahuac',1209),(120903,'Chongos Bajo',1209),(120904,'Huachac',1209),(120905,'Huamancaca Chico',1209),(120906,'San Juan de Iscos',1209),(120907,'San Juan de Jarpa',1209),(120908,'Tres de Diciembre',1209),(120909,'Yanacancha',1209),(130101,'Trujillo',1301),(130102,'El Porvenir',1301),(130103,'Florencia de Mora',1301),(130104,'Huanchaco',1301),(130105,'La Esperanza',1301),(130106,'Laredo',1301),(130107,'Moche',1301),(130108,'Poroto',1301),(130109,'Salaverry',1301),(130110,'Simbal',1301),(130111,'Victor Larco Herrera',1301),(130201,'Ascope',1302),(130202,'Chicama',1302),(130203,'Chocope',1302),(130204,'Magdalena de Cao',1302),(130205,'Paijan',1302),(130206,'Rázuri',1302),(130207,'Santiago de Cao',1302),(130208,'Casa Grande',1302),(130301,'Bolívar',1303),(130302,'Bambamarca',1303),(130303,'Condormarca',1303),(130304,'Longotea',1303),(130305,'Uchumarca',1303),(130306,'Ucuncha',1303),(130401,'Chepen',1304),(130402,'Pacanga',1304),(130403,'Pueblo Nuevo',1304),(130501,'Julcan',1305),(130502,'Calamarca',1305),(130503,'Carabamba',1305),(130504,'Huaso',1305),(130601,'Otuzco',1306),(130602,'Agallpampa',1306),(130604,'Charat',1306),(130605,'Huaranchal',1306),(130606,'La Cuesta',1306),(130608,'Mache',1306),(130610,'Paranday',1306),(130611,'Salpo',1306),(130613,'Sinsicap',1306),(130614,'Usquil',1306),(130701,'San Pedro de Lloc',1307),(130702,'Guadalupe',1307),(130703,'Jequetepeque',1307),(130704,'Pacasmayo',1307),(130705,'San José',1307),(130801,'Tayabamba',1308),(130802,'Buldibuyo',1308),(130803,'Chillia',1308),(130804,'Huancaspata',1308),(130805,'Huaylillas',1308),(130806,'Huayo',1308),(130807,'Ongon',1308),(130808,'Parcoy',1308),(130809,'Pataz',1308),(130810,'Pias',1308),(130811,'Santiago de Challas',1308),(130812,'Taurija',1308),(130813,'Urpay',1308),(130901,'Huamachuco',1309),(130902,'Chugay',1309),(130903,'Cochorco',1309),(130904,'Curgos',1309),(130905,'Marcabal',1309),(130906,'Sanagoran',1309),(130907,'Sarin',1309),(130908,'Sartimbamba',1309),(131001,'Santiago de Chuco',1310),(131002,'Angasmarca',1310),(131003,'Cachicadan',1310),(131004,'Mollebamba',1310),(131005,'Mollepata',1310),(131006,'Quiruvilca',1310),(131007,'Santa Cruz de Chuca',1310),(131008,'Sitabamba',1310),(131101,'Cascas',1311),(131102,'Lucma',1311),(131103,'Marmot',1311),(131104,'Sayapullo',1311),(131201,'Viru',1312),(131202,'Chao',1312),(131203,'Guadalupito',1312),(140101,'Chiclayo',1401),(140102,'Chongoyape',1401),(140103,'Eten',1401),(140104,'Eten Puerto',1401),(140105,'José Leonardo Ortiz',1401),(140106,'La Victoria',1401),(140107,'Lagunas',1401),(140108,'Monsefu',1401),(140109,'Nueva Arica',1401),(140110,'Oyotun',1401),(140111,'Picsi',1401),(140112,'Pimentel',1401),(140113,'Reque',1401),(140114,'Santa Rosa',1401),(140115,'Saña',1401),(140116,'Cayalti',1401),(140117,'Patapo',1401),(140118,'Pomalca',1401),(140119,'Pucala',1401),(140120,'Tuman',1401),(140201,'Ferreñafe',1402),(140202,'Cañaris',1402),(140203,'Incahuasi',1402),(140204,'Manuel Antonio Mesones Muro',1402),(140205,'Pitipo',1402),(140206,'Pueblo Nuevo',1402),(140301,'Lambayeque',1403),(140302,'Chochope',1403),(140303,'Illimo',1403),(140304,'Jayanca',1403),(140305,'Mochumi',1403),(140306,'Morrope',1403),(140307,'Motupe',1403),(140308,'Olmos',1403),(140309,'Pacora',1403),(140310,'Salas',1403),(140311,'San José',1403),(140312,'Tucume',1403),(150101,'Lima',1501),(150102,'Ancón',1501),(150103,'Ate',1501),(150104,'Barranco',1501),(150105,'Breña',1501),(150106,'Carabayllo',1501),(150107,'Chaclacayo',1501),(150108,'Chorrillos',1501),(150109,'Cieneguilla',1501),(150110,'Comas',1501),(150111,'El Agustino',1501),(150112,'Independencia',1501),(150113,'Jesús María',1501),(150114,'La Molina',1501),(150115,'La Victoria',1501),(150116,'Lince',1501),(150117,'Los Olivos',1501),(150118,'Lurigancho',1501),(150119,'Lurin',1501),(150120,'Magdalena del Mar',1501),(150121,'Pueblo Libre',1501),(150122,'Miraflores',1501),(150123,'Pachacamac',1501),(150124,'Pucusana',1501),(150125,'Puente Piedra',1501),(150126,'Punta Hermosa',1501),(150127,'Punta Negra',1501),(150128,'Rímac',1501),(150129,'San Bartolo',1501),(150130,'San Borja',1501),(150131,'San Isidro',1501),(150132,'San Juan de Lurigancho',1501),(150133,'San Juan de Miraflores',1501),(150134,'San Luis',1501),(150135,'San Martín de Porres',1501),(150136,'San Miguel',1501),(150137,'Santa Anita',1501),(150138,'Santa María del Mar',1501),(150139,'Santa Rosa',1501),(150140,'Santiago de Surco',1501),(150141,'Surquillo',1501),(150142,'Villa El Salvador',1501),(150143,'Villa María del Triunfo',1501),(150201,'Barranca',1502),(150202,'Paramonga',1502),(150203,'Pativilca',1502),(150204,'Supe',1502),(150205,'Supe Puerto',1502),(150301,'Cajatambo',1503),(150302,'Copa',1503),(150303,'Gorgor',1503),(150304,'Huancapon',1503),(150305,'Manas',1503),(150401,'Canta',1504),(150402,'Arahuay',1504),(150403,'Huamantanga',1504),(150404,'Huaros',1504),(150405,'Lachaqui',1504),(150406,'San Buenaventura',1504),(150407,'Santa Rosa de Quives',1504),(150501,'San Vicente de Cañete',1505),(150502,'Asia',1505),(150503,'Calango',1505),(150504,'Cerro Azul',1505),(150505,'Chilca',1505),(150506,'Coayllo',1505),(150507,'Imperial',1505),(150508,'Lunahuana',1505),(150509,'Mala',1505),(150510,'Nuevo Imperial',1505),(150511,'Pacaran',1505),(150512,'Quilmana',1505),(150513,'San Antonio',1505),(150514,'San Luis',1505),(150515,'Santa Cruz de Flores',1505),(150516,'Zúñiga',1505),(150601,'Huaral',1506),(150602,'Atavillos Alto',1506),(150603,'Atavillos Bajo',1506),(150604,'Aucallama',1506),(150605,'Chancay',1506),(150606,'Ihuari',1506),(150607,'Lampian',1506),(150608,'Pacaraos',1506),(150609,'San Miguel de Acos',1506),(150610,'Santa Cruz de Andamarca',1506),(150611,'Sumbilca',1506),(150612,'Veintisiete de Noviembre',1506),(150701,'Matucana',1507),(150702,'Antioquia',1507),(150703,'Callahuanca',1507),(150704,'Carampoma',1507),(150705,'Chicla',1507),(150706,'Cuenca',1507),(150707,'Huachupampa',1507),(150708,'Huanza',1507),(150709,'Huarochiri',1507),(150710,'Lahuaytambo',1507),(150711,'Langa',1507),(150712,'Laraos',1507),(150713,'Mariatana',1507),(150714,'Ricardo Palma',1507),(150715,'San Andrés de Tupicocha',1507),(150716,'San Antonio',1507),(150717,'San Bartolomé',1507),(150718,'San Damian',1507),(150719,'San Juan de Iris',1507),(150720,'San Juan de Tantaranche',1507),(150721,'San Lorenzo de Quinti',1507),(150722,'San Mateo',1507),(150723,'San Mateo de Otao',1507),(150724,'San Pedro de Casta',1507),(150725,'San Pedro de Huancayre',1507),(150726,'Sangallaya',1507),(150727,'Santa Cruz de Cocachacra',1507),(150728,'Santa Eulalia',1507),(150729,'Santiago de Anchucaya',1507),(150730,'Santiago de Tuna',1507),(150731,'Santo Domingo de Los Olleros',1507),(150732,'Surco',1507),(150801,'Huacho',1508),(150802,'Ambar',1508),(150803,'Caleta de Carquin',1508),(150804,'Checras',1508),(150805,'Hualmay',1508),(150806,'Huaura',1508),(150807,'Leoncio Prado',1508),(150808,'Paccho',1508),(150809,'Santa Leonor',1508),(150810,'Santa María',1508),(150811,'Sayan',1508),(150812,'Vegueta',1508),(150901,'Oyon',1509),(150902,'Andajes',1509),(150903,'Caujul',1509),(150904,'Cochamarca',1509),(150905,'Navan',1509),(150906,'Pachangara',1509),(151001,'Yauyos',1510),(151002,'Alis',1510),(151003,'Allauca',1510),(151004,'Ayaviri',1510),(151005,'Azángaro',1510),(151006,'Cacra',1510),(151007,'Carania',1510),(151008,'Catahuasi',1510),(151009,'Chocos',1510),(151010,'Cochas',1510),(151011,'Colonia',1510),(151012,'Hongos',1510),(151013,'Huampara',1510),(151014,'Huancaya',1510),(151015,'Huangascar',1510),(151016,'Huantan',1510),(151017,'Huañec',1510),(151018,'Laraos',1510),(151019,'Lincha',1510),(151020,'Madean',1510),(151021,'Miraflores',1510),(151022,'Omas',1510),(151023,'Putinza',1510),(151024,'Quinches',1510),(151025,'Quinocay',1510),(151026,'San Joaquín',1510),(151027,'San Pedro de Pilas',1510),(151028,'Tanta',1510),(151029,'Tauripampa',1510),(151030,'Tomas',1510),(151031,'Tupe',1510),(151032,'Viñac',1510),(151033,'Vitis',1510),(160101,'Iquitos',1601),(160102,'Alto Nanay',1601),(160103,'Fernando Lores',1601),(160104,'Indiana',1601),(160105,'Las Amazonas',1601),(160106,'Mazan',1601),(160107,'Napo',1601),(160108,'Punchana',1601),(160110,'Torres Causana',1601),(160112,'Belén',1601),(160113,'San Juan Bautista',1601),(160201,'Yurimaguas',1602),(160202,'Balsapuerto',1602),(160205,'Jeberos',1602),(160206,'Lagunas',1602),(160210,'Santa Cruz',1602),(160211,'Teniente Cesar López Rojas',1602),(160301,'Nauta',1603),(160302,'Parinari',1603),(160303,'Tigre',1603),(160304,'Trompeteros',1603),(160305,'Urarinas',1603),(160401,'Ramón Castilla',1604),(160402,'Pebas',1604),(160403,'Yavari',1604),(160404,'San Pablo',1604),(160501,'Requena',1605),(160502,'Alto Tapiche',1605),(160503,'Capelo',1605),(160504,'Emilio San Martín',1605),(160505,'Maquia',1605),(160506,'Puinahua',1605),(160507,'Saquena',1605),(160508,'Soplin',1605),(160509,'Tapiche',1605),(160510,'Jenaro Herrera',1605),(160511,'Yaquerana',1605),(160601,'Contamana',1606),(160602,'Inahuaya',1606),(160603,'Padre Márquez',1606),(160604,'Pampa Hermosa',1606),(160605,'Sarayacu',1606),(160606,'Vargas Guerra',1606),(160701,'Barranca',1607),(160702,'Cahuapanas',1607),(160703,'Manseriche',1607),(160704,'Morona',1607),(160705,'Pastaza',1607),(160706,'Andoas',1607),(160801,'Putumayo',1608),(160802,'Rosa Panduro',1608),(160803,'Teniente Manuel Clavero',1608),(160804,'Yaguas',1608),(170101,'Tambopata',1701),(170102,'Inambari',1701),(170103,'Las Piedras',1701),(170104,'Laberinto',1701),(170201,'Manu',1702),(170202,'Fitzcarrald',1702),(170203,'Madre de Dios',1702),(170204,'Huepetuhe',1702),(170301,'Iñapari',1703),(170302,'Iberia',1703),(170303,'Tahuamanu',1703),(180101,'Moquegua',1801),(180102,'Carumas',1801),(180103,'Cuchumbaya',1801),(180104,'Samegua',1801),(180105,'San Cristóbal',1801),(180106,'Torata',1801),(180201,'Omate',1802),(180202,'Chojata',1802),(180203,'Coalaque',1802),(180204,'Ichuña',1802),(180205,'La Capilla',1802),(180206,'Lloque',1802),(180207,'Matalaque',1802),(180208,'Puquina',1802),(180209,'Quinistaquillas',1802),(180210,'Ubinas',1802),(180211,'Yunga',1802),(180301,'Ilo',1803),(180302,'El Algarrobal',1803),(180303,'Pacocha',1803),(190101,'Chaupimarca',1901),(190102,'Huachon',1901),(190103,'Huariaca',1901),(190104,'Huayllay',1901),(190105,'Ninacaca',1901),(190106,'Pallanchacra',1901),(190107,'Paucartambo',1901),(190108,'San Francisco de Asís de Yarusyacan',1901),(190109,'Simon Bolívar',1901),(190110,'Ticlacayan',1901),(190111,'Tinyahuarco',1901),(190112,'Vicco',1901),(190113,'Yanacancha',1901),(190201,'Yanahuanca',1902),(190202,'Chacayan',1902),(190203,'Goyllarisquizga',1902),(190204,'Paucar',1902),(190205,'San Pedro de Pillao',1902),(190206,'Santa Ana de Tusi',1902),(190207,'Tapuc',1902),(190208,'Vilcabamba',1902),(190301,'Oxapampa',1903),(190302,'Chontabamba',1903),(190303,'Huancabamba',1903),(190304,'Palcazu',1903),(190305,'Pozuzo',1903),(190306,'Puerto Bermúdez',1903),(190307,'Villa Rica',1903),(190308,'Constitución',1903),(200101,'Piura',2001),(200104,'Castilla',2001),(200105,'Catacaos',2001),(200107,'Cura Mori',2001),(200108,'El Tallan',2001),(200109,'La Arena',2001),(200110,'La Unión',2001),(200111,'Las Lomas',2001),(200114,'Tambo Grande',2001),(200115,'Veintiseis de Octubre',2001),(200201,'Ayabaca',2002),(200202,'Frias',2002),(200203,'Jilili',2002),(200204,'Lagunas',2002),(200205,'Montero',2002),(200206,'Pacaipampa',2002),(200207,'Paimas',2002),(200208,'Sapillica',2002),(200209,'Sicchez',2002),(200210,'Suyo',2002),(200301,'Huancabamba',2003),(200302,'Canchaque',2003),(200303,'El Carmen de la Frontera',2003),(200304,'Huarmaca',2003),(200305,'Lalaquiz',2003),(200306,'San Miguel de El Faique',2003),(200307,'Sondor',2003),(200308,'Sondorillo',2003),(200401,'Chulucanas',2004),(200402,'Buenos Aires',2004),(200403,'Chalaco',2004),(200404,'La Matanza',2004),(200405,'Morropon',2004),(200406,'Salitral',2004),(200407,'San Juan de Bigote',2004),(200408,'Santa Catalina de Mossa',2004),(200409,'Santo Domingo',2004),(200410,'Yamango',2004),(200501,'Paita',2005),(200502,'Amotape',2005),(200503,'Arenal',2005),(200504,'Colan',2005),(200505,'La Huaca',2005),(200506,'Tamarindo',2005),(200507,'Vichayal',2005),(200601,'Sullana',2006),(200602,'Bellavista',2006),(200603,'Ignacio Escudero',2006),(200604,'Lancones',2006),(200605,'Marcavelica',2006),(200606,'Miguel Checa',2006),(200607,'Querecotillo',2006),(200608,'Salitral',2006),(200701,'Pariñas',2007),(200702,'El Alto',2007),(200703,'La Brea',2007),(200704,'Lobitos',2007),(200705,'Los Organos',2007),(200706,'Mancora',2007),(200801,'Sechura',2008),(200802,'Bellavista de la Unión',2008),(200803,'Bernal',2008),(200804,'Cristo Nos Valga',2008),(200805,'Vice',2008),(200806,'Rinconada Llicuar',2008),(210101,'Puno',2101),(210102,'Acora',2101),(210103,'Amantani',2101),(210104,'Atuncolla',2101),(210105,'Capachica',2101),(210106,'Chucuito',2101),(210107,'Coata',2101),(210108,'Huata',2101),(210109,'Mañazo',2101),(210110,'Paucarcolla',2101),(210111,'Pichacani',2101),(210112,'Plateria',2101),(210113,'San Antonio',2101),(210114,'Tiquillaca',2101),(210115,'Vilque',2101),(210201,'Azángaro',2102),(210202,'Achaya',2102),(210203,'Arapa',2102),(210204,'Asillo',2102),(210205,'Caminaca',2102),(210206,'Chupa',2102),(210207,'José Domingo Choquehuanca',2102),(210208,'Muñani',2102),(210209,'Potoni',2102),(210210,'Saman',2102),(210211,'San Anton',2102),(210212,'San José',2102),(210213,'San Juan de Salinas',2102),(210214,'Santiago de Pupuja',2102),(210215,'Tirapata',2102),(210301,'Macusani',2103),(210302,'Ajoyani',2103),(210303,'Ayapata',2103),(210304,'Coasa',2103),(210305,'Corani',2103),(210306,'Crucero',2103),(210307,'Ituata',2103),(210308,'Ollachea',2103),(210309,'San Gaban',2103),(210310,'Usicayos',2103),(210401,'Juli',2104),(210402,'Desaguadero',2104),(210403,'Huacullani',2104),(210404,'Kelluyo',2104),(210405,'Pisacoma',2104),(210406,'Pomata',2104),(210407,'Zepita',2104),(210501,'Ilave',2105),(210502,'Capazo',2105),(210503,'Pilcuyo',2105),(210504,'Santa Rosa',2105),(210505,'Conduriri',2105),(210601,'Huancane',2106),(210602,'Cojata',2106),(210603,'Huatasani',2106),(210604,'Inchupalla',2106),(210605,'Pusi',2106),(210606,'Rosaspata',2106),(210607,'Taraco',2106),(210608,'Vilque Chico',2106),(210701,'Lampa',2107),(210702,'Cabanilla',2107),(210703,'Calapuja',2107),(210704,'Nicasio',2107),(210705,'Ocuviri',2107),(210706,'Palca',2107),(210707,'Paratia',2107),(210708,'Pucara',2107),(210709,'Santa Lucia',2107),(210710,'Vilavila',2107),(210801,'Ayaviri',2108),(210802,'Antauta',2108),(210803,'Cupi',2108),(210804,'Llalli',2108),(210805,'Macari',2108),(210806,'Nuñoa',2108),(210807,'Orurillo',2108),(210808,'Santa Rosa',2108),(210809,'Umachiri',2108),(210901,'Moho',2109),(210902,'Conima',2109),(210903,'Huayrapata',2109),(210904,'Tilali',2109),(211001,'Putina',2110),(211002,'Ananea',2110),(211003,'Pedro Vilca Apaza',2110),(211004,'Quilcapuncu',2110),(211005,'Sina',2110),(211101,'Juliaca',2111),(211102,'Cabana',2111),(211103,'Cabanillas',2111),(211104,'Caracoto',2111),(211105,'San Miguel',2111),(211201,'Sandia',2112),(211202,'Cuyocuyo',2112),(211203,'Limbani',2112),(211204,'Patambuco',2112),(211205,'Phara',2112),(211206,'Quiaca',2112),(211207,'San Juan del Oro',2112),(211208,'Yanahuaya',2112),(211209,'Alto Inambari',2112),(211210,'San Pedro de Putina Punco',2112),(211301,'Yunguyo',2113),(211302,'Anapia',2113),(211303,'Copani',2113),(211304,'Cuturapi',2113),(211305,'Ollaraya',2113),(211306,'Tinicachi',2113),(211307,'Unicachi',2113),(220101,'Moyobamba',2201),(220102,'Calzada',2201),(220103,'Habana',2201),(220104,'Jepelacio',2201),(220105,'Soritor',2201),(220106,'Yantalo',2201),(220201,'Bellavista',2202),(220202,'Alto Biavo',2202),(220203,'Bajo Biavo',2202),(220204,'Huallaga',2202),(220205,'San Pablo',2202),(220206,'San Rafael',2202),(220301,'San José de Sisa',2203),(220302,'Agua Blanca',2203),(220303,'San Martín',2203),(220304,'Santa Rosa',2203),(220305,'Shatoja',2203),(220401,'Saposoa',2204),(220402,'Alto Saposoa',2204),(220403,'El Eslabón',2204),(220404,'Piscoyacu',2204),(220405,'Sacanche',2204),(220406,'Tingo de Saposoa',2204),(220501,'Lamas',2205),(220502,'Alonso de Alvarado',2205),(220503,'Barranquita',2205),(220504,'Caynarachi',2205),(220505,'Cuñumbuqui',2205),(220506,'Pinto Recodo',2205),(220507,'Rumisapa',2205),(220508,'San Roque de Cumbaza',2205),(220509,'Shanao',2205),(220510,'Tabalosos',2205),(220511,'Zapatero',2205),(220601,'Juanjuí',2206),(220602,'Campanilla',2206),(220603,'Huicungo',2206),(220604,'Pachiza',2206),(220605,'Pajarillo',2206),(220701,'Picota',2207),(220702,'Buenos Aires',2207),(220703,'Caspisapa',2207),(220704,'Pilluana',2207),(220705,'Pucacaca',2207),(220706,'San Cristóbal',2207),(220707,'San Hilarión',2207),(220708,'Shamboyacu',2207),(220709,'Tingo de Ponasa',2207),(220710,'Tres Unidos',2207),(220801,'Rioja',2208),(220802,'Awajun',2208),(220803,'Elías Soplin Vargas',2208),(220804,'Nueva Cajamarca',2208),(220805,'Pardo Miguel',2208),(220806,'Posic',2208),(220807,'San Fernando',2208),(220808,'Yorongos',2208),(220809,'Yuracyacu',2208),(220901,'Tarapoto',2209),(220902,'Alberto Leveau',2209),(220903,'Cacatachi',2209),(220904,'Chazuta',2209),(220905,'Chipurana',2209),(220906,'El Porvenir',2209),(220907,'Huimbayoc',2209),(220908,'Juan Guerra',2209),(220909,'La Banda de Shilcayo',2209),(220910,'Morales',2209),(220911,'Papaplaya',2209),(220912,'San Antonio',2209),(220913,'Sauce',2209),(220914,'Shapaja',2209),(221001,'Tocache',2210),(221002,'Nuevo Progreso',2210),(221003,'Polvora',2210),(221004,'Shunte',2210),(221005,'Uchiza',2210),(230101,'Tacna',2301),(230102,'Alto de la Alianza',2301),(230103,'Calana',2301),(230104,'Ciudad Nueva',2301),(230105,'Inclan',2301),(230106,'Pachia',2301),(230107,'Palca',2301),(230108,'Pocollay',2301),(230109,'Sama',2301),(230110,'Coronel Gregorio Albarracín Lanchipa',2301),(230111,'La Yarada los Palos',2301),(230201,'Candarave',2302),(230202,'Cairani',2302),(230203,'Camilaca',2302),(230204,'Curibaya',2302),(230205,'Huanuara',2302),(230206,'Quilahuani',2302),(230301,'Locumba',2303),(230302,'Ilabaya',2303),(230303,'Ite',2303),(230401,'Tarata',2304),(230402,'Héroes Albarracín',2304),(230403,'Estique',2304),(230404,'Estique-Pampa',2304),(230405,'Sitajara',2304),(230406,'Susapaya',2304),(230407,'Tarucachi',2304),(230408,'Ticaco',2304),(240101,'Tumbes',2401),(240102,'Corrales',2401),(240103,'La Cruz',2401),(240104,'Pampas de Hospital',2401),(240105,'San Jacinto',2401),(240106,'San Juan de la Virgen',2401),(240201,'Zorritos',2402),(240202,'Casitas',2402),(240203,'Canoas de Punta Sal',2402),(240301,'Zarumilla',2403),(240302,'Aguas Verdes',2403),(240303,'Matapalo',2403),(240304,'Papayal',2403),(250101,'Calleria',2501),(250102,'Campoverde',2501),(250103,'Iparia',2501),(250104,'Masisea',2501),(250105,'Yarinacocha',2501),(250106,'Nueva Requena',2501),(250107,'Manantay',2501),(250201,'Raymondi',2502),(250202,'Sepahua',2502),(250203,'Tahuania',2502),(250204,'Yurua',2502),(250301,'Padre Abad',2503),(250302,'Irazola',2503),(250303,'Curimana',2503),(250304,'Neshuya',2503),(250305,'Alexander Von Humboldt',2503),(250401,'Purus',2504);
/*!40000 ALTER TABLE `DISTRITO` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `EMPLEADO`
--

DROP TABLE IF EXISTS `EMPLEADO`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `EMPLEADO` (
  `id_empleado` int NOT NULL AUTO_INCREMENT,
  `nombres` varchar(100) DEFAULT NULL,
  `apellidos` varchar(100) DEFAULT NULL,
  `fecha_nacimiento` date DEFAULT NULL,
  `documento_identidad` varchar(20) DEFAULT NULL,
  `sexo` varchar(20) DEFAULT NULL,
  `estado` varchar(20) DEFAULT NULL,
  `id_usuario` int DEFAULT NULL,
  `id_rol` int DEFAULT NULL,
  `id_distrito` int DEFAULT NULL,
  `id_especialidad` int DEFAULT NULL,
  PRIMARY KEY (`id_empleado`),
  UNIQUE KEY `documento_identidad` (`documento_identidad`),
  KEY `id_usuario` (`id_usuario`),
  KEY `id_rol` (`id_rol`),
  KEY `id_distrito` (`id_distrito`),
  KEY `id_especialidad` (`id_especialidad`),
  CONSTRAINT `EMPLEADO_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `USUARIO` (`id_usuario`),
  CONSTRAINT `EMPLEADO_ibfk_2` FOREIGN KEY (`id_rol`) REFERENCES `ROL` (`id_rol`),
  CONSTRAINT `EMPLEADO_ibfk_3` FOREIGN KEY (`id_distrito`) REFERENCES `DISTRITO` (`id_distrito`),
  CONSTRAINT `EMPLEADO_ibfk_4` FOREIGN KEY (`id_especialidad`) REFERENCES `ESPECIALIDAD` (`id_especialidad`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `EMPLEADO`
--

LOCK TABLES `EMPLEADO` WRITE;
/*!40000 ALTER TABLE `EMPLEADO` DISABLE KEYS */;
INSERT INTO `EMPLEADO` VALUES (1,'Karelly','Garcia Inoñan',NULL,'72658837','Femenino','Activo',3,1,140312,1),(2,'Mauricio','Chero',NULL,'73109345','M','activo',1,2,140101,14),(3,'Jose','Fiestas',NULL,'78905642','Masculino','Activo',2,3,130504,2),(4,'María','Salazar Rivas',NULL,'75648921','Femenino','Activo',6,2,140105,4),(5,'Juan','Cáceres Torres',NULL,'74859632','M','activo',7,3,20903,4),(6,'Carlos','Pérez Mendoza',NULL,'72563148','Masculino','Activo',8,4,140201,1),(7,'Ana','Gómez Huamán',NULL,'73924856','Femenino','Activo',9,5,131101,2),(17,'Jasson','Puican (Administrador)',NULL,'72780865','Masculino','ACTIVO',21,1,140312,1),(18,'Manuel','Marrtt',NULL,'98442233','M','activo',27,2,150403,6),(19,'Kata','Moria',NULL,'99993392','Masculino','activo',28,2,150809,8),(20,'Carlos','Montoyo','2007-10-10','72838223','Masculino','activo',29,5,130704,NULL);
/*!40000 ALTER TABLE `EMPLEADO` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ESPECIALIDAD`
--

DROP TABLE IF EXISTS `ESPECIALIDAD`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ESPECIALIDAD` (
  `id_especialidad` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) DEFAULT NULL,
  `estado` varchar(20) DEFAULT NULL,
  `descripcion` text,
  PRIMARY KEY (`id_especialidad`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ESPECIALIDAD`
--

LOCK TABLES `ESPECIALIDAD` WRITE;
/*!40000 ALTER TABLE `ESPECIALIDAD` DISABLE KEYS */;
INSERT INTO `ESPECIALIDAD` VALUES (1,'Medicina General','Activo','Atención médica básica y orientación general para el paciente.'),(2,'Pediatría','Activo','Especialidad dedicada al cuidado y tratamiento de niños y adolescentes.'),(3,'Ginecología','Activo','Atiende la salud del sistema reproductor femenino y control prenatal.'),(4,'Cardiología','Activo','Diagnóstico y tratamiento de enfermedades del corazón y sistema circulatorio.'),(5,'Dermatología','Activo','Tratamiento de enfermedades de la piel, cabello y uñas.'),(6,'Oftalmología','Activo','Estudia y trata los trastornos de la vista y enfermedades oculares.'),(7,'Odontología','Activo','Prevención y tratamiento de enfermedades bucodentales.'),(8,'Neurología','Activo','Diagnóstico y tratamiento de trastornos del sistema nervioso.'),(9,'Traumatología','Activo','Atiende lesiones del sistema músculo-esquelético.'),(10,'Psiquiatría','Activo','Diagnóstico y tratamiento de trastornos mentales y emocionales.'),(11,'Endocrinología','Activo','Diagnóstico y tratamiento de enfermedades hormonales y del metabolismo, como diabetes, tiroides y obesidad.'),(12,'Gastroenterología','Activo','Atiende trastornos del sistema digestivo: estómago, intestinos, hígado, páncreas y vesícula biliar.'),(13,'Otorrinolaringología','Activo','Diagnóstico y tratamiento de enfermedades del oído, nariz, garganta y vías respiratorias superiores.'),(14,'Urología','Activo','Especialidad enfocada en el tratamiento médico y quirúrgico del sistema urinario y aparato reproductor masculino.'),(15,'Cirugía Plástica','Activo','Realiza procedimientos reconstructivos, estéticos y reparadores del cuerpo y rostro.'),(16,'Neurocirugía','Activo','Cirugía del cerebro, médula espinal y sistema nervioso periférico.'),(17,'Cirugía General','Activo','Especialidad quirúrgica que aborda patologías del abdomen, piel, tejidos blandos y órganos internos.');
/*!40000 ALTER TABLE `ESPECIALIDAD` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `EXAMEN`
--

DROP TABLE IF EXISTS `EXAMEN`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `EXAMEN` (
  `id_examen` int NOT NULL AUTO_INCREMENT,
  `fecha_examen` date DEFAULT NULL,
  `hora_examen` time DEFAULT NULL,
  `observacion` text,
  `estado` varchar(20) DEFAULT NULL,
  `id_reserva` int DEFAULT NULL,
  `id_reservaServicio` int DEFAULT NULL,
  PRIMARY KEY (`id_examen`),
  KEY `id_reserva` (`id_reserva`),
  KEY `id_reservaServicio` (`id_reservaServicio`),
  CONSTRAINT `EXAMEN_ibfk_1` FOREIGN KEY (`id_reserva`) REFERENCES `RESERVA` (`id_reserva`),
  CONSTRAINT `EXAMEN_ibfk_2` FOREIGN KEY (`id_reservaServicio`) REFERENCES `RESERVA` (`id_reserva`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `EXAMEN`
--

LOCK TABLES `EXAMEN` WRITE;
/*!40000 ALTER TABLE `EXAMEN` DISABLE KEYS */;
/*!40000 ALTER TABLE `EXAMEN` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `HORARIO`
--

DROP TABLE IF EXISTS `HORARIO`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `HORARIO` (
  `id_horario` int NOT NULL AUTO_INCREMENT,
  `id_empleado` int DEFAULT NULL,
  `fecha` date DEFAULT NULL,
  `hora_inicio` time DEFAULT NULL,
  `hora_fin` time DEFAULT NULL,
  `disponibilidad` varchar(30) DEFAULT NULL,
  `estado` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`id_horario`),
  KEY `id_empleado` (`id_empleado`),
  CONSTRAINT `HORARIO_ibfk_1` FOREIGN KEY (`id_empleado`) REFERENCES `EMPLEADO` (`id_empleado`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `HORARIO`
--

LOCK TABLES `HORARIO` WRITE;
/*!40000 ALTER TABLE `HORARIO` DISABLE KEYS */;
INSERT INTO `HORARIO` VALUES (1,1,'2025-10-27','08:00:00','16:00:00','Disponible','Activo'),(2,1,'2025-10-28','08:00:00','16:00:00','Disponible','Activo'),(3,2,'2025-10-27','09:00:00','13:00:00','Disponible','Activo'),(4,2,'2025-10-29','14:00:00','18:00:00','Disponible','Activo'),(5,2,'2025-10-30','09:00:00','13:00:00','Disponible','Activo'),(6,3,'2025-10-27','07:00:00','15:00:00','Disponible','Activo'),(7,3,'2025-10-28','07:00:00','15:00:00','Disponible','Activo'),(8,3,'2025-10-29','07:00:00','15:00:00','Disponible','Activo'),(9,4,'2025-10-27','10:00:00','14:00:00','Disponible','Activo'),(10,4,'2025-10-28','10:00:00','14:00:00','Disponible','Activo'),(11,4,'2025-10-29','15:00:00','19:00:00','Disponible','Activo'),(12,5,'2025-10-27','13:00:00','21:00:00','Disponible','inactivo'),(13,5,'2025-10-28','13:00:00','21:00:00','Disponible','Activo'),(14,5,'2025-10-29','13:00:00','21:00:00','Disponible','Activo'),(15,6,'2025-10-27','08:00:00','14:00:00','Disponible','Activo'),(16,6,'2025-10-28','14:00:00','20:00:00','Disponible','Activo'),(17,6,'2025-10-29','08:00:00','14:00:00','Disponible','Activo'),(18,7,'2025-10-27','07:30:00','12:30:00','Disponible','Activo'),(19,7,'2025-10-28','07:30:00','12:30:00','Disponible','Activo'),(20,7,'2025-10-29','07:30:00','12:30:00','Disponible','Activo');
/*!40000 ALTER TABLE `HORARIO` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `INCIDENCIA`
--

DROP TABLE IF EXISTS `INCIDENCIA`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `INCIDENCIA` (
  `id_incidencia` int NOT NULL AUTO_INCREMENT,
  `descripcion` text,
  `fecha_registro` date DEFAULT NULL,
  `id_paciente` int DEFAULT NULL,
  `categoria` varchar(50) DEFAULT NULL,
  `prioridad` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id_incidencia`),
  KEY `id_paciente` (`id_paciente`),
  CONSTRAINT `INCIDENCIA_ibfk_1` FOREIGN KEY (`id_paciente`) REFERENCES `PACIENTE` (`id_paciente`)
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `INCIDENCIA`
--

LOCK TABLES `INCIDENCIA` WRITE;
/*!40000 ALTER TABLE `INCIDENCIA` DISABLE KEYS */;
INSERT INTO `INCIDENCIA` VALUES (9,'Aire acondicionado del consultorio 3 no funciona','2025-10-25',1,NULL,NULL),(10,'Fuga de agua en el baño del área de pediatría','2025-10-26',2,NULL,NULL),(11,'Computadora de recepción presenta fallas al encender','2025-10-26',4,NULL,NULL),(12,'Falta de insumos en el área de esterilización','2025-10-27',5,NULL,NULL),(13,'Ascensor principal fuera de servicio','2025-10-27',6,NULL,NULL),(14,'Luz intermitente en el pasillo de emergencias','2025-10-28',3,NULL,NULL),(15,'Problemas con la conexión de red en laboratorio','2025-10-28',7,NULL,NULL),(16,'Puerta del almacén no cierra correctamente','2025-10-29',8,NULL,NULL),(17,'No me atendieron correctamente','2025-10-31',8,'Infraestructura','Media'),(18,'cc','2025-10-31',13,'Insumos','Media'),(19,'vvvv','2025-10-31',1,'Insumos','Media'),(20,'h','2025-10-31',8,'Insumos','Media'),(21,'7','2025-10-31',2,'Insumos',NULL),(22,'..','2025-10-31',8,'Otro',NULL),(23,'JO','2025-10-31',8,'Insumos',NULL),(24,'LO','2025-10-31',8,'Equipamiento Médico','Alta'),(25,'}','2025-10-31',8,'Software','Media'),(26,'k','2025-10-31',1,'Hardware','Alta'),(27,'ss','2025-10-31',9,'Hardware','Media'),(28,'sss','2025-10-31',8,'Equipamiento Médico','Alta'),(29,'Prueba1','2025-11-01',NULL,'Infraestructura','Media'),(30,'Prueba1','2025-11-01',NULL,'Infraestructura','Media'),(31,'Prueba2','2025-11-01',NULL,'Software','Media'),(32,'prueba 3','2025-11-01',NULL,'Infraestructura','Media'),(33,'Prueba 4','2025-11-01',6,'Equipamiento Médico','Media'),(34,'prueba 3','2025-11-02',3,'Infraestructura','Media'),(35,'jjj','2025-11-02',4,'Insumos','Baja'),(36,'jjj','2025-11-02',4,'Insumos','Baja'),(37,'yty','2025-11-02',6,'Infraestructura','Baja'),(38,'Cambio de Descripcion','2025-11-02',6,'Infraestructura','Media');
/*!40000 ALTER TABLE `INCIDENCIA` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `NOTIFICACION`
--

DROP TABLE IF EXISTS `NOTIFICACION`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `NOTIFICACION` (
  `id_notificacion` int NOT NULL AUTO_INCREMENT,
  `titulo` varchar(255) DEFAULT NULL,
  `mensaje` text,
  `tipo` varchar(30) DEFAULT NULL,
  `fecha_envio` date DEFAULT NULL,
  `hora_envio` time DEFAULT NULL,
  `id_reserva` int DEFAULT NULL,
  `id_paciente` int DEFAULT NULL,
  PRIMARY KEY (`id_notificacion`),
  KEY `id_paciente` (`id_paciente`),
  KEY `id_reserva` (`id_reserva`),
  CONSTRAINT `NOTIFICACION_ibfk_1` FOREIGN KEY (`id_paciente`) REFERENCES `PACIENTE` (`id_paciente`),
  CONSTRAINT `NOTIFICACION_ibfk_2` FOREIGN KEY (`id_reserva`) REFERENCES `RESERVA` (`id_reserva`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `NOTIFICACION`
--

LOCK TABLES `NOTIFICACION` WRITE;
/*!40000 ALTER TABLE `NOTIFICACION` DISABLE KEYS */;
/*!40000 ALTER TABLE `NOTIFICACION` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `OPERACION`
--

DROP TABLE IF EXISTS `OPERACION`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `OPERACION` (
  `id_operacion` int NOT NULL AUTO_INCREMENT,
  `fecha_operacion` date DEFAULT NULL,
  `hora_inicio` time DEFAULT NULL,
  `hora_fin` time DEFAULT NULL,
  `observaciones` text,
  `id_reserva` int DEFAULT NULL,
  `id_empleado` int DEFAULT NULL,
  `id_cita` int DEFAULT NULL,
  PRIMARY KEY (`id_operacion`),
  KEY `id_reserva` (`id_reserva`),
  KEY `id_empleado` (`id_empleado`),
  KEY `id_cita` (`id_cita`),
  CONSTRAINT `OPERACION_ibfk_1` FOREIGN KEY (`id_reserva`) REFERENCES `RESERVA` (`id_reserva`),
  CONSTRAINT `OPERACION_ibfk_2` FOREIGN KEY (`id_empleado`) REFERENCES `EMPLEADO` (`id_empleado`),
  CONSTRAINT `OPERACION_ibfk_3` FOREIGN KEY (`id_cita`) REFERENCES `CITA` (`id_cita`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `OPERACION`
--

LOCK TABLES `OPERACION` WRITE;
/*!40000 ALTER TABLE `OPERACION` DISABLE KEYS */;
/*!40000 ALTER TABLE `OPERACION` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `OPERACION_RECURSO`
--

DROP TABLE IF EXISTS `OPERACION_RECURSO`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `OPERACION_RECURSO` (
  `id_operacion_recurso` int NOT NULL AUTO_INCREMENT,
  `id_operacion` int DEFAULT NULL,
  `id_recurso` int DEFAULT NULL,
  PRIMARY KEY (`id_operacion_recurso`),
  KEY `id_operacion` (`id_operacion`),
  KEY `id_recurso` (`id_recurso`),
  CONSTRAINT `OPERACION_RECURSO_ibfk_1` FOREIGN KEY (`id_operacion`) REFERENCES `OPERACION` (`id_operacion`),
  CONSTRAINT `OPERACION_RECURSO_ibfk_2` FOREIGN KEY (`id_recurso`) REFERENCES `RECURSO` (`id_recurso`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `OPERACION_RECURSO`
--

LOCK TABLES `OPERACION_RECURSO` WRITE;
/*!40000 ALTER TABLE `OPERACION_RECURSO` DISABLE KEYS */;
/*!40000 ALTER TABLE `OPERACION_RECURSO` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `PACIENTE`
--

DROP TABLE IF EXISTS `PACIENTE`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `PACIENTE` (
  `id_paciente` int NOT NULL AUTO_INCREMENT,
  `nombres` varchar(100) DEFAULT NULL,
  `apellidos` varchar(100) DEFAULT NULL,
  `documento_identidad` varchar(20) DEFAULT NULL,
  `sexo` varchar(20) DEFAULT NULL,
  `fecha_nacimiento` date DEFAULT NULL,
  `id_usuario` int DEFAULT NULL,
  `id_distrito` int DEFAULT NULL,
  PRIMARY KEY (`id_paciente`),
  UNIQUE KEY `documento_identidad` (`documento_identidad`),
  KEY `id_usuario` (`id_usuario`),
  KEY `id_distrito` (`id_distrito`),
  CONSTRAINT `PACIENTE_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `USUARIO` (`id_usuario`),
  CONSTRAINT `PACIENTE_ibfk_2` FOREIGN KEY (`id_distrito`) REFERENCES `DISTRITO` (`id_distrito`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `PACIENTE`
--

LOCK TABLES `PACIENTE` WRITE;
/*!40000 ALTER TABLE `PACIENTE` DISABLE KEYS */;
INSERT INTO `PACIENTE` VALUES (1,'Dana','Garcia','99999999','Femenino','2007-11-02',4,140312),(2,'Paciente','1','14785569',NULL,'2025-09-17',5,140301),(3,'Lucía','Rojas Pérez','74569812','Femenino','1992-04-15',10,140105),(4,'Fernando','López Ramírez','73214567','Masculino','1988-09-22',11,140312),(5,'Karina','Mendoza Torres','75623145','Femenino','1995-11-10',12,140201),(6,'David','Silva Gutiérrez','74891236','Masculino','1990-07-05',13,140101),(7,'Rocío','Torres Campos','76253418','Femenino','1985-01-25',14,130504),(8,'Andrés','Pacheco Ruiz','75361248','Masculino','1998-03-19',15,131101),(9,'María','García León','76984512','Femenino','2000-06-30',16,20903),(10,'Luis','Vargas Moreno','74123689','Masculino','1993-08-14',17,140105),(13,'juan','diez','12236533','Masculino','2004-05-27',22,150201),(14,'Matias','Puican','15687792',NULL,'2025-10-07',23,60101),(15,'Marle','Marzo','94893939','F','2002-10-15',24,101004),(16,'Ñatra','Dertor','93333333','M','2002-11-14',25,160507),(17,'Mancos','Pao','93333332','Masculino','2025-11-17',26,50104);
/*!40000 ALTER TABLE `PACIENTE` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `PROGRAMACION`
--

DROP TABLE IF EXISTS `PROGRAMACION`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `PROGRAMACION` (
  `id_programacion` int NOT NULL AUTO_INCREMENT,
  `fecha` date DEFAULT NULL,
  `hora_inicio` time DEFAULT NULL,
  `hora_fin` time DEFAULT NULL,
  `estado` varchar(20) DEFAULT NULL,
  `id_servicio` int DEFAULT NULL,
  `id_horario` int DEFAULT NULL,
  PRIMARY KEY (`id_programacion`),
  KEY `id_servicio` (`id_servicio`),
  KEY `id_horario` (`id_horario`),
  CONSTRAINT `PROGRAMACION_ibfk_1` FOREIGN KEY (`id_servicio`) REFERENCES `SERVICIO` (`id_servicio`),
  CONSTRAINT `PROGRAMACION_ibfk_2` FOREIGN KEY (`id_horario`) REFERENCES `HORARIO` (`id_horario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `PROGRAMACION`
--

LOCK TABLES `PROGRAMACION` WRITE;
/*!40000 ALTER TABLE `PROGRAMACION` DISABLE KEYS */;
/*!40000 ALTER TABLE `PROGRAMACION` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `PROVINCIA`
--

DROP TABLE IF EXISTS `PROVINCIA`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `PROVINCIA` (
  `id_provincia` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `id_departamento` int DEFAULT NULL,
  PRIMARY KEY (`id_provincia`),
  KEY `id_departamento` (`id_departamento`),
  CONSTRAINT `PROVINCIA_ibfk_1` FOREIGN KEY (`id_departamento`) REFERENCES `DEPARTAMENTO` (`id_departamento`)
) ENGINE=InnoDB AUTO_INCREMENT=2505 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `PROVINCIA`
--

LOCK TABLES `PROVINCIA` WRITE;
/*!40000 ALTER TABLE `PROVINCIA` DISABLE KEYS */;
INSERT INTO `PROVINCIA` VALUES (101,'Chachapoyas',1),(102,'Bagua',1),(103,'Bongará',1),(104,'Condorcanqui',1),(105,'Luya',1),(106,'Rodríguez de Mendoza',1),(107,'Utcubamba',1),(201,'Huaraz',2),(202,'Aija',2),(203,'Antonio Raymondi',2),(204,'Asunción',2),(205,'Bolognesi',2),(206,'Carhuaz',2),(207,'Carlos Fermín Fitzcarrald',2),(208,'Casma',2),(209,'Corongo',2),(210,'Huari',2),(211,'Huarmey',2),(212,'Huaylas',2),(213,'Mariscal Luzuriaga',2),(214,'Ocros',2),(215,'Pallasca',2),(216,'Pomabamba',2),(217,'Recuay',2),(218,'Santa',2),(219,'Sihuas',2),(220,'Yungay',2),(301,'Abancay',3),(302,'Andahuaylas',3),(303,'Antabamba',3),(304,'Aymaraes',3),(305,'Cotabambas',3),(306,'Chincheros',3),(307,'Grau',3),(401,'Arequipa',4),(402,'Camaná',4),(403,'Caravelí',4),(404,'Castilla',4),(405,'Caylloma',4),(406,'Condesuyos',4),(407,'Islay',4),(408,'La Uniòn',4),(501,'Huamanga',5),(502,'Cangallo',5),(503,'Huanca Sancos',5),(504,'Huanta',5),(505,'La Mar',5),(506,'Lucanas',5),(507,'Parinacochas',5),(508,'Pàucar del Sara Sara',5),(509,'Sucre',5),(510,'Víctor Fajardo',5),(511,'Vilcas Huamán',5),(601,'Cajamarca',6),(602,'Cajabamba',6),(603,'Celendín',6),(604,'Chota',6),(605,'Contumazá',6),(606,'Cutervo',6),(607,'Hualgayoc',6),(608,'Jaén',6),(609,'San Ignacio',6),(610,'San Marcos',6),(611,'San Miguel',6),(612,'San Pablo',6),(613,'Santa Cruz',6),(701,'Prov. Const. del Callao',7),(801,'Cusco',8),(802,'Acomayo',8),(803,'Anta',8),(804,'Calca',8),(805,'Canas',8),(806,'Canchis',8),(807,'Chumbivilcas',8),(808,'Espinar',8),(809,'La Convención',8),(810,'Paruro',8),(811,'Paucartambo',8),(812,'Quispicanchi',8),(813,'Urubamba',8),(901,'Huancavelica',9),(902,'Acobamba',9),(903,'Angaraes',9),(904,'Castrovirreyna',9),(905,'Churcampa',9),(906,'Huaytará',9),(907,'Tayacaja',9),(1001,'Huánuco',10),(1002,'Ambo',10),(1003,'Dos de Mayo',10),(1004,'Huacaybamba',10),(1005,'Huamalíes',10),(1006,'Leoncio Prado',10),(1007,'Marañón',10),(1008,'Pachitea',10),(1009,'Puerto Inca',10),(1010,'Lauricocha',10),(1011,'Yarowilca',10),(1101,'Ica',11),(1102,'Chincha',11),(1103,'Nasca',11),(1104,'Palpa',11),(1105,'Pisco',11),(1201,'Huancayo',12),(1202,'Concepción',12),(1203,'Chanchamayo',12),(1204,'Jauja',12),(1205,'Junín',12),(1206,'Satipo',12),(1207,'Tarma',12),(1208,'Yauli',12),(1209,'Chupaca',12),(1301,'Trujillo',13),(1302,'Ascope',13),(1303,'Bolívar',13),(1304,'Chepén',13),(1305,'Julcán',13),(1306,'Otuzco',13),(1307,'Pacasmayo',13),(1308,'Pataz',13),(1309,'Sánchez Carrión',13),(1310,'Santiago de Chuco',13),(1311,'Gran Chimú',13),(1312,'Virú',13),(1401,'Chiclayo',14),(1402,'Ferreñafe',14),(1403,'Lambayeque',14),(1501,'Lima',15),(1502,'Barranca',15),(1503,'Cajatambo',15),(1504,'Canta',15),(1505,'Cañete',15),(1506,'Huaral',15),(1507,'Huarochirí',15),(1508,'Huaura',15),(1509,'Oyón',15),(1510,'Yauyos',15),(1601,'Maynas',16),(1602,'Alto Amazonas',16),(1603,'Loreto',16),(1604,'Mariscal Ramón Castilla',16),(1605,'Requena',16),(1606,'Ucayali',16),(1607,'Datem del Marañón',16),(1608,'Putumayo',16),(1701,'Tambopata',17),(1702,'Manu',17),(1703,'Tahuamanu',17),(1801,'Mariscal Nieto',18),(1802,'General Sánchez Cerro',18),(1803,'Ilo',18),(1901,'Pasco',19),(1902,'Daniel Alcides Carrión',19),(1903,'Oxapampa',19),(2001,'Piura',20),(2002,'Ayabaca',20),(2003,'Huancabamba',20),(2004,'Morropón',20),(2005,'Paita',20),(2006,'Sullana',20),(2007,'Talara',20),(2008,'Sechura',20),(2101,'Puno',21),(2102,'Azángaro',21),(2103,'Carabaya',21),(2104,'Chucuito',21),(2105,'El Collao',21),(2106,'Huancané',21),(2107,'Lampa',21),(2108,'Melgar',21),(2109,'Moho',21),(2110,'San Antonio de Putina',21),(2111,'San Román',21),(2112,'Sandia',21),(2113,'Yunguyo',21),(2201,'Moyobamba',22),(2202,'Bellavista',22),(2203,'El Dorado',22),(2204,'Huallaga',22),(2205,'Lamas',22),(2206,'Mariscal Cáceres',22),(2207,'Picota',22),(2208,'Rioja',22),(2209,'San Martín',22),(2210,'Tocache',22),(2301,'Tacna',23),(2302,'Candarave',23),(2303,'Jorge Basadre',23),(2304,'Tarata',23),(2401,'Tumbes',24),(2402,'Contralmirante Villar',24),(2403,'Zarumilla',24),(2501,'Coronel Portillo',25),(2502,'Atalaya',25),(2503,'Padre Abad',25),(2504,'Purús',25);
/*!40000 ALTER TABLE `PROVINCIA` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `RECUPERACION_CONTRASENA`
--

DROP TABLE IF EXISTS `RECUPERACION_CONTRASENA`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `RECUPERACION_CONTRASENA` (
  `id_recuperacion` int NOT NULL AUTO_INCREMENT,
  `id_usuario` int NOT NULL,
  `codigo` varchar(6) NOT NULL,
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `usado` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id_recuperacion`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `RECUPERACION_CONTRASENA_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `USUARIO` (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `RECUPERACION_CONTRASENA`
--

LOCK TABLES `RECUPERACION_CONTRASENA` WRITE;
/*!40000 ALTER TABLE `RECUPERACION_CONTRASENA` DISABLE KEYS */;
INSERT INTO `RECUPERACION_CONTRASENA` VALUES (3,5,'422339','2025-10-28 22:44:01',0),(6,23,'311891','2025-10-31 07:03:27',0);
/*!40000 ALTER TABLE `RECUPERACION_CONTRASENA` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `RECURSO`
--

DROP TABLE IF EXISTS `RECURSO`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `RECURSO` (
  `id_recurso` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) DEFAULT NULL,
  `estado` varchar(20) DEFAULT NULL,
  `id_tipo_recurso` int DEFAULT NULL,
  PRIMARY KEY (`id_recurso`),
  KEY `id_tipo_recurso` (`id_tipo_recurso`),
  CONSTRAINT `RECURSO_ibfk_1` FOREIGN KEY (`id_tipo_recurso`) REFERENCES `TIPO_RECURSO` (`id_tipo_recurso`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `RECURSO`
--

LOCK TABLES `RECURSO` WRITE;
/*!40000 ALTER TABLE `RECURSO` DISABLE KEYS */;
INSERT INTO `RECURSO` VALUES (1,'Ecógrafo 4D/5D','Activo',1),(2,'Máquina de Rayos X','Activo',1),(3,'Tomógrafo Computarizado','Activo',1),(4,'Electrocardiógrafo','Activo',1),(5,'Monitor Multiparámetro','Activo',1),(6,'Guantes Estériles','Activo',2),(7,'Jeringas Desechables','Activo',2),(8,'Gasas y Vendas','Activo',2),(9,'Mascarillas Quirúrgicas','Activo',2),(10,'Batas Médicas','Activo',2),(11,'Sala de Cirugía Principal','Activo',3),(12,'Sala de Recuperación','Activo',3),(13,'Consultorio Médico General','Activo',3),(14,'Laboratorio Clínico','Activo',3),(15,'Central de Esterilización','Activo',3),(16,'Área de Imagenología','Activo',3),(17,'Sala de Espera de Pacientes','Activo',3),(18,'Área de Toma de Muestras','Activo',3);
/*!40000 ALTER TABLE `RECURSO` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `RECURSO_ARCHIVO`
--

DROP TABLE IF EXISTS `RECURSO_ARCHIVO`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `RECURSO_ARCHIVO` (
  `id_archivo` int NOT NULL AUTO_INCREMENT,
  `id_recurso` int NOT NULL,
  `nombre_archivo` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ruta_archivo` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `tipo_archivo` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `tamano_bytes` bigint DEFAULT NULL,
  `fecha_subida` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_archivo`),
  KEY `idx_recurso` (`id_recurso`),
  KEY `idx_fecha` (`fecha_subida`),
  CONSTRAINT `RECURSO_ARCHIVO_ibfk_1` FOREIGN KEY (`id_recurso`) REFERENCES `RECURSO` (`id_recurso`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `RECURSO_ARCHIVO`
--

LOCK TABLES `RECURSO_ARCHIVO` WRITE;
/*!40000 ALTER TABLE `RECURSO_ARCHIVO` DISABLE KEYS */;
/*!40000 ALTER TABLE `RECURSO_ARCHIVO` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `REPORTE`
--

DROP TABLE IF EXISTS `REPORTE`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `REPORTE` (
  `id_reporte` int NOT NULL AUTO_INCREMENT,
  `codigo` varchar(50) DEFAULT NULL,
  `nombre` varchar(100) DEFAULT NULL,
  `tipo` varchar(50) DEFAULT NULL,
  `descripcion` text,
  `contenido_json` json DEFAULT NULL,
  `estado` varchar(20) DEFAULT 'Pendiente',
  `fecha_creacion` timestamp NULL DEFAULT NULL,
  `id_categoria` int DEFAULT NULL,
  `id_empleado` int DEFAULT NULL,
  `id_servicio` int DEFAULT NULL,
  `id_recurso` int DEFAULT NULL,
  PRIMARY KEY (`id_reporte`),
  KEY `id_categoria` (`id_categoria`),
  KEY `id_empleado` (`id_empleado`),
  KEY `id_servicio` (`id_servicio`),
  KEY `id_recurso` (`id_recurso`),
  CONSTRAINT `REPORTE_ibfk_1` FOREIGN KEY (`id_categoria`) REFERENCES `CATEGORIA` (`id_categoria`),
  CONSTRAINT `REPORTE_ibfk_2` FOREIGN KEY (`id_empleado`) REFERENCES `EMPLEADO` (`id_empleado`),
  CONSTRAINT `REPORTE_ibfk_3` FOREIGN KEY (`id_servicio`) REFERENCES `SERVICIO` (`id_servicio`),
  CONSTRAINT `REPORTE_ibfk_4` FOREIGN KEY (`id_recurso`) REFERENCES `RECURSO` (`id_recurso`)
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `REPORTE`
--

LOCK TABLES `REPORTE` WRITE;
/*!40000 ALTER TABLE `REPORTE` DISABLE KEYS */;
INSERT INTO `REPORTE` VALUES (31,'REP-20251031105500-1787','dd','Auditoría','dd',NULL,'Pendiente','2025-10-31 10:55:01',8,2,NULL,NULL),(32,'REP-20251102-0001','Reporte de Prueba 1','Mensual','Este es un reporte de prueba para validar la funcionalidad del sistema',NULL,'Completado','2025-11-02 01:16:18',1,2,NULL,NULL),(33,'REP-20251102-0002','Reporte de Incidencias','Semanal','Reporte semanal de incidencias registradas en el sistema',NULL,'Completado','2025-11-02 01:16:18',1,2,NULL,NULL),(34,'REP-20251102-0003','Reporte de Recursos','Mensual','Estado actual de los recursos físicos de la clínica',NULL,'Completado','2025-11-02 01:16:18',1,2,NULL,NULL),(35,'REP-20251102-0004','Reporte de Servicios','Trimestral','Análisis de los servicios prestados durante el trimestre',NULL,'Pendiente','2025-11-02 01:16:18',1,2,NULL,NULL),(36,'REP-20251102-0005','Reporte de Auditoría','Anual','Auditoría anual de procesos y procedimientos',NULL,'En Proceso','2025-11-02 01:16:18',1,2,NULL,NULL),(37,'REP-20251102-0001','Reporte de Prueba 1','Mensual','Este es un reporte de prueba para validar la funcionalidad del sistema',NULL,'Completado','2025-11-02 01:16:37',1,2,NULL,NULL),(38,'REP-20251102-0002','Reporte de Incidencias','Semanal','Reporte semanal de incidencias registradas en el sistema',NULL,'Completado','2025-11-02 01:16:37',1,2,NULL,NULL),(39,'REP-20251102-0003','Reporte de Recursos','Mensual','Estado actual de los recursos físicos de la clínica',NULL,'Completado','2025-11-02 01:16:37',1,2,NULL,NULL),(40,'REP-20251102-0004','Reporte de Servicios','Trimestral','Análisis de los servicios prestados durante el trimestre',NULL,'Pendiente','2025-11-02 01:16:37',1,2,NULL,NULL),(41,'REP-20251102-0005','Reporte de Auditoría','Anual','Auditoría anual de procesos y procedimientos',NULL,'En Proceso','2025-11-02 01:16:37',1,2,NULL,NULL);
/*!40000 ALTER TABLE `REPORTE` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `REPORTE_ARCHIVO`
--

DROP TABLE IF EXISTS `REPORTE_ARCHIVO`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `REPORTE_ARCHIVO` (
  `id_archivo` int NOT NULL AUTO_INCREMENT,
  `id_reporte` int NOT NULL,
  `nombre_archivo` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `ruta_archivo` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `tipo_archivo` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `tamano_bytes` bigint NOT NULL,
  `fecha_subida` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_archivo`),
  KEY `idx_id_reporte` (`id_reporte`),
  KEY `idx_fecha_subida` (`fecha_subida`),
  CONSTRAINT `fk_reporte_archivo` FOREIGN KEY (`id_reporte`) REFERENCES `REPORTE` (`id_reporte`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `REPORTE_ARCHIVO`
--

LOCK TABLES `REPORTE_ARCHIVO` WRITE;
/*!40000 ALTER TABLE `REPORTE_ARCHIVO` DISABLE KEYS */;
INSERT INTO `REPORTE_ARCHIVO` VALUES (9,31,'Herramientas_de_Red_-_CLI_GUI.pdf','uploads/reportes\\20251031105501_Herramientas_de_Red_-_CLI_GUI.pdf','application/pdf',954929,'2025-10-31 15:55:01');
/*!40000 ALTER TABLE `REPORTE_ARCHIVO` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `RESERVA`
--

DROP TABLE IF EXISTS `RESERVA`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `RESERVA` (
  `id_reserva` int NOT NULL AUTO_INCREMENT,
  `fecha_registro` date DEFAULT NULL,
  `hora_registro` time DEFAULT NULL,
  `tipo` int DEFAULT NULL,
  `estado` varchar(20) DEFAULT NULL,
  `motivo_cancelacion` varchar(200) DEFAULT NULL,
  `id_paciente` int DEFAULT NULL,
  `id_programacion` int DEFAULT NULL,
  PRIMARY KEY (`id_reserva`),
  KEY `id_paciente` (`id_paciente`),
  KEY `id_programacion` (`id_programacion`),
  CONSTRAINT `RESERVA_ibfk_1` FOREIGN KEY (`id_paciente`) REFERENCES `PACIENTE` (`id_paciente`),
  CONSTRAINT `RESERVA_ibfk_2` FOREIGN KEY (`id_programacion`) REFERENCES `PROGRAMACION` (`id_programacion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `RESERVA`
--

LOCK TABLES `RESERVA` WRITE;
/*!40000 ALTER TABLE `RESERVA` DISABLE KEYS */;
/*!40000 ALTER TABLE `RESERVA` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ROL`
--

DROP TABLE IF EXISTS `ROL`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ROL` (
  `id_rol` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `estado` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id_rol`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ROL`
--

LOCK TABLES `ROL` WRITE;
/*!40000 ALTER TABLE `ROL` DISABLE KEYS */;
INSERT INTO `ROL` VALUES (1,'Administrador','Activo'),(2,'Médico','Activo'),(3,'Recepcionista','Activo'),(4,'Farmacéutico','Activo'),(5,'Laboratorista','Activo');
/*!40000 ALTER TABLE `ROL` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `SERVICIO`
--

DROP TABLE IF EXISTS `SERVICIO`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `SERVICIO` (
  `id_servicio` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) DEFAULT NULL,
  `descripcion` text,
  `estado` varchar(20) DEFAULT NULL,
  `id_tipo_servicio` int DEFAULT NULL,
  `id_especialidad` int DEFAULT NULL,
  PRIMARY KEY (`id_servicio`),
  KEY `id_tipo_servicio` (`id_tipo_servicio`),
  KEY `id_especialidad` (`id_especialidad`),
  CONSTRAINT `SERVICIO_ibfk_1` FOREIGN KEY (`id_tipo_servicio`) REFERENCES `TIPO_SERVICIO` (`id_tipo_servicio`),
  CONSTRAINT `SERVICIO_ibfk_2` FOREIGN KEY (`id_especialidad`) REFERENCES `ESPECIALIDAD` (`id_especialidad`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `SERVICIO`
--

LOCK TABLES `SERVICIO` WRITE;
/*!40000 ALTER TABLE `SERVICIO` DISABLE KEYS */;
INSERT INTO `SERVICIO` VALUES (1,'Pediatría','Atención médica personalizada en diversas especialidades médicas.','Activo',1,2),(2,'Cirugía General','Procedimientos quirúrgicos enfocados en el tratamiento de patologías abdominales, de piel, tejidos blandos y hernias.','Activo',2,17),(3,'Hematología','Análisis de sangre para evaluación del estado general de salud.','Activo',6,NULL),(4,'Rayos X','Servicios de diagnóstico por imágenes mediante rayos X y tomografías.','activo',3,NULL),(5,'Ecografía 4D/5D/6D','Servicio de ecografía avanzada para control médico y gestacional.','Activo',3,3),(6,'Banco de Sangre','Procesamiento y almacenamiento de sangre y hemoderivados para transfusiones.','Activo',4,NULL),(7,'Central de Esterilización','Área encargada de la esterilización de materiales e instrumentos médicos.','Activo',4,NULL),(8,'Farmacia','Dispensación y venta de medicamentos para pacientes hospitalizados y externos.','Activo',5,NULL),(10,'Tomografía','Servicios de diagnóstico por tomografías.','Activo',3,NULL),(11,'Cardiología','Especialidad encargada del diagnóstico, tratamiento y prevención de las enfermedades del corazón y del sistema cardiovascular.','Activo',1,4),(12,'Endocrinología','Se ocupa del estudio, diagnóstico y tratamiento de los trastornos hormonales y metabólicos, como la diabetes y los problemas tiroideos.','Activo',1,11),(13,'Gastroenterología','Atiende las enfermedades del aparato digestivo, incluyendo estómago, hígado, páncreas e intestinos.','Activo',1,12),(14,'Ginecología','Brinda atención integral a la salud reproductiva y ginecológica de la mujer, desde la adolescencia hasta la menopausia.','Activo',1,3),(15,'Dermatología','Especialidad médica enfocada en el diagnóstico y tratamiento de enfermedades de la piel, cabello y uñas.','Activo',1,5),(16,'Neurología','Se dedica al estudio, diagnóstico y tratamiento de los trastornos del sistema nervioso central y periférico.','Activo',1,8),(17,'Otorrinolaringología','Se encarga del diagnóstico y tratamiento de enfermedades del oído, nariz, garganta y estructuras relacionadas de cabeza y cuello.','Activo',1,13),(18,'Traumatología','Trata lesiones y enfermedades del sistema musculoesquelético, como huesos, articulaciones, ligamentos y tendones.','Activo',1,NULL),(19,'Urología','Especialidad médica que se ocupa del sistema urinario en ambos sexos y del aparato reproductor masculino.','Activo',1,14),(20,'Bioquímica Clínica','Pruebas para medir glucosa, colesterol, función renal y hepática.','Activo',6,NULL),(21,'Inmunología','Pruebas inmunológicas y detección de anticuerpos.','Activo',6,NULL),(22,'Cirugía Ginecológica','Intervenciones quirúrgicas relacionadas con el sistema reproductor femenino, como histerectomía o laparoscopía ginecológica.','Activo',2,3),(23,'Cirugía Ortopédica y Traumatológica','Cirugías de huesos, articulaciones, tendones y ligamentos para tratar fracturas y lesiones musculoesqueléticas.','Activo',2,NULL),(24,'Cirugía Urológica','Procedimientos quirúrgicos del sistema urinario y aparato reproductor masculino.','Activo',2,14),(25,'Cirugía Plástica','Procedimientos estéticos y reconstructivos destinados a mejorar la apariencia o restaurar la funcionalidad de tejidos y estructuras corporales.','Activo',2,15),(26,'Neurocirugía','Procedimientos quirúrgicos que tratan enfermedades del cerebro, médula espinal y sistema nervioso periférico.','Activo',2,8),(27,'Cirugía Gastrointestinal','Cirugías del aparato digestivo que incluyen estómago, intestinos, hígado, vesícula biliar y páncreas.','Activo',2,12),(29,'Prueba1','Prueba919291','activo',5,NULL);
/*!40000 ALTER TABLE `SERVICIO` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `TIPO_RECURSO`
--

DROP TABLE IF EXISTS `TIPO_RECURSO`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `TIPO_RECURSO` (
  `id_tipo_recurso` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) DEFAULT NULL,
  `descripcion` text,
  PRIMARY KEY (`id_tipo_recurso`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `TIPO_RECURSO`
--

LOCK TABLES `TIPO_RECURSO` WRITE;
/*!40000 ALTER TABLE `TIPO_RECURSO` DISABLE KEYS */;
INSERT INTO `TIPO_RECURSO` VALUES (1,'Equipamiento Médico','Dispositivos, máquinas y equipos utilizados para diagnóstico, tratamiento y monitoreo de pacientes.'),(2,'Material Médico','Insumos y materiales descartables necesarios para la atención médica y quirúrgica.'),(3,'Infraestructura','Ambientes físicos, áreas clínicas y espacios de apoyo en la clínica.');
/*!40000 ALTER TABLE `TIPO_RECURSO` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `TIPO_SERVICIO`
--

DROP TABLE IF EXISTS `TIPO_SERVICIO`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `TIPO_SERVICIO` (
  `id_tipo_servicio` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) DEFAULT NULL,
  `descripcion` text,
  PRIMARY KEY (`id_tipo_servicio`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `TIPO_SERVICIO`
--

LOCK TABLES `TIPO_SERVICIO` WRITE;
/*!40000 ALTER TABLE `TIPO_SERVICIO` DISABLE KEYS */;
INSERT INTO `TIPO_SERVICIO` VALUES (1,'Servicios de Consulta','Atención médica en consultorios externos de diversas especialidades.'),(2,'Procedimientos Quirúrgicos','Intervenciones quirúrgicas y atención en centro quirúrgico.'),(3,'Diagnóstico e Imagenología','Servicios de laboratorio clínico, rayos X, ecografía y tomografía.'),(4,'Banco de Sangre y Esterilización','Procesamiento y manejo de sangre, además de la central de esterilización.'),(5,'Farmacia','Atención y dispensación de medicamentos dentro de la clínica.'),(6,'Laboratorio Clínico','Realización de análisis y pruebas de laboratorio para diagnóstico.');
/*!40000 ALTER TABLE `TIPO_SERVICIO` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `USUARIO`
--

DROP TABLE IF EXISTS `USUARIO`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `USUARIO` (
  `id_usuario` int NOT NULL AUTO_INCREMENT,
  `correo` varchar(100) DEFAULT NULL,
  `contrasena` varchar(255) DEFAULT NULL,
  `telefono` varchar(9) DEFAULT NULL,
  `estado` varchar(20) DEFAULT NULL,
  `fecha_creacion` date DEFAULT NULL,
  PRIMARY KEY (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `USUARIO`
--

LOCK TABLES `USUARIO` WRITE;
/*!40000 ALTER TABLE `USUARIO` DISABLE KEYS */;
INSERT INTO `USUARIO` VALUES (1,'mauriciochero7@hotmail.com','scrypt:32768:8:1$u7vOwM7YqnRsenmN$37c58dc7f3e3ec7ad9e32d6308f9a94b45009c6a756fcf0d08a5abfe0f49e669918ed7290eaa4ae7f0ed988f7cd3b0e97ead4de705c638669c660bb249ff64e3','957984611','activo','2025-10-27'),(2,'jose@gmail.com','scrypt:32768:8:1$PYTSjKkQcuC3ZVF1$66ead60596ccb82aa11fd1040cf817f951c3f507f9cf2e1b3e8933205c09961193fc6bc0547e5c704a5a2dda4cda3943ee4fb362e6aa219b35cdf66ff96c58de','986645443','activo','2025-10-27'),(3,'kare@gmail.com','scrypt:32768:8:1$ukgyQX7k4BmnQkCe$4c89f417f48e3d1a9d853978eb4470ca4173381a4e85c9aedcc0bb59d880f67443b45ce6c7783e6e1638b741f74da5aad733be74fdf3d89d8d416c44c8be3c5b','930472644','activo','2025-10-28'),(4,'dana@gmail.com','scrypt:32768:8:1$QZf9w3fdLaeZk2dk$dde0b5ef33bbf081894b38b26feac14604aa227f4283fa64c27c6ec7d11684269e6f43479d4cfc95fe9f8ee8ca44691a9b1f4a996dff5edf13bcbe5dcef6d935','998989898','Activo','2025-10-28'),(5,'karecuenta01@gmail.com','scrypt:32768:8:1$3HsbgIOYkuGQvF6U$220998da16106a61ef4a8261d56b329ceb9c2e549d821e43213a57ae6a92aacb526349bac2862c06a7bdf35752df2ddce3f94e05818168c965a53536636b9b7a','151651651','inactivo','2025-10-28'),(6,'maria.medico@clinicaunion.com','scrypt:32768:8:1$2IwlsUBP8IGkEaNX$e9d9226a9beeac22bd830d3bb3b00286c7bb03e40199d1fa2edfbfac0983874fc66ebc1aac9cf4c942ea82056ed9f1177dd767f3a99b4b622bf798f5fc4baffe','987654321','activo','2025-10-28'),(7,'juan.recepcionista@clinicaunion.com','scrypt:32768:8:1$INM5hFZBUZRo6VKg$a4b2c951dec80dd50cf71368a07e1fa2158bf241c6b945fafaeb5d544e8a96b8a3ae2bc0b3b6b5c8aa0178a34faed8f64f28c6463a230c38768286537863b27c','976543210','activo','2025-10-28'),(8,'carlos.farmaceutico@clinicaunion.com','scrypt:32768:8:1$G5EBZ7dgM8hIG5be$2202f5464a031fb2f5f8fbad9d9e76626320c66b251e149252979d757ed09709ea364b061af63e4538e574877fe204708c204bc0b1b81e528cdbf18690a0bd60','965432109','activo','2025-10-28'),(9,'ana.laboratorista@clinicaunion.com','scrypt:32768:8:1$2UxrVNTlbbiNUCT4$5e6c95337065d763b7e5e6f39438750e64d4a497d4c5c09cafde4d855040d4aa9ad782369ab5d8fecd9d0456b74add6e3b3051e3020856348969ee6bc1000ac1','954321098','activo','2025-10-28'),(10,'lucia.rojas@correo.com','lucia123','987654300','inactivo','2025-10-29'),(11,'fernando.lopez@correo.com','fernando123','987654301','Activo','2025-10-29'),(12,'karina.mendoza@correo.com','karina123','987654302','Activo','2025-10-29'),(13,'david.silva@correo.com','david123','987654303','Activo','2025-10-29'),(14,'rocio.torres@correo.com','rocio123','987654304','Activo','2025-10-29'),(15,'andres.pacheco@correo.com','andres123','987654305','Activo','2025-10-29'),(16,'maria.garcia@correo.com','maria123','987654306','Activo','2025-10-29'),(17,'luis.vargas@correo.com','luis123','987654307','Activo','2025-10-29'),(21,'jassonpuican@gmail.com','scrypt:32768:8:1$AzTGHDKpsv0mbLxF$96a17273ac77fb9809b270f25d3ee85c4657284ad6920c96cd0ee0ddf84d6d64a5553f4b4047a71c0bb1162359e5033364fa45f2a5a862a9cfe132e6b27b376d','961366430','activo','2025-10-31'),(22,'juandiez@gmail.com','scrypt:32768:8:1$4WUFzP4kkzBrVfx6$96cfa1fcd1a4cf5b63ee203c26324dd769bde3e992b651ce5ae42ecc1925112589455bdc8178057c123ce01a36c8867628520ba410278577df371a4fa9b3ab72','961457890','activo','2025-10-31'),(23,'karecuenta102@gmail.com','scrypt:32768:8:1$hMT2kgotgNh4uhcz$a93a34d11ce9885f5cae83a41f63a50cc247c83b3e5c07485487f349843ed148afb71812406aa23e265bc94ad1e923fae700189e3820cf36ca5e947fcccf20f7','921475644','activo','2025-10-31'),(24,'marta@gmail.com','scrypt:32768:8:1$T5UB4AWwiivO0xvg$ac277971e36e8d46c38556015cf1e7f26e58844cc4f66d2104d12e1cb218a3df6ddbf9aa78a64145cac3c72ac0d6980486dcc499eb241115e8723633f2e3fe59','932323312','activo','2025-11-01'),(25,'joaar@gmail.com','scrypt:32768:8:1$Rx0QLXACMGBRtT5d$d2e02d15f8fd430fe36b6844e15d85d3836f0afd99749cb87a3ed2b875cdd21b0ed1dfccbf83d19c3c5b93fa2eb02b51dd86b2153fb69306af01084992802c71','238239239','Activo','2025-11-01'),(26,'par@gamil.com','scrypt:32768:8:1$6zanTEBMOa61MrI1$8c68618cb91408725796c8e47c592061ef368b2ba410cf17d5d64c07dd2160fb48e0cec6cdfc9fb8639c02242b9537f65640a391e2b5f7d0099348616af74891','928839283','Activo','2025-11-01'),(27,'josewe@gmail.com','scrypt:32768:8:1$3vlTVM9pU3MNQg6b$b30913606493bb1fe2e2342fa5e6246f9636cfff9f67581deab36512900c0e01fe4b6f3f8952931b417931ade93495b0a24c973d82430614291f4cd03c47a516','988328289','activo','2025-11-01'),(28,'josecarloschiclayo@gmail.com','scrypt:32768:8:1$1OZpEZOmfBi7B4M7$e11eeafcbbbb4833f1f100071c10a30465f2af3dfa348008a4258b673611b1f50119ecfe8841ef4468ad640ebe7064151f0ed2a10df35330c51ea8d06ea8152a','893229342','Activo','2025-11-01'),(29,'carlr@gmail.com','scrypt:32768:8:1$CDF0CAw4Iq3yXfoi$9106c93cf3763f4ca3b1e3e47e00a02254b9bee9ad213a7e19f29e6bc9f8cb1207d2ee97c7ef3c32ddd4991ff3703899bb51780c76a4d28737d5d37cbd03226d','992323232','Activo','2025-11-01');
/*!40000 ALTER TABLE `USUARIO` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-03  0:54:44
