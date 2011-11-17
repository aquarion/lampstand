-- MySQL dump 10.11
--
-- Host: localhost    Database: maelfroth
-- ------------------------------------------------------
-- Server version	5.0.51a-24+lenny5-log

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
-- Table structure for table `define`
--

DROP TABLE IF EXISTS `define`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `define` (
  `id` int(11) NOT NULL auto_increment,
  `word` varchar(255) NOT NULL,
  `definition` varchar(255) NOT NULL,
  `author` varchar(255) NOT NULL,
  `timestamp` tinytext NOT NULL,
  PRIMARY KEY  (`id`),
  KEY `word` (`word`)
) ENGINE=MyISAM AUTO_INCREMENT=1389 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `events`
--

DROP TABLE IF EXISTS `events`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `events` (
  `id` int(11) NOT NULL auto_increment,
  `creator` varchar(64) default NULL,
  `datetime` datetime default NULL,
  `description` varchar(255) default NULL,
  `class` varchar(64) default NULL,
  `datetime_end` datetime default NULL,
  `aliases` varchar(255) NOT NULL,
  `url` varchar(255) NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=147 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `gameaccounts`
--

DROP TABLE IF EXISTS `gameaccounts`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `gameaccounts` (
  `username` varchar(255) NOT NULL,
  `steamname` varchar(255) NOT NULL,
  `timestamp` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `hugReaction`
--

DROP TABLE IF EXISTS `hugReaction`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `hugReaction` (
  `username` varchar(64) NOT NULL default '',
  `item` varchar(255) default NULL,
  `date_modified` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  PRIMARY KEY  (`username`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `item`
--

DROP TABLE IF EXISTS `item`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `item` (
  `id` int(11) NOT NULL auto_increment,
  `item` varchar(255) character set utf8 collate utf8_unicode_ci NOT NULL,
  `date_created` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  `author` varchar(255) character set utf8 collate utf8_unicode_ci NOT NULL,
  PRIMARY KEY  (`id`),
  KEY `author` (`author`),
  KEY `item` (`item`)
) ENGINE=MyISAM AUTO_INCREMENT=598 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `lastquit`
--

DROP TABLE IF EXISTS `lastquit`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `lastquit` (
  `username` varchar(64) NOT NULL default '',
  `last_quit` bigint(20) default NULL,
  `reason` varchar(255) default NULL,
  `method` varchar(7) default NULL,
  `channel` varchar(31) character set utf8 collate utf8_unicode_ci NOT NULL,
  PRIMARY KEY  (`username`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `lastseen`
--

DROP TABLE IF EXISTS `lastseen`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `lastseen` (
  `username` varchar(64) NOT NULL default '',
  `last_seen` bigint(20) default NULL,
  `last_words` varchar(255) default NULL,
  `channel` varchar(16) NOT NULL,
  PRIMARY KEY  (`username`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `nickserv`
--

DROP TABLE IF EXISTS `nickserv`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `nickserv` (
  `server` varchar(255) NOT NULL,
  `password` varchar(255) default NULL,
  PRIMARY KEY  (`server`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `part`
--

DROP TABLE IF EXISTS `part`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `part` (
  `id` int(11) NOT NULL auto_increment,
  `title` tinytext NOT NULL,
  `author` int(10) unsigned default NULL,
  `dateadded` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  `content` mediumtext,
  `coolness` int(11) default NULL,
  `votes` mediumtext,
  `restricted` bit(1) default NULL,
  `story` int(10) unsigned default '0',
  `backto` int(10) unsigned default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `partlink`
--

DROP TABLE IF EXISTS `partlink`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `partlink` (
  `id` int(11) NOT NULL auto_increment,
  `linkto` int(11) NOT NULL,
  `linkfrom` int(11) NOT NULL,
  `linkname` tinytext NOT NULL,
  `linklock` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `revision`
--

DROP TABLE IF EXISTS `revision`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `revision` (
  `revision` int(10) unsigned NOT NULL auto_increment,
  `page` int(10) NOT NULL default '0',
  `content` mediumtext NOT NULL,
  `comment` tinytext,
  `creator` tinytext NOT NULL,
  `created` datetime NOT NULL default '0000-00-00 00:00:00',
  PRIMARY KEY  (`revision`)
) ENGINE=MyISAM AUTO_INCREMENT=501 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `urllist`
--

DROP TABLE IF EXISTS `urllist`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `urllist` (
  `username` varchar(64) default NULL,
  `time` float default NULL,
  `message` varchar(255) default NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `users` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `username` varchar(64) NOT NULL default '',
  `real_name` tinytext,
  `email` tinytext,
  `birthday` date default NULL,
  `password` tinytext,
  `location` int(11) default NULL,
  `last_access` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  `date_creation` timestamp NOT NULL default '0000-00-00 00:00:00',
  `access_level` int(11) default '0',
  `creationsite` varchar(255) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=84 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `vote`
--

DROP TABLE IF EXISTS `vote`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `vote` (
  `id` int(11) NOT NULL,
  `username` varchar(64) default NULL,
  `item` varchar(64) default NULL,
  `vote` tinyint(4) default NULL,
  `time` float default NULL,
  `textline` varchar(255) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `wikipage`
--

DROP TABLE IF EXISTS `wikipage`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `wikipage` (
  `page` int(10) unsigned NOT NULL auto_increment,
  `wiki` tinytext NOT NULL,
  `name` tinytext NOT NULL,
  `spinlock` bigint(20) default NULL,
  `created` datetime default NULL,
  `modified` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  `origin` tinytext,
  `yalelock` tinytext,
  PRIMARY KEY  (`page`)
) ENGINE=MyISAM AUTO_INCREMENT=131 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2011-11-17 10:24:29
