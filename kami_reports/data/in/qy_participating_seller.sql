USE db_uc_kami;
SELECT 
  cliente_participante.cod_cliente,
  cliente_participante.cod_colaborador 
FROM cd_cliente_participante AS cliente_participante
WHERE cliente_participante.cod_cliente IN (SELECT DISTINCTROW pedido.cod_cliente FROM vd_pedido AS pedido WHERE YEAR(pedido.dt_implant) >= 2021);