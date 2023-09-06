-- db_uc_kami.tb_invoice source
CREATE OR REPLACE
ALGORITHM = UNDEFINED VIEW `tb_invoice` AS
SELECT DISTINCT
    CAST(`empresa`.`cnpj` AS CHAR charset utf8mb4) AS `distributorDocument`,
    IFNULL(CAST(DATE_FORMAT(`nota_fiscal`.`dt_emissao`, '%d/%m/%Y') AS CHAR charset utf8mb4), 'null') AS `invoiceDate`,
    IFNULL(CAST(`empresa`.`cod_empresa` AS CHAR charset utf8mb4), '0') AS `salesChannelCode`,
    IFNULL(CAST(`nota_fiscal`.`cnpj` AS CHAR charset utf8mb4), '0') AS `document`,
    IFNULL(CAST(`nota_fiscal`.`nome_cliente` AS CHAR charset utf8mb4), '0') AS `fullname`,
    'TRUSS' AS `businessSegment`,
    IFNULL(CAST(`nota_fiscal`.`sigla_uf` AS CHAR charset utf8mb4), '0') AS `state`,
    IFNULL(CAST(`nota_fiscal`.`cidade` AS CHAR charset utf8mb4), '0') AS `city`,
    IFNULL(CAST(`nota_fiscal`.`bairro` AS CHAR charset utf8mb4), '0') AS `district`,
    IFNULL(CAST(`nota_fiscal`.`cep` AS CHAR charset utf8mb4), '0') AS `zipcode`,
    IFNULL(CAST(`nota_fiscal`.`cnpj` AS CHAR charset utf8mb4), '0') AS `headquartersDocument`,
    IFNULL(CAST(`nota_fiscal`.`nome_cliente` AS CHAR charset utf8mb4), '0') AS `headquartersName`,
    IFNULL(CAST(REPLACE(`nota_fiscal`.`cfop`, '.', '') AS CHAR charset utf8mb4), '0') AS `cfopCode`,
    IFNULL(CAST(`nota_fiscal`.`desc_abrev_cfop` AS CHAR charset utf8mb4), '0') AS `cfopDescription`,
    IFNULL(CAST(`nota_fiscal`.`nr_nota_fiscal` AS CHAR charset utf8mb4), '0') AS `invoiceId`,
    IFNULL(CAST(`nota_fiscal`.`serie` AS CHAR charset utf8mb4), '0') AS `invoiceSeries`,
    '0' AS `sefazAccessKey`,
    IFNULL(CAST(`nota_fiscal`.`cod_colaborador` AS CHAR charset utf8mb4), '0') AS `salespersonCode`,
    '0' AS `salespersonCommissionRate`,
    IFNULL(CAST(`nota_fiscal`.`desc_cond_pagto` AS CHAR charset utf8mb4), '0') AS `paymentConditionCode`,
    IFNULL(CAST(`cond_pagto`.`qtd_parcelas` AS CHAR charset utf8mb4), '0') AS `totalPaymentInstallments`,
    IFNULL(CAST(`nota_fiscal_item`.`cod_produto` AS CHAR charset utf8mb4), '0') AS `distributorSku`,
    IFNULL(CAST(`nota_fiscal_item`.`desc_nota_fiscal` AS CHAR charset utf8mb4), '0') AS `distributorSkuDescription`,
    IFNULL(COALESCE(CAST(`produto`.`cod_ean` AS CHAR charset utf8mb4)), '0') AS `manufacturerSku`,
    (CASE
        WHEN (`nota_fiscal_item`.`cod_empresa` IN (1, 3)) THEN 'TbPdKAMISP'
        WHEN (`nota_fiscal_item`.`cod_empresa` = 2) THEN 'TbPdKAMIRS'
        WHEN (`nota_fiscal_item`.`cod_empresa` = 6) THEN 'TbPdKAMIRJ'
        WHEN (`nota_fiscal_item`.`cod_empresa` = 13) THEN 'TbPd3MKOES'
    END) AS `priceCode`,
    IFNULL(REPLACE(ROUND(`nota_fiscal_item`.`preco_unit`, 2), '.', ','), '0') AS `price`,
    IFNULL(CAST(ROUND(`nota_fiscal_item`.`qtd`, 0) AS CHAR charset utf8mb4), '0') AS `quantity`,
    IFNULL(CAST(REPLACE(ROUND(`nota_fiscal_item`.`preco_total`, 2), '.', ',') AS CHAR charset utf8mb4), '0') AS `invoiceTotal`,
    IFNULL(CAST(REPLACE(ROUND(`nota_fiscal`.`vl_ICMS_substituicao`, 2), '.', ',') AS CHAR charset utf8mb4), '0') AS `icmsSubstitutionTaxTotal`,
    '0' AS `fcpWithholdingSubstitutionTaxTotal`,
    '0' AS `fcpTaxTotal`,
    IFNULL(CAST(REPLACE(ROUND(`nota_fiscal_item`.`vl_icms`, 2), '.', ',') AS CHAR charset utf8mb4), '0') AS `icmsTaxTotal`,
    '0' AS `icmsExemptTaxTotal`,
    IFNULL(CAST(REPLACE(ROUND(`nota_fiscal_item`.`vl_ipi`, 2), '.', ',') AS CHAR charset utf8mb4), '0') AS `ipiTaxTotal`,
    IFNULL(CAST(REPLACE(ROUND(`nota_fiscal_item`.`vl_pis`, 2), '.', ',') AS CHAR charset utf8mb4), '0') AS `pisTaxTotal`,
    IFNULL(CAST(REPLACE(ROUND(`nota_fiscal_item`.`vl_cofins`, 2), '.', ',') AS CHAR charset utf8mb4), '0') AS `cofinsTaxTotal`,
    IFNULL(CAST(REPLACE(ROUND(`nota_fiscal`.`vl_despesas`, 2), '.', ',') AS CHAR charset utf8mb4), '0') AS `otherExpensesTotal`,
    IFNULL(CAST(REPLACE(ROUND(((`nota_fiscal_item`.`preco_total` / `nota_fiscal`.`vl_total_produtos`) * `nota_fiscal`.`vl_frete`), 2), '.', ',') AS CHAR charset utf8mb4), '0') AS `freightTotal`,
    IFNULL(CAST(REPLACE(ROUND(((`nota_fiscal_item`.`preco_total` * `nota_fiscal`.`vl_desconto`) / `nota_fiscal`.`vl_total_produtos`), 2), '.', ',') AS CHAR charset utf8mb4), '0') AS `discountTotal`,
    CONCAT(CONVERT(DATE_FORMAT(`nota_fiscal`.`dt_emissao`, '%d%m%Y') using latin1), CONCAT(`nota_fiscal`.`cod_nota_fiscal`, `nota_fiscal_item`.`cod_produto`), `nota_fiscal_item`.`nr_sequencia_nf`) AS `identifier`,
    (CASE
        WHEN (`nota_fiscal`.`situacao` <> 200) THEN NULL
        ELSE CAST(DATE_FORMAT(`nota_fiscal`.`dt_retorno`, '%d/%m/%Y') AS CHAR charset utf8mb4)
    END) AS `invoiceCancelledOn`,
    (CASE
        WHEN (`nota_fiscal`.`situacao` = 200) THEN 'Cancelled'
        ELSE 'Active'
    END) AS `invoiceStatus`
