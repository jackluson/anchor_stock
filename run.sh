#!/bin/sh
docker run -d -v /Users/admin/personal/anchor_plan/anchor_stock/.env:/anchor_stock/.env -v /Users/admin/personal/anchor_plan/anchor_stock/archives:/anchor_stock/archives -v /Users/admin/personal/anchor_plan/anchor_stock/log:/anchor_stock/log --name anchor_stock anchor_stock
