-- db_uc_kami.tb_inventory source
CREATE OR REPLACE
ALGORITHM = UNDEFINED VIEW `tb_inventory` AS
SELECT DISTINCT 
    IFNULL(CAST(DATE_FORMAT(`inventario`.`dt_inicio`, '%d/%m/%Y') AS CHAR charset utf8mb4), 'null') AS 'InventoryDate',
    IFNULL(CAST(`empresa`.`cnpj` AS CHAR charset utf8mb4), '0') AS 'distributorDocument',
    IFNULL(CAST(`empresa`.`cnpj` AS CHAR charset utf8mb4), '0') AS 'salesChannelCode',
    IFNULL(CAST(`inventario_item`.`cod_produto` AS CHAR charset utf8mb4), '0') AS 'distributorSku',
    IFNULL(coalesce(CAST(`produto`.`cod_ean` AS CHAR charset utf8mb4)), '0') AS 'manufacturerSku',
    IFNULL(CAST(round(`inventario_item`.`qtd_contada`, 0) AS CHAR charset utf8mb4), '0') AS 'quantity',
    IFNULL(CAST(replace(round(((`produto_empresa`.`vl_custo_total` * `inventario_item`.`qtd_contada`)), 2), '.', ',') AS CHAR charset utf8mb4), '0') AS 'stockAverageCost',
    IFNULL(CAST(DATE_FORMAT(`inventario_item`.`dt_contagem`, '%d/%m/%Y') AS CHAR charset utf8mb4), 'null') AS 'stockLastInDate',
    IFNULL(CAST(DATE_FORMAT((
        SELECT MAX(`nota_fiscal`.`dt_emissao`) FROM `vd_nota_fiscal` AS `nota_fiscal`
        JOIN `vd_nota_fiscal_item` AS `nota_fiscal_item` ON (`nota_fiscal_item`.`cod_nota_fiscal` = `nota_fiscal`.`cod_nota_fiscal`)
        WHERE `nota_fiscal_item`.`cod_produto`=`inventario_item`.`cod_produto`
        AND `nota_fiscal`.`situacao` < 86
        AND `nota_fiscal`.`situacao` > 79
        AND `nota_fiscal`.`cod_empresa` = `empresa`.`cod_empresa`), '%d/%m/%Y') AS CHAR charset utf8mb4), 'null') AS 'stockLastOutDate',
    IFNULL(CAST(`inventario_item`.`cod_lote` AS CHAR charset utf8mb4), '0') AS 'batch',
    IFNULL(CAST(DATE_FORMAT(`inventario_item`.`dt_validade`, '%d/%m/%Y') AS CHAR charset utf8mb4), 'null') AS 'productExpirationDate',
    CONCAT(
        CONVERT(DATE_FORMAT(`inventario`.`dt_inicio`, '%d%m%Y') USING latin1),
        CONCAT(`inventario`.`cod_inventario`, `inventario`.`cod_empresa`,`inventario_item`.`cod_produto`)) 
    AS 'identifier'    
FROM
    (((`eq_inventario` `inventario`
JOIN `eq_inventario_item` `inventario_item`
    ON (`inventario_item`.`cod_inventario` = `inventario`.`cod_inventario`))
JOIN `cd_produto` `produto`
    ON ((`produto`.`cod_produto` = `inventario_item`.`cod_produto`)))
JOIN `cd_empresa` `empresa`
    ON ((`empresa`.`cod_empresa` = `inventario`.`cod_empresa`))
JOIN `cd_produto_empresa` `produto_empresa` 
    ON (((`produto_empresa`.`cod_produto` = `produto`.`cod_produto`)
    and (`produto_empresa`.`cod_empresa` = `empresa`.`cod_empresa`))))
WHERE
    (`inventario`.`cod_empresa` in (1, 2, 3, 6, 13))
ORDER BY
    (`inventario`.`dt_inicio`);