FROM (((((((((`vd_nota_fiscal` `nota_fiscal`
JOIN `vd_nota_fiscal_item` `nota_fiscal_item` 
    ON (((`nota_fiscal`.`cod_empresa` = `nota_fiscal_item`.`cod_empresa`)
    AND (`nota_fiscal`.`cod_nota_fiscal` = `nota_fiscal_item`.`cod_nota_fiscal`))))
JOIN `cd_produto` `produto`
    ON ((`nota_fiscal_item`.`cod_produto` = `produto`.`cod_produto`)))
JOIN `cd_cliente_endereco` `cliente_endereco`
    ON ((`nota_fiscal`.`cod_cliente` = `cliente_endereco`.`cod_cliente`)))
JOIN `vd_nota_fiscal_atividade` `nota_fiscal_atividade`
    ON (((`nota_fiscal`.`cod_nota_fiscal` = `nota_fiscal_atividade`.`cod_nota_fiscal`)
    AND (`nota_fiscal_item`.`cod_nota_fiscal` = `nota_fiscal_atividade`.`cod_nota_fiscal`))))
JOIN `cd_ramo_atividade` `ramo_atividade` 
    ON ((`nota_fiscal_atividade`.`cod_ramo_atividade` = `ramo_atividade`.`cod_ramo_atividade`)))
JOIN `cd_cliente_atividade` `cliente_atividade` 
    ON (((`nota_fiscal`.`cod_cliente` = `cliente_atividade`.`cod_cliente`)
    AND (`nota_fiscal_atividade`.`cod_ramo_atividade` = `cliente_atividade`.`cod_ramo_atividade`)
    AND (`ramo_atividade`.`cod_ramo_atividade` = `cliente_atividade`.`cod_ramo_atividade`))))
JOIN `cd_empresa` `empresa`
    ON (((`nota_fiscal`.`cod_empresa` = `empresa`.`cod_empresa`)
    AND (`nota_fiscal_item`.`cod_empresa` = `empresa`.`cod_empresa`))))
JOIN `sg_colaborador` `vendedor`
    ON ((`nota_fiscal`.`cod_colaborador` = `vendedor`.`cod_colaborador`)))
JOIN `cd_cond_pagto` `cond_pagto`
    ON ((`nota_fiscal`.`cod_cond_pagto` = `cond_pagto`.`cod_cond_pagto`)))
WHERE (`nota_fiscal`.`cod_empresa` IN (1, 2, 3, 6, 13))
ORDER BY `nota_fiscal`.`dt_emissao`;