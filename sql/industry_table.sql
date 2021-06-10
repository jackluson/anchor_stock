CREATE TABLE `shen_wan_industry` (
  `id` bigint unsigned NOT NULL COMMENT '唯一id， 雪花算法',
  `industry_code` varchar(10) NOT NULL COMMENT '行业代码',
  `industry_name` varchar(24) NOT NULL COMMENT '行业名称',
	`industry_type` TINYINT(1) NOT NULL COMMENT '行业类型，0：一级分类；1：二级类型；2：三级类型',
	`p_industry_id` varchar(10) NOT NULL COMMENT '父级行业行业代码，如果是一级行业，为null',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uni_industry_code` (`industry_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
