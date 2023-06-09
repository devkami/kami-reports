USE db_uc_kami;
CREATE OR REPLACE VIEW vw_customer_details AS SELECT DISTINC
 IFNULL(CONVERT(cliente.cod_cliente, CHAR), '0') AS cod_cliente
,IFNULL(CONVERT(cliente.nome_cliente, CHAR), '0') AS nome_cliente
,IFNULL(CONVERT(cliente.razao_social, CHAR), '0') AS razao_social
,IFNULL(CONVERT(ramo_atividade.desc_abrev, CHAR), '0') AS ramo_atividade
,IFNULL(CONVERT(cliente_endereco.bairro, CHAR), '0') AS bairro
,IFNULL(CONVERT(cliente_endereco.cidade, CHAR), '0') AS cidade
,IFNULL(CONVERT(cliente_endereco.sigla_uf, CHAR), '0') AS uf
,IFNULL(CONVERT(cliente_endereco.endereco, CHAR), '0') AS endereco
,IFNULL(CONVERT(cliente_endereco.numero, CHAR), '0') AS numero
,IFNULL(CONVERT(cliente_endereco.cep, CHAR), '0') AS cep
,IFNULL(CONVERT(DATE_FORMAT(cliente.dt_implant,'%d/%m/%Y'), CHAR), '0') AS data_cadastro
,IFNULL(CONVERT(ROUND((SELECT CASE WHEN (SUM(recebe.vl_total_titulo) - SUM(recebe.vl_total_baixa)) > 0 THEN (TIMESTAMPDIFF(DAY,recebe.dt_vencimento, CURRENT_DATE())) ELSE  "0" END FROM fn_titulo_receber AS recebe WHERE recebe.cod_cliente = cliente.cod_cliente AND recebe.situacao < 30 AND recebe.dt_vencimento < SUBDATE(CURDATE(), INTERVAL 1 DAY) AND recebe.cod_empresa IN (1,2,3,4,5,6,9,10,11) group by recebe.cod_cliente),0), CHAR), '0') AS dias_atraso
,IFNULL(CONVERT(ROUND((SELECT CASE WHEN (SUM(recebe.vl_total_titulo) - SUM(recebe.vl_total_baixa)) > 0 THEN  (SUM(recebe.vl_total_titulo) - SUM(recebe.vl_total_baixa)) ELSE  "0" END FROM fn_titulo_receber AS recebe WHERE recebe.cod_cliente = cliente.cod_cliente AND recebe.situacao < 30 AND recebe.dt_vencimento < SUBDATE(CURDATE(), INTERVAL 1 DAY)  AND recebe.cod_empresa IN (1,2,3,4,5,6,9,10,11) group by recebe.cod_cliente),2), CHAR), '0') AS valor_devido
,IFNULL(CONVERT((SELECT DATE_FORMAT(MIN(nf2.dt_emissao),'%d/%m/%Y') FROM vd_nota_fiscal AS nf2 WHERE cliente.cod_cliente = nf2.cod_cliente AND nf2.situacao < 81 AND nf2.cod_empresa IN (1,2,3,4,5,6,9,10,11) AND nf2.nop IN ("6.102","6.404","BLACKFRIDAY","VENDA","VENDA_S_ESTOQUE","WORKSHOP")), CHAR), '0') AS dt_primeira_compra
,IFNULL(CONVERT((SELECT DATE_FORMAT(MAX(nf2.dt_emissao),'%d/%m/%Y') FROM vd_nota_fiscal AS nf2 WHERE cliente.cod_cliente = nf2.cod_cliente AND nf2.situacao < 81 AND nf2.cod_empresa IN (1,2,3,4,5,6,9,10,11) AND nf2.nop IN ("6.102","6.404","BLACKFRIDAY","VENDA","VENDA_S_ESTOQUE","WORKSHOP")), CHAR), '0') AS dt_ultima_compra
,IFNULL(CONVERT((SELECT MAX(YEAR(nf2.dt_emissao)) FROM vd_nota_fiscal AS nf2 WHERE cliente.cod_cliente = nf2.cod_cliente AND nf2.situacao < 81 AND nf2.cod_empresa IN (1,2,3,4,5,6,9,10,11) AND nf2.nop IN ("6.102","6.404","BLACKFRIDAY","VENDA","VENDA_S_ESTOQUE","WORKSHOP")), CHAR), '0') AS ultimo_ano_ativo
FROM cd_cliente AS cliente
LEFT JOIN cd_cliente_endereco AS cliente_endereco ON (cliente_endereco.cod_cliente = cliente.cod_cliente)
LEFT JOIN cd_cliente_atividade AS cliente_atividade  ON (cliente_atividade.cod_cliente = cliente.cod_cliente)
LEFT JOIN cd_ramo_atividade AS ramo_atividade  ON (cliente_atividade.cod_ramo_atividade = ramo_atividade.cod_ramo_atividade)
LEFT JOIN vd_pedido AS pedido ON (pedido.cod_cliente = cliente.cod_cliente)
WHERE pedido.cod_empresa IN (1,2,3,4,5,6,9,10,11);