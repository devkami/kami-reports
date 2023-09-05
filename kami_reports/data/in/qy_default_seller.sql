USE db_uc_kami;
SELECT 
  cliente.cod_cliente,
  cliente.cod_colaborador
FROM cd_cliente AS cliente
WHERE cliente.cod_cliente IN (SELECT DISTINCTROW pedido.cod_cliente FROM vd_pedido AS pedido WHERE YEAR(pedido.dt_implant) >= 2021);