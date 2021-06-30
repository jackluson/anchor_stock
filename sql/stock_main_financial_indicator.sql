CREATE TABLE `stock_main_financial_indicator` (
  `id` bigint unsigned NOT NULL COMMENT '唯一id， 雪花算法',
  `code` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '股票代码',
  `name` varchar(24) NOT NULL COMMENT '股票名称',
  `report_name` varchar(24) NOT NULL COMMENT '报告名称',
  `report_date` timestamp NOT NULL COMMENT '报告日期',
  `report_publish_date` timestamp NOT NULL COMMENT '报告公布时间',
	-- 关键指标
  `total_revenue` decimal(18,4) DEFAULT NULL COMMENT '营业收入',
  `total_revenue_yoy` decimal(16,4) DEFAULT NULL COMMENT '营业收入同比增长',
  `total_revenue_yoy_yoy` decimal(16,4) DEFAULT NULL COMMENT '营业收入同比增长的同比增长',
  `net_profit_atsopc` decimal(16,4) DEFAULT NULL COMMENT '净利润',
  `net_profit_atsopc_yoy` decimal(16,4) DEFAULT NULL COMMENT '净利润同比',
  `net_profit_atsopc_yoy_yoy` decimal(16,4) DEFAULT NULL COMMENT '净利润同比增长的同比',
  `net_selling_rate` decimal(16,4) DEFAULT NULL COMMENT '销售净利率',
  `net_selling_rate_yoy` decimal(16,4) DEFAULT NULL COMMENT '销售净利率同比',
  `gross_selling_rate` decimal(16,4) DEFAULT NULL COMMENT '销售毛利率',
  `gross_selling_rate_yoy` decimal(16,4) DEFAULT NULL COMMENT '销售毛利率同比',
  `net_profit_after_nrgal_atsolc` decimal(16,4) DEFAULT NULL COMMENT '扣非净利润',
  `net_profit_after_nrgal_atsolc_yoy` decimal(16,4) DEFAULT NULL COMMENT '扣非净利润同比增长',
  `net_profit_after_nrgal_atsolc_yoy_yoy` decimal(16,4) DEFAULT NULL COMMENT '扣非净利润同比增长的同比',
  `roe` decimal(16,4) DEFAULT NULL COMMENT '净资产收益率',
  `roe_yoy` decimal(16,4) DEFAULT NULL COMMENT '净资产收益率同比',
	-- 每股指标
  `np_per_share` decimal(16,4) DEFAULT NULL COMMENT '每股净资产',
  `np_per_share_yoy` decimal(16,4) DEFAULT NULL COMMENT '每股净资产同比',
  `operate_cash_flow_ps` decimal(16,4) DEFAULT NULL COMMENT '每股经营现金流',
  `operate_cash_flow_ps_yoy` decimal(16,4) DEFAULT NULL COMMENT '每股经营现金流同比',
  `basic_eps` decimal(16,4) DEFAULT NULL COMMENT '每股收益',
  `basic_eps_yoy` decimal(16,4) DEFAULT NULL COMMENT '每股收益同比',
  `capital_reserve` decimal(16,4) DEFAULT NULL COMMENT '每股资本公积金',
  `capital_reserve_yoy` decimal(16,4) DEFAULT NULL COMMENT '每股资本公积金同比',
  `undistri_profit_ps` decimal(16,4) DEFAULT NULL COMMENT '每股未分配利润',
  `undistri_profit_ps_yoy` decimal(16,4) DEFAULT NULL COMMENT '每股未分配利润同比',

	-- 盈利能力
  `ore_dlt` decimal(16,4) DEFAULT NULL COMMENT '净资产收益率-摊薄',
  `ore_dlt_yoy` decimal(16,4) DEFAULT NULL COMMENT '净资产收益率-摊薄同比',
  `net_interest_of_total_assets` decimal(16,4) DEFAULT NULL COMMENT '总资产报酬率',
  `net_interest_of_total_assets_yoy` decimal(16,4) DEFAULT NULL COMMENT '总资产报酬率同比',
  `rop` decimal(16,4) DEFAULT NULL COMMENT '人力投入回报率',
  `rop_yoy` decimal(16,4) DEFAULT NULL COMMENT '人力投入回报率同比',

	-- 偿债能力，财务风险
  `asset_liab_ratio` decimal(16,4) DEFAULT NULL COMMENT '资产负债率',
  `asset_liab_ratio_yoy` decimal(16,4) DEFAULT NULL COMMENT '资产负债率同比',
  `equity_multiplier` decimal(16,4) NOT NULL COMMENT '权益乘数',
  `equity_multiplier_yoy` decimal(16,4) NOT NULL COMMENT '权益乘数同比',
  `current_ratio` decimal(16,4) DEFAULT NULL COMMENT '流动比率',
  `current_ratio_yoy` decimal(16,4) DEFAULT NULL COMMENT '流动比率同比',
  `quick_ratio` decimal(16,4) NOT NULL COMMENT '速动比率',
  `quick_ratio_yoy` decimal(16,4) NOT NULL COMMENT '速动比率同比',
  `equity_ratio` decimal(16,4) NOT NULL COMMENT '产权比率',
  `equity_ratio_yoy` decimal(16,4) NOT NULL COMMENT '产权比率同比',
  `holder_equity` decimal(16,4) NOT NULL COMMENT '股东权益比率',
  `holder_equity_yoy` decimal(16,4) NOT NULL COMMENT '股东权益比率同比',
  `ncf_from_oa_to_total_liab` decimal(16,4) DEFAULT NULL COMMENT '现金流量比率',
  `ncf_from_oa_to_total_liab_yoy` decimal(16,4) DEFAULT NULL COMMENT '现金流量比率同比',
	-- 运营能力
  `inventory_turnover_days` decimal(16,4) DEFAULT NULL COMMENT '存货周转天数',
  `inventory_turnover_days_yoy` decimal(16,4) DEFAULT NULL COMMENT '存货周转天数同比',
  `receivable_turnover_days` decimal(16,4) DEFAULT NULL COMMENT '应收账款周转天数',
  `receivable_turnover_days_yoy` decimal(16,4) DEFAULT NULL COMMENT '应收账款周转天数同比',
  `accounts_payable_turnover_days` decimal(16,4) DEFAULT NULL COMMENT '应付账款周转天数',
  `accounts_payable_turnover_days_yoy` decimal(16,4) DEFAULT NULL COMMENT '应付账款周转天数同比',
  `cash_cycle` decimal(16,4) DEFAULT NULL COMMENT '现金循环周期',
  `cash_cycle_yoy` decimal(16,4) DEFAULT NULL COMMENT '现金循环周期同比',
  `operating_cycle` decimal(16,4) DEFAULT NULL COMMENT '营业周期',
  `operating_cycle_yoy` decimal(16,4) DEFAULT NULL COMMENT '营业周期同比',
  `total_capital_turnover` decimal(16,4) DEFAULT NULL COMMENT '总资产周转率',
  `total_capital_turnover_yoy` decimal(16,4) DEFAULT NULL COMMENT '总资产周转率同比',
  `inventory_turnover` decimal(16,4) DEFAULT NULL COMMENT '存货周转率',
  `inventory_turnover_yoy` decimal(16,4) DEFAULT NULL COMMENT '存货周转率同比',
  `account_receivable_turnover` decimal(16,4) DEFAULT NULL COMMENT '应收账款周转率',
  `account_receivable_turnover_yoy` decimal(16,4) DEFAULT NULL COMMENT '应收账款周转率同比',
  `accounts_payable_turnover` decimal(16,4) DEFAULT NULL COMMENT '应付账款周转率',
  `accounts_payable_turnover_yoy` decimal(16,4) DEFAULT NULL COMMENT '应付账款周转率同比',
  `current_asset_turnover_rate` decimal(16,4) DEFAULT NULL COMMENT '流动资产周转率',
  `current_asset_turnover_rate_yoy` decimal(16,4) DEFAULT NULL COMMENT '流动资产周转率同比',
  `fixed_asset_turnover_ratio` decimal(16,4) DEFAULT NULL COMMENT '固定资产周转率',
  `fixed_asset_turnover_ratio_yoy` decimal(16,4) DEFAULT NULL COMMENT '固定资产周转率同比',

  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `code_report_date` (`code`,`report_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
