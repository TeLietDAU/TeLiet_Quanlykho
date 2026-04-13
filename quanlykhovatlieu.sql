-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: quanlykhovatlieu
-- ------------------------------------------------------
-- Server version	8.0.45

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
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=73 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',3,'add_permission'),(6,'Can change permission',3,'change_permission'),(7,'Can delete permission',3,'delete_permission'),(8,'Can view permission',3,'view_permission'),(9,'Can add group',2,'add_group'),(10,'Can change group',2,'change_group'),(11,'Can delete group',2,'delete_group'),(12,'Can view group',2,'view_group'),(13,'Can add content type',4,'add_contenttype'),(14,'Can change content type',4,'change_contenttype'),(15,'Can delete content type',4,'delete_contenttype'),(16,'Can view content type',4,'view_contenttype'),(17,'Can add session',5,'add_session'),(18,'Can change session',5,'change_session'),(19,'Can delete session',5,'delete_session'),(20,'Can view session',5,'view_session'),(21,'Can add category',6,'add_category'),(22,'Can change category',6,'change_category'),(23,'Can delete category',6,'delete_category'),(24,'Can view category',6,'view_category'),(25,'Can add product',7,'add_product'),(26,'Can change product',7,'change_product'),(27,'Can delete product',7,'delete_product'),(28,'Can view product',7,'view_product'),(29,'Can add product unit',8,'add_productunit'),(30,'Can change product unit',8,'change_productunit'),(31,'Can delete product unit',8,'delete_productunit'),(32,'Can view product unit',8,'view_productunit'),(33,'Can add user',9,'add_user'),(34,'Can change user',9,'change_user'),(35,'Can delete user',9,'delete_user'),(36,'Can view user',9,'view_user'),(37,'Can add warehouse transaction',16,'add_warehousetransaction'),(38,'Can change warehouse transaction',16,'change_warehousetransaction'),(39,'Can delete warehouse transaction',16,'delete_warehousetransaction'),(40,'Can view warehouse transaction',16,'view_warehousetransaction'),(41,'Can add inventory',12,'add_inventory'),(42,'Can change inventory',12,'change_inventory'),(43,'Can delete inventory',12,'delete_inventory'),(44,'Can view inventory',12,'view_inventory'),(45,'Can add sales order',13,'add_salesorder'),(46,'Can change sales order',13,'change_salesorder'),(47,'Can delete sales order',13,'delete_salesorder'),(48,'Can view sales order',13,'view_salesorder'),(49,'Can add warehouse',15,'add_warehouse'),(50,'Can change warehouse',15,'change_warehouse'),(51,'Can delete warehouse',15,'delete_warehouse'),(52,'Can view warehouse',15,'view_warehouse'),(53,'Can add system log',14,'add_systemlog'),(54,'Can change system log',14,'change_systemlog'),(55,'Can delete system log',14,'delete_systemlog'),(56,'Can view system log',14,'view_systemlog'),(57,'Can add export log',11,'add_exportlog'),(58,'Can change export log',11,'change_exportlog'),(59,'Can delete export log',11,'delete_exportlog'),(60,'Can view export log',11,'view_exportlog'),(61,'Can add customer debt',10,'add_customerdebt'),(62,'Can change customer debt',10,'change_customerdebt'),(63,'Can delete customer debt',10,'delete_customerdebt'),(64,'Can view customer debt',10,'view_customerdebt'),(65,'Can add Blacklisted Token',17,'add_blacklistedtoken'),(66,'Can change Blacklisted Token',17,'change_blacklistedtoken'),(67,'Can delete Blacklisted Token',17,'delete_blacklistedtoken'),(68,'Can view Blacklisted Token',17,'view_blacklistedtoken'),(69,'Can add Outstanding Token',18,'add_outstandingtoken'),(70,'Can change Outstanding Token',18,'change_outstandingtoken'),(71,'Can delete Outstanding Token',18,'delete_outstandingtoken'),(72,'Can view Outstanding Token',18,'view_outstandingtoken');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `id` char(32) NOT NULL,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES ('02000000000000000000000000000003','Cát & Sỏi'),('02000000000000000000000000000010','Đinh vít & Bu lông'),('02000000000000000000000000000002','Gạch & Đá'),('02000000000000000000000000000008','Gỗ & Ván ép'),('02000000000000000000000000000005','Ống nhựa & Phụ kiện'),('02000000000000000000000000000004','Sắt thép xây dựng'),('02000000000000000000000000000006','Sơn & Chống thấm'),('02000000000000000000000000000007','Tấm lợp & Mái'),('02000000000000000000000000000009','Vật liệu cách nhiệt'),('02000000000000000000000000000001','Xi măng & Vữa');
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` char(32) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_users_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
INSERT INTO `django_admin_log` VALUES (1,'2026-04-08 08:15:54.243409','01000000-0000-0000-0000-000000000009','ketoan01',2,'[{\"changed\": {\"fields\": [\"Staff status\"]}}]',9,'01000000000000000000000000000002'),(2,'2026-04-08 08:22:59.487135','01000000-0000-0000-0000-000000000009','ketoan01',2,'[{\"changed\": {\"fields\": [\"Staff status\"]}}]',9,'01000000000000000000000000000002');
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(2,'auth','group'),(3,'auth','permission'),(9,'authentication','user'),(4,'contenttypes','contenttype'),(6,'product','category'),(10,'product','customerdebt'),(11,'product','exportlog'),(12,'product','inventory'),(7,'product','product'),(8,'product','productunit'),(13,'product','salesorder'),(14,'product','systemlog'),(15,'product','warehouse'),(16,'product','warehousetransaction'),(5,'sessions','session'),(17,'token_blacklist','blacklistedtoken'),(18,'token_blacklist','outstandingtoken');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2026-03-23 07:39:45.101094'),(2,'contenttypes','0002_remove_content_type_name','2026-03-23 07:39:45.246313'),(3,'auth','0001_initial','2026-03-23 07:39:45.866918'),(4,'auth','0002_alter_permission_name_max_length','2026-03-23 07:39:45.965114'),(5,'auth','0003_alter_user_email_max_length','2026-03-23 07:39:45.974471'),(6,'auth','0004_alter_user_username_opts','2026-03-23 07:39:45.981492'),(7,'auth','0005_alter_user_last_login_null','2026-03-23 07:39:45.988828'),(8,'auth','0006_require_contenttypes_0002','2026-03-23 07:39:45.993822'),(9,'auth','0007_alter_validators_add_error_messages','2026-03-23 07:39:46.000798'),(10,'auth','0008_alter_user_username_max_length','2026-03-23 07:39:46.007906'),(11,'auth','0009_alter_user_last_name_max_length','2026-03-23 07:39:46.015109'),(12,'auth','0010_alter_group_name_max_length','2026-03-23 07:39:46.030855'),(13,'auth','0011_update_proxy_permissions','2026-03-23 07:39:46.037147'),(14,'auth','0012_alter_user_first_name_max_length','2026-03-23 07:39:46.044047'),(15,'authentication','0001_initial','2026-03-23 07:39:46.637343'),(16,'admin','0001_initial','2026-03-23 07:39:46.884249'),(17,'admin','0002_logentry_remove_auto_add','2026-03-23 07:39:46.901772'),(18,'admin','0003_logentry_add_action_flag_choices','2026-03-23 07:39:46.910695'),(19,'product','0001_initial','2026-03-23 07:39:47.237996'),(20,'sessions','0001_initial','2026-03-23 07:39:47.296813'),(21,'product','0002_warehouse_exportlog_salesorder_customerdebt_and_more','2026-03-23 07:51:14.177832'),(22,'product','0002_remove_exportlog_user_and_more','2026-04-06 03:01:33.618459'),(23,'token_blacklist','0001_initial','2026-04-06 03:01:33.923635'),(24,'token_blacklist','0002_outstandingtoken_jti_hex','2026-04-06 03:01:34.012718'),(25,'token_blacklist','0003_auto_20171017_2007','2026-04-06 03:01:34.029049'),(26,'token_blacklist','0004_auto_20171017_2013','2026-04-06 03:01:34.149225'),(27,'token_blacklist','0005_remove_outstandingtoken_jti','2026-04-06 03:01:34.234609'),(28,'token_blacklist','0006_auto_20171017_2113','2026-04-06 03:01:34.269839'),(29,'token_blacklist','0007_auto_20171017_2214','2026-04-06 03:01:34.574716'),(30,'token_blacklist','0008_migrate_to_bigautofield','2026-04-06 03:01:35.006040'),(31,'token_blacklist','0010_fix_migrate_to_bigautofield','2026-04-06 03:01:35.018538'),(32,'token_blacklist','0011_linearizes_history','2026-04-06 03:01:35.024010'),(33,'token_blacklist','0012_alter_outstandingtoken_user','2026-04-06 03:01:35.034786'),(34,'token_blacklist','0013_alter_blacklistedtoken_options_and_more','2026-04-06 03:01:35.047618');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('apqfxjr8z9xrjdizft12kycli1sl0f2v','.eJxVjjsOwjAQBe_iGlte2xtjSnrOEK29axJAiZRPhbg7iZQC6jczem_V0rp07TrL1PasLipZayk51BE56UBN0lRYNKSKOeIZQgF1-tUylacMu8sPGu6jKeOwTH02O2KOdTa3keV1Pdi_QEdzt9leoAJECWQlbCcKBG6qiwlrDhXRlmgJ2KGvGF0qxAExOy8ZofHeq88Xqo1APw:1w6Rcj:T98F0yC38yKBhdho_cGRyvK0emNbLezPmc__-E7r2bw','2026-04-11 11:14:37.388088'),('dt6h4kqu99q4zdxxo118c574k38hgx9d','.eJxtjMEOwiAQRP-FsxJaQLoevfsNZGG3UjWQlPZk_Hdb7UET5zCXeW8ewuM8JT9XHv1A4ihUo97Z_6lPGiV231rAeOO8unTFfCkyljyNQ5ArIre1ynMhvp829ucgYU2Lba0NEAAcA_bYojIHIjAIELWxjh0pJmRSgNgZbHVk0xGHnskspcXzBTwQP-o:1wAOFH:5OMoyNeAmuYjK8Io-uemWDS2bq4BMup7mQuJhLJnEok','2026-04-22 08:26:43.874791');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product_units`
--

