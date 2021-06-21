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

CREATE TABLE `stock_daily_info` (
  `id` bigint unsigned NOT NULL COMMENT '唯一id， 雪花算法',
  `symbol` varchar(10) NOT NULL COMMENT '股票代码',
  `name` varchar(24) NOT NULL COMMENT '股票名称',
  `exchange` varchar(8) NOT NULL COMMENT '股票市场',
  `timestamp` timestamp NOT NULL COMMENT '当前数据时间戳',
  `price` decimal(5) NOT NULL COMMENT '当前价格',
  `open_price` decimal(5) NOT NULL COMMENT '开盘价',
  `limit_up_price` decimal(5) NOT NULL COMMENT '最高价',
  `limit_low_price` decimal(5) NOT NULL COMMENT '最低价',
  `avg_price` decimal(5) NOT NULL COMMENT '均价',
  `last_close_price` decimal(5) NOT NULL COMMENT '昨日收盘价',
  `amplitude` decimal(5) NOT NULL COMMENT '振幅',
  `turnover_rate` decimal(5) NOT NULL COMMENT '换手率',
  `low52w` decimal(5) NOT NULL COMMENT '52周最低',
  `high52w` decimal(5) NOT NULL COMMENT '52周最高',
  `pb` decimal(5) NOT NULL COMMENT '市净率',
  `pe_ttm` decimal(5) NOT NULL COMMENT '市盈率（TTM）',
  `pe_lyr` decimal(5) NOT NULL COMMENT '市盈率（静）',
  `pe_forecast` decimal(5) NOT NULL COMMENT '市盈率（动）',
  `amount` decimal(5) NOT NULL COMMENT '成交额',
  `volume` decimal(5) NOT NULL COMMENT '成交量',
  `volume_ratio` decimal(5) NOT NULL COMMENT '量比（即时每分钟平均成交量与之前连续5天每分钟平均成交量的比较，而不是随意抽取某一天的成交量作为比较，所以能够客观真实地反映盘口成交异动及其力度。）',
  `pankou_ratio` decimal(5) NOT NULL COMMENT '委比',
  `total_shares` decimal(5) NOT NULL COMMENT '总股本',
  `float_shares` decimal(5) NOT NULL COMMENT '流通股',
  `market_capital` float NOT NULL COMMENT '总市值',
  `float_market_capital` float NOT NULL COMMENT '流通市值',
  `eps` decimal(5) NOT NULL COMMENT '每股净收益',
  `navps` decimal(5) NOT NULL COMMENT '每股净资产',
  `dividend` decimal(5) NOT NULL COMMENT '股息（TTM）',
  `dividend_yield` decimal(5) NOT NULL COMMENT '股息率（TTM）',
  `percent` decimal(5) NOT NULL COMMENT '当天涨幅',
  `current_year_percent` decimal(5) NOT NULL COMMENT '当年涨幅',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `symbol_timestamp` (`symbol`,`timestamp`),
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
