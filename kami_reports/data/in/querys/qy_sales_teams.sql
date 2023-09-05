SELECT DISTINCTROW
  IFNULL(CONVERT(grupo_colaborador.cod_colaborador, CHAR), '0') AS 'cod_colaborador',
  IFNULL(CONVERT(colaborador.nome_colaborador, CHAR), '0') AS 'nome_colaborador',
  IFNULL(CONVERT(grupo_venda.cod_grupo_venda, CHAR), '0') AS 'cod_grupo_venda',
  IFNULL(CONVERT(grupo_venda.nome_grupo, CHAR), '0') AS 'equipe',
  IFNULL(CONVERT(grupo_venda.cod_empresa, CHAR), '0') AS 'cod_empresa'
FROM vd_grupo AS grupo_venda
LEFT JOIN vd_grupo_colaborador AS grupo_colaborador ON (grupo_colaborador.cod_grupo_venda = grupo_venda.cod_grupo_venda)
LEFT JOIN sg_colaborador AS colaborador ON (colaborador.cod_colaborador = grupo_colaborador.cod_colaborador);