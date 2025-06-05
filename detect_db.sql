-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 05, 2025 at 09:28 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.1.25

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `detect_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `detections`
--

CREATE TABLE `detections` (
  `id` int(11) NOT NULL,
  `camera_id` varchar(100) NOT NULL,
  `timestamp` datetime NOT NULL,
  `confidence` float NOT NULL,
  `image_path` text DEFAULT NULL,
  `created_at` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `detections`
--

INSERT INTO `detections` (`id`, `camera_id`, `timestamp`, `confidence`, `image_path`, `created_at`) VALUES
(288, 'Front Gate Camera', '2025-06-04 10:58:39', 80.24, '20250604/Front_Gate_Camera/person_20250604_105832_322_80.jpg', '2025-06-04 10:58:39'),
(303, 'Main Entrance', '2025-06-04 11:01:37', 59.33, '20250604/Main_Entrance/person_20250604_110135_161_59.jpg', '2025-06-04 11:01:37'),
(304, 'Main Entrance', '2025-06-04 11:01:47', 61.01, '20250604/Main_Entrance/person_20250604_110145_524_61.jpg', '2025-06-04 11:01:47'),
(305, 'Main Entrance', '2025-06-04 11:01:52', 61.03, '20250604/Main_Entrance/person_20250604_110150_694_61.jpg', '2025-06-04 11:01:52'),
(306, 'Front Gate Camera', '2025-06-05 11:47:12', 87.8, '20250605/Front_Gate_Camera/person_20250605_114706_375_88.jpg', '2025-06-05 11:47:12'),
(307, 'Front Gate Camera', '2025-06-05 11:47:15', 88.48, '20250605/Front_Gate_Camera/person_20250605_114712_997_88.jpg', '2025-06-05 11:47:15'),
(308, 'Front Gate Camera', '2025-06-05 11:47:17', 87.85, '20250605/Front_Gate_Camera/person_20250605_114715_093_88.jpg', '2025-06-05 11:47:17'),
(309, 'Front Gate Camera', '2025-06-05 11:47:19', 88.48, '20250605/Front_Gate_Camera/person_20250605_114717_182_88.jpg', '2025-06-05 11:47:19'),
(310, 'Main Entrance', '2025-06-05 11:58:00', 84.56, '20250605/Main_Entrance/person_20250605_115753_446_85.jpg', '2025-06-05 11:58:00'),
(311, 'Main Entrance', '2025-06-05 11:58:02', 67.39, '20250605/Main_Entrance/person_20250605_115800_890_67.jpg', '2025-06-05 11:58:02'),
(312, 'Main Entrance', '2025-06-05 11:58:04', 79.9, '20250605/Main_Entrance/person_20250605_115802_949_80.jpg', '2025-06-05 11:58:04'),
(313, 'Main Entrance', '2025-06-05 12:03:34', 67.25, '20250605/Main_Entrance/person_20250605_120300_854_67.jpg', '2025-06-05 12:03:34'),
(314, 'Main Entrance', '2025-06-05 12:03:40', 60.16, '20250605/Main_Entrance/person_20250605_120334_151_60.jpg', '2025-06-05 12:03:40'),
(315, 'Main Entrance', '2025-06-05 12:03:42', 73.2, '20250605/Main_Entrance/person_20250605_120340_906_73.jpg', '2025-06-05 12:03:42'),
(316, 'Main Entrance', '2025-06-05 12:03:44', 57.19, '20250605/Main_Entrance/person_20250605_120342_961_57.jpg', '2025-06-05 12:03:44'),
(317, 'Main Entrance', '2025-06-05 12:03:47', 63.08, '20250605/Main_Entrance/person_20250605_120344_993_63.jpg', '2025-06-05 12:03:47'),
(318, 'Main Entrance', '2025-06-05 12:04:38', 62.32, '20250605/Main_Entrance/person_20250605_120431_966_62.jpg', '2025-06-05 12:04:38'),
(319, 'Front Gate Camera', '2025-06-05 12:04:43', 66.04, '20250605/Front_Gate_Camera/person_20250605_120441_046_66.jpg', '2025-06-05 12:04:43'),
(320, 'Front Gate Camera', '2025-06-05 12:04:45', 84.6, '20250605/Front_Gate_Camera/person_20250605_120443_883_85.jpg', '2025-06-05 12:04:45'),
(321, 'Front Gate Camera', '2025-06-05 12:04:47', 83.44, '20250605/Front_Gate_Camera/person_20250605_120445_931_83.jpg', '2025-06-05 12:04:47'),
(322, 'Front Gate Camera', '2025-06-05 12:04:49', 83.83, '20250605/Front_Gate_Camera/person_20250605_120447_971_84.jpg', '2025-06-05 12:04:49'),
(323, 'Front Gate Camera', '2025-06-05 12:04:52', 74.44, '20250605/Front_Gate_Camera/person_20250605_120450_001_74.jpg', '2025-06-05 12:04:52'),
(324, 'Front Gate Camera', '2025-06-05 12:04:54', 83.44, '20250605/Front_Gate_Camera/person_20250605_120452_047_83.jpg', '2025-06-05 12:04:54'),
(325, 'Front Gate Camera', '2025-06-05 12:04:56', 83.34, '20250605/Front_Gate_Camera/person_20250605_120454_085_83.jpg', '2025-06-05 12:04:56'),
(326, 'Front Gate Camera', '2025-06-05 12:04:58', 86.65, '20250605/Front_Gate_Camera/person_20250605_120456_110_87.jpg', '2025-06-05 12:04:58'),
(327, 'Front Gate Camera', '2025-06-05 12:05:00', 84.14, '20250605/Front_Gate_Camera/person_20250605_120458_143_84.jpg', '2025-06-05 12:05:00'),
(328, 'Front Gate Camera', '2025-06-05 12:05:02', 84.42, '20250605/Front_Gate_Camera/person_20250605_120500_183_84.jpg', '2025-06-05 12:05:02'),
(329, 'Front Gate Camera', '2025-06-05 12:05:19', 75.05, '20250605/Front_Gate_Camera/person_20250605_120502_225_75.jpg', '2025-06-05 12:05:19'),
(330, 'Front Gate Camera', '2025-06-05 12:05:22', 75.62, '20250605/Front_Gate_Camera/person_20250605_120519_701_76.jpg', '2025-06-05 12:05:22'),
(331, 'Main Entrance', '2025-06-05 12:05:23', 67.93, '20250605/Main_Entrance/person_20250605_120521_298_68.jpg', '2025-06-05 12:05:23'),
(332, 'Front Gate Camera', '2025-06-05 12:05:25', 63.03, '20250605/Front_Gate_Camera/person_20250605_120522_994_63.jpg', '2025-06-05 12:05:25'),
(333, 'Main Entrance', '2025-06-05 12:05:25', 68.9, '20250605/Main_Entrance/person_20250605_120523_348_69.jpg', '2025-06-05 12:05:25'),
(334, 'Front Gate Camera', '2025-06-05 12:05:27', 77.7, '20250605/Front_Gate_Camera/person_20250605_120525_036_78.jpg', '2025-06-05 12:05:27'),
(335, 'Front Gate Camera', '2025-06-05 12:05:29', 63, '20250605/Front_Gate_Camera/person_20250605_120527_077_63.jpg', '2025-06-05 12:05:29'),
(336, 'Front Gate Camera', '2025-06-05 12:05:31', 61.9, '20250605/Front_Gate_Camera/person_20250605_120529_124_62.jpg', '2025-06-05 12:05:31'),
(337, 'Front Gate Camera', '2025-06-05 12:05:33', 63.36, '20250605/Front_Gate_Camera/person_20250605_120531_176_63.jpg', '2025-06-05 12:05:33');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `detections`
--
ALTER TABLE `detections`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_camera_timestamp` (`camera_id`,`timestamp`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `detections`
--
ALTER TABLE `detections`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=338;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