DROP TABLE IF EXISTS `product_units`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_units` (
  `id` char(32) NOT NULL,
  `unit_name` varchar(100) NOT NULL,
  `conversion_rate` decimal(19,4) NOT NULL,
  `product_id` char(32) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `product_units_product_id_4dead36d_fk_products_id` (`product_id`),
  CONSTRAINT `product_units_product_id_4dead36d_fk_products_id` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_units`
--

LOCK TABLES `product_units` WRITE;
/*!40000 ALTER TABLE `product_units` DISABLE KEYS */;
INSERT INTO `product_units` VALUES ('04000000000000000000000000000001','Bao',1.0000,'03000000000000000000000000000001'),('04000000000000000000000000000002','Pallet',50.0000,'03000000000000000000000000000001'),('04000000000000000000000000000003','Viên',1.0000,'03000000000000000000000000000004'),('04000000000000000000000000000004','Xe',10000.0000,'03000000000000000000000000000004'),('04000000000000000000000000000005','Khối',1.0000,'03000000000000000000000000000007'),('04000000000000000000000000000006','Tấn',0.6667,'03000000000000000000000000000007'),('04000000000000000000000000000007','Cây',1.0000,'03000000000000000000000000000010'),('04000000000000000000000000000008','Bó',10.0000,'03000000000000000000000000000010'),('04000000000000000000000000000009','Thùng',1.0000,'03000000000000000000000000000015'),('04000000000000000000000000000010','Lít',0.0556,'03000000000000000000000000000015');
/*!40000 ALTER TABLE `product_units` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `products` (
  `id` char(32) NOT NULL,
  `name` varchar(255) NOT NULL,
  `base_price` decimal(19,4) NOT NULL,
  `image_url` varchar(255) DEFAULT NULL,
  `base_unit` varchar(50) NOT NULL,
  `category_id` char(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `products_category_id_a7a3a156_fk_categories_id` (`category_id`),
  CONSTRAINT `products_category_id_a7a3a156_fk_categories_id` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
INSERT INTO `products` VALUES ('03000000000000000000000000000001','Xi măng Hà Tiên PCB40 50kg',95000.0000,NULL,'Bao','02000000000000000000000000000001'),('03000000000000000000000000000002','Xi măng Bỉm Sơn PCB40 50kg',92000.0000,'ximang_bimson.jpg','Bao','02000000000000000000000000000001'),('03000000000000000000000000000003','Vữa xây tô khô trộn sẵn 25kg',55000.0000,'vua_kho.jpg','Bao','02000000000000000000000000000001'),('03000000000000000000000000000004','Gạch đặc 4 lỗ 6x10x22cm',1200.0000,'gach_4lo.jpg','Viên','02000000000000000000000000000002'),('03000000000000000000000000000005','Gạch ống 6 lỗ 8x8x19cm',900.0000,'gach_6lo.jpg','Viên','02000000000000000000000000000002'),('03000000000000000000000000000006','Đá dăm 1x2 xây dựng',280000.0000,'da_dam.jpg','Khối','02000000000000000000000000000002'),('03000000000000000000000000000007','Cát vàng xây dựng (hạt to)',220000.0000,'cat_vang.jpg','Khối','02000000000000000000000000000003'),('03000000000000000000000000000008','Cát mịn tô trát',195000.0000,'cat_min.jpg','Khối','02000000000000000000000000000003'),('03000000000000000000000000000009','Sỏi rửa đổ bê tông 1x2',260000.0000,'soi_betong.jpg','Khối','02000000000000000000000000000003'),('03000000000000000000000000000010','Thép cây phi 10 dài 11.7m (Hòa Phát)',185000.0000,'thep_phi10.jpg','Cây','02000000000000000000000000000004'),('03000000000000000000000000000011','Thép cây phi 12 dài 11.7m (Hòa Phát)',265000.0000,'thep_phi12.jpg','Cây','02000000000000000000000000000004'),('03000000000000000000000000000012','Lưới thép hàn phi 4 ô 15x15cm',320000.0000,'luoi_thep.jpg','Tấm','02000000000000000000000000000004'),('03000000000000000000000000000013','Ống nhựa PVC Tiền Phong D114 4m',185000.0000,'ong_pvc_114.jpg','Cây','02000000000000000000000000000005'),('03000000000000000000000000000014','Ống nhựa PVC Tiền Phong D60 4m',95000.0000,'ong_pvc_60.jpg','Cây','02000000000000000000000000000005'),('03000000000000000000000000000015','Sơn nước nội thất Dulux 5 Easy 18L',850000.0000,'son_dulux18l.jpg','Thùng','02000000000000000000000000000006'),('03000000000000000000000000000016','Chống thấm Sika Latex 5kg',420000.0000,'sika_latex5kg.jpg','Thùng','02000000000000000000000000000006'),('03000000000000000000000000000017','Tôn lạnh 0.4mm dài 3m (Hoa Sen)',185000.0000,'ton_hoasen.jpg','Tấm','02000000000000000000000000000007'),('03000000000000000000000000000018','Tấm Fibro xi măng sóng nhỏ 2.4m',120000.0000,'fibro_ximang.jpg','Tấm','02000000000000000000000000000007'),('03000000000000000000000000000019','Ván ép 12ly 1220x2440mm',320000.0000,'van_ep_12ly.jpg','Tấm','02000000000000000000000000000008'),('03000000000000000000000000000020','Đinh thép 7cm (1kg)',28000.0000,'dinh_thep_7cm.jpg','Kg','02000000000000000000000000000010');
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `token_blacklist_blacklistedtoken`
--

DROP TABLE IF EXISTS `token_blacklist_blacklistedtoken`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `token_blacklist_blacklistedtoken` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `blacklisted_at` datetime(6) NOT NULL,
  `token_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token_id` (`token_id`),
  CONSTRAINT `token_blacklist_blacklistedtoken_token_id_3cc7fe56_fk` FOREIGN KEY (`token_id`) REFERENCES `token_blacklist_outstandingtoken` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `token_blacklist_blacklistedtoken`
--

LOCK TABLES `token_blacklist_blacklistedtoken` WRITE;
/*!40000 ALTER TABLE `token_blacklist_blacklistedtoken` DISABLE KEYS */;
/*!40000 ALTER TABLE `token_blacklist_blacklistedtoken` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `token_blacklist_outstandingtoken`
--

DROP TABLE IF EXISTS `token_blacklist_outstandingtoken`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `token_blacklist_outstandingtoken` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `token` longtext NOT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `expires_at` datetime(6) NOT NULL,
  `user_id` char(32) DEFAULT NULL,
  `jti` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token_blacklist_outstandingtoken_jti_hex_d9bdf6f7_uniq` (`jti`),
  KEY `token_blacklist_outstandingtoken_user_id_83bc629a_fk_users_id` (`user_id`),
  CONSTRAINT `token_blacklist_outstandingtoken_user_id_83bc629a_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `token_blacklist_outstandingtoken`
--

LOCK TABLES `token_blacklist_outstandingtoken` WRITE;
/*!40000 ALTER TABLE `token_blacklist_outstandingtoken` DISABLE KEYS */;
INSERT INTO `token_blacklist_outstandingtoken` VALUES (1,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc3ODAzNjUyMSwiaWF0IjoxNzc1NDQ0NTIxLCJqdGkiOiJiMzFiZTE4MjlhNDI0MjIzYjEyNGU0NTJlMDhiODE0NyIsInVzZXJfaWQiOiI5MDAwYTkyNS03NWQ5LTRhNjktYWNkZS0xOWY1Yjc1ODE0YzEifQ.loY_2mpkpkqMkUo8Bx1J9LpFpnKQlrKNyaA2RkySLZo','2026-04-06 03:02:01.818673','2026-05-06 03:02:01.000000','9000a92575d94a69acde19f5b75814c1','b31be1829a424223b124e452e08b8147'),(2,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc3ODAzNzMyNiwiaWF0IjoxNzc1NDQ1MzI2LCJqdGkiOiJkOGY4OTgwNWI0ZDQ0OWEzODJjMWUyYWY0ZjA2MDMwNiIsInVzZXJfaWQiOiIwMTAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDIifQ.KcbG8JWYBuqHNbzoz-XI9uFPCEVbBf_05vQko3XC6qw','2026-04-06 03:15:26.700342','2026-05-06 03:15:26.000000','01000000000000000000000000000002','d8f89805b4d449a382c1e2af4f060306'),(3,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc3ODAzNzMzOCwiaWF0IjoxNzc1NDQ1MzM4LCJqdGkiOiJhYjkyZWIyYjRlNDM0OTc1OTIxN2UxNTRiZTc1OWMwNCIsInVzZXJfaWQiOiIwMTAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDYifQ.-C3y_pnnKhZaup91YPVNnqzEW45m_TT0l01z8om5ibU','2026-04-06 03:15:38.171420','2026-05-06 03:15:38.000000','01000000000000000000000000000006','ab92eb2b4e4349759217e154be759c04'),(4,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc3ODIyODAzMywiaWF0IjoxNzc1NjM2MDMzLCJqdGkiOiJlMmViYTgzNjczYzg0OTkwYTIwOGI2OTZjYjgzYTgzOSIsInVzZXJfaWQiOiIwMTAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDIifQ.g77yBXMlICHmpjiy6BZx9PJi1TCai4MX0LnoO6UE3bM','2026-04-08 08:13:53.192510','2026-05-08 08:13:53.000000','01000000000000000000000000000002','e2eba83673c84990a208b696cb83a839'),(5,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc3ODIyODA5MSwiaWF0IjoxNzc1NjM2MDkxLCJqdGkiOiJiOWQzNjk5YzhiY2M0MDI1OWIxMDZjYmFmNjBkMGQ5NiIsInVzZXJfaWQiOiIwMTAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDIifQ.MWzXOlj0ukHtCRoXPMU73hftOj6XeR5CaNd0r4m1XSQ','2026-04-08 08:14:51.689585','2026-05-08 08:14:51.000000','01000000000000000000000000000002','b9d3699c8bcc40259b106cbaf60d0d96'),(6,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc3ODIyODU1OCwiaWF0IjoxNzc1NjM2NTU4LCJqdGkiOiI4YTE3NmI2MjFlMWU0MzMwYjYzZDk4YjY2MThjMjNjNCIsInVzZXJfaWQiOiIwMTAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDYifQ.4htnvQ2wD4u20caVfF3_QSX_ilgPscsOjR1aMwVuG_s','2026-04-08 08:22:38.694598','2026-05-08 08:22:38.000000','01000000000000000000000000000006','8a176b621e1e4330b63d98b6618c23c4'),(7,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc3ODIyODU5OCwiaWF0IjoxNzc1NjM2NTk4LCJqdGkiOiI0OTUwNzNiOGY1YmU0ZWYyOTM4MThhYjRiNWRkZDcwZCIsInVzZXJfaWQiOiIwMTAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDMifQ.br7Eocpe92zebmfFvUdDOXlQxqkc1vkSe8oOTdSOOxI','2026-04-08 08:23:18.719339','2026-05-08 08:23:18.000000','01000000000000000000000000000003','495073b8f5be4ef293818ab4b5ddd70d'),(8,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc3ODIyODYxMSwiaWF0IjoxNzc1NjM2NjExLCJqdGkiOiIyOTFjYTlkODdmNzM0OTAyOTVmMmY4NTkxOTAwMzI5YyIsInVzZXJfaWQiOiIwMTAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDQifQ.rbZsb9wwe8UgHSfICksBpqmRiB9KBFNaVHXbKop9PXg','2026-04-08 08:23:31.036421','2026-05-08 08:23:31.000000','01000000000000000000000000000004','291ca9d87f73490295f2f8591900329c'),(9,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc3ODIyODYyMiwiaWF0IjoxNzc1NjM2NjIyLCJqdGkiOiJjNjJhZDk5YmVkY2Q0MDE3ODQ0NDc4ZWIyMThhMzJjNSIsInVzZXJfaWQiOiIwMTAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDUifQ.W9hvlG0nR2cyXxkjzY50gfL5JKyqiL-oNYRle-yHlJo','2026-04-08 08:23:42.320343','2026-05-08 08:23:42.000000','01000000000000000000000000000005','c62ad99bedcd4017844478eb218a32c5'),(10,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc3ODIyODY0OSwiaWF0IjoxNzc1NjM2NjQ5LCJqdGkiOiI0ZmZlM2VlNmNkOTU0OWQ2YjZlODUxZmNlNWIwZjk0OSIsInVzZXJfaWQiOiIwMTAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDYifQ.lD-i6r3CHS4-3gJvj67FU_WtUxKyrsNnMqs0HEXdMwk','2026-04-08 08:24:09.927339','2026-05-08 08:24:09.000000','01000000000000000000000000000006','4ffe3ee6cd9549d6b6e851fce5b0f949'),(11,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc3ODIyODY1OCwiaWF0IjoxNzc1NjM2NjU4LCJqdGkiOiI2Y2U1YmY1MTIwMDE0NzMwYTAxNzA3NjE4ZGQxZTkzMiIsInVzZXJfaWQiOiIwMTAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDcifQ.c-FQ3Nqr2iP_Q7UWxPwJBAEkAr2y3pLkxXpjJ0RAOww','2026-04-08 08:24:18.897129','2026-05-08 08:24:18.000000','01000000000000000000000000000007','6ce5bf5120014730a01707618dd1e932'),(12,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc3ODIyODY2NiwiaWF0IjoxNzc1NjM2NjY2LCJqdGkiOiJjMDZmYTJlZGVmNjE0NjM4OTA2YjAyZjVkNGU4NTliZSIsInVzZXJfaWQiOiIwMTAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDgifQ.lKDZNnpTtwPeck5EVP5kUUC4q5-APZAK3nEXySBX7gw','2026-04-08 08:24:26.390588','2026-05-08 08:24:26.000000','01000000000000000000000000000008','c06fa2edef614638906b02f5d4e859be'),(13,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc3ODIyODc5NCwiaWF0IjoxNzc1NjM2Nzk0LCJqdGkiOiI4N2RmMTg4MTA2MGY0YTk1YjM2MDQxOTViZGE1NDZkYSIsInVzZXJfaWQiOiIwMTAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMDkifQ.KbubVr7YuX0rC8D_OAah1gd__RxOW4rCegBqHW-hF8A','2026-04-08 08:26:34.947476','2026-05-08 08:26:34.000000','01000000000000000000000000000009','87df1881060f4a95b3604195bda546da'),(14,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc3ODIyODgwMywiaWF0IjoxNzc1NjM2ODAzLCJqdGkiOiI0ODgzZDIzY2RhYTM0YTMzYTJjMzU3YmM5MDQ2OWQzYSIsInVzZXJfaWQiOiIwMTAwMDAwMC0wMDAwLTAwMDAtMDAwMC0wMDAwMDAwMDAwMTAifQ.3H77PhSLeG1bA2BLOv0tHoNlwFUVk8D3usrHADJrJ6E','2026-04-08 08:26:43.804368','2026-05-08 08:26:43.000000','01000000000000000000000000000010','4883d23cdaa34a33a2c357bc90469d3a');
/*!40000 ALTER TABLE `token_blacklist_outstandingtoken` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `id` char(32) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `phone_number` varchar(20) DEFAULT NULL,
  `address` longtext,
  `role` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES ('pbkdf2_sha256$1200000$9u8MwuLVoJrS1zj2QKQ5CL$ohjkR597ClPlHvyAqJW8wMfSNdbMAYnBdglTiKsCd5A=','2026-04-08 08:22:46.851125',1,'admin02','Hùng','Trần','admin02@vlxd.vn',1,1,'2024-01-02 08:00:00.000000','01000000000000000000000000000002','Trần Văn Hùng','0901000002','45 Nguyễn Huệ, Q1, TP.HCM','ADMIN'),('pbkdf2_sha256$1200000$2LF0VtcwORedFl6Snm6dHC$cCN8dA24y4+O9qjhBlLHRIwz9huMCbLdnvq7rsHnm/g=','2026-04-08 08:23:18.784835',0,'sale01','Lan','Phạm','sale01@vlxd.vn',0,1,'2024-01-05 08:00:00.000000','01000000000000000000000000000003','Phạm Thị Lan','0902000001','78 Trần Hưng Đạo, Q5, TP.HCM','SALE'),('pbkdf2_sha256$1200000$8u7u81wH2F8IWU0xq25PDJ$2NCSa490b+W3pFyh8gzzCxxCwEpIVtpHtxPLTMxz50U=','2026-04-08 08:23:31.097083',0,'sale02','Hoa','Lê','sale02@vlxd.vn',0,1,'2024-01-06 08:00:00.000000','01000000000000000000000000000004','Lê Thị Hoa','0902000002','23 Đinh Tiên Hoàng, Q1, TP.HCM','SALE'),('pbkdf2_sha256$1200000$W0oJlI10twTfo13G1PJrzF$qcbfUykm0OCA2nahl6ltZ0rPOXUmW34evbxRpBq/2eM=','2026-04-08 08:23:42.379561',0,'sale03','Tuấn','Đỗ','sale03@vlxd.vn',0,1,'2024-01-07 08:00:00.000000','01000000000000000000000000000005','Đỗ Văn Tuấn','0902000003','56 Lý Thường Kiệt, Q10, TP.HCM','SALE'),('pbkdf2_sha256$1200000$53nkEzUNqnGdqy5SHQl3QB$7vaQQEMNl7QLB0eoCJH5TqBfXi7SwLfssfwTHDIwhtA=','2026-04-08 08:24:09.948377',0,'kho01','Nam','Hoàng','kho01@vlxd.vn',0,1,'2024-01-10 08:00:00.000000','01000000000000000000000000000006','Hoàng Văn Nam','0903000001','11 Điện Biên Phủ, Bình Thạnh, TP.HCM','KHO'),('pbkdf2_sha256$1200000$kxmEJvSKxUbeyNDjYy7efU$k8/bI3JaqlHgsaK63Kr4c6ng5l9sOzR6R5BzCkF79ms=','2026-04-08 08:24:18.962386',0,'kho02','Dũng','Ngô','kho02@vlxd.vn',0,1,'2024-01-11 08:00:00.000000','01000000000000000000000000000007','Ngô Văn Dũng','0903000002','22 Hoàng Văn Thụ, Phú Nhuận, TP.HCM','KHO'),('pbkdf2_sha256$1200000$TCS6yOUNwiPhqMTOzcpF7M$hohmEplH/q0xyfzC0eZmu45x6Ym7HYNl7Z+xV0nAYHA=','2026-04-08 08:24:26.455073',0,'kho03','Hiền','Đinh','kho03@vlxd.vn',0,1,'2024-01-12 08:00:00.000000','01000000000000000000000000000008','Đinh Thị Hiền','0903000003','67 Lê Văn Sỹ, Q3, TP.HCM','KHO'),('pbkdf2_sha256$1200000$aMo8r37ELqYvRyCBwZ9ZS4$5KAZbtS2U7XIwehcga4IcBBxzS3kFdkajer8nmoHg2E=','2026-04-08 08:26:35.006789',0,'ketoan01','Thu','Phan','ketoan01@vlxd.vn',0,1,'2024-01-15 08:00:00.000000','01000000000000000000000000000009','Phan Thị Thu','0904000001','44 Nguyễn Đình Chiểu, Q3, TP.HCM','KE_TOAN'),('pbkdf2_sha256$1200000$gIceKEkYYQNfU2WW8kpyJT$PxfOk2uD9OUv9rqFw20d3FSyxeE8YfY9v6L4AiFpkmA=','2026-04-08 08:26:43.866574',0,'ketoan02','Hằng','Vũ','ketoan02@vlxd.vn',0,1,'2024-01-16 08:00:00.000000','01000000000000000000000000000010','Vũ Thị Hằng','0904000002','77 Bà Huyện Thanh Quan, Q3, TP.HCM','KE_TOAN'),('pbkdf2_sha256$1200000$9u8MwuLVoJrS1zj2QKQ5CL$ohjkR597ClPlHvyAqJW8wMfSNdbMAYnBdglTiKsCd5A=','2026-04-06 03:02:27.394312',1,'admin','','','',1,1,'2026-03-23 08:16:05.150846','9000a92575d94a69acde19f5b75814c1','',NULL,NULL,'');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users_groups`
--

DROP TABLE IF EXISTS `users_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` char(32) NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_groups_user_id_group_id_fc7788e8_uniq` (`user_id`,`group_id`),
  KEY `users_groups_group_id_2f3517aa_fk_auth_group_id` (`group_id`),
  CONSTRAINT `users_groups_group_id_2f3517aa_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `users_groups_user_id_f500bee5_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users_groups`
--

LOCK TABLES `users_groups` WRITE;
/*!40000 ALTER TABLE `users_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `users_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users_user_permissions`
--

DROP TABLE IF EXISTS `users_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` char(32) NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_user_permissions_user_id_permission_id_3b86cbdf_uniq` (`user_id`,`permission_id`),
  KEY `users_user_permissio_permission_id_6d08dcd2_fk_auth_perm` (`permission_id`),
  CONSTRAINT `users_user_permissio_permission_id_6d08dcd2_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `users_user_permissions_user_id_92473840_fk_users_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users_user_permissions`
--

LOCK TABLES `users_user_permissions` WRITE;
/*!40000 ALTER TABLE `users_user_permissions` DISABLE KEYS */;
INSERT INTO `users_user_permissions` VALUES (8,'01000000000000000000000000000003',24),(10,'01000000000000000000000000000003',28),(9,'01000000000000000000000000000003',32),(11,'01000000000000000000000000000004',24),(13,'01000000000000000000000000000004',28),(12,'01000000000000000000000000000004',32),(14,'01000000000000000000000000000005',24),(16,'01000000000000000000000000000005',28),(15,'01000000000000000000000000000005',32),(2,'01000000000000000000000000000006',24),(3,'01000000000000000000000000000006',25),(4,'01000000000000000000000000000006',26),(5,'01000000000000000000000000000006',28),(6,'01000000000000000000000000000006',29),(1,'01000000000000000000000000000006',32),(18,'01000000000000000000000000000007',24),(19,'01000000000000000000000000000007',25),(20,'01000000000000000000000000000007',26),(21,'01000000000000000000000000000007',28),(22,'01000000000000000000000000000007',29),(17,'01000000000000000000000000000007',32),(24,'01000000000000000000000000000008',24),(25,'01000000000000000000000000000008',25),(26,'01000000000000000000000000000008',26),(27,'01000000000000000000000000000008',28),(28,'01000000000000000000000000000008',29),(23,'01000000000000000000000000000008',32),(30,'01000000000000000000000000000009',28),(31,'01000000000000000000000000000010',28);
/*!40000 ALTER TABLE `users_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-08 15:29:13
