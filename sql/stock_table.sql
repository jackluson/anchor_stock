CREATE TABLE `stock_industry` (
  `id` bigint unsigned NOT NULL COMMENT '唯一id， 雪花算法',
  `stock_code` varchar(10) NOT NULL COMMENT '股票代码',
  `stock_name` varchar(24) NOT NULL COMMENT '股票名称',
  `industry_code_first` varchar(10) NOT NULL COMMENT '一级行业代码',
  `industry_name_first` varchar(255) NOT NULL COMMENT '一级行业名称',
  `industry_code_second` varchar(10) NOT NULL COMMENT '二级级行业代码',
  `industry_name_second` varchar(255) NOT NULL COMMENT '二级行业名称',
  `industry_code_third` varchar(10) NOT NULL COMMENT '二级级行业代码',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `industry_name_third` varchar(255) NOT NULL COMMENT '三级行业名称',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uni_stock_code` (`stock_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
