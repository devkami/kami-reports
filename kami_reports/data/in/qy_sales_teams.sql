SELECT DISTINCTROW
  grupo_colaborador.cod_colaborador AS 'cod_colaborador',
  colaborador.nome_colaborador AS 'nome_colaborador',
  grupo_venda.cod_grupo_venda AS 'cod_grupo_venda',
  grupo_venda.nome_grupo AS 'equipe',
  grupo_venda.cod_empresa AS 'cod_empresa'
FROM vd_grupo AS grupo_venda
LEFT JOIN vd_grupo_colaborador AS grupo_colaborador ON (grupo_colaborador.cod_grupo_venda = grupo_venda.cod_grupo_venda)
LEFT JOIN sg_colaborador AS colaborador ON (colaborador.cod_colaborador = grupo_colaborador.cod_colaborador);