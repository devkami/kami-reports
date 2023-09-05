SELECT
  IFNULL(CONVERT(cliente.cod_cliente, CHAR), '0') AS 'cod_cliente',
  IFNULL(CONVERT(cliente.cod_colaborador, CHAR), '0') AS 'cod_colaborador'
FROM cd_cliente AS cliente
WHERE cliente.cod_cliente IN (SELECT DISTINCTROW pedido.cod_cliente FROM vd_pedido AS pedido WHERE YEAR(pedido.dt_implant) >= 2021